from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from collections.abc import Generator

from sqlalchemy.exc import IntegrityError

# --- ここから追加：DB接続（.env の DATABASE_URL を使用） ---
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Alembic/前段で設定済みの .env を読み込む
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check backend/.env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 動作確認用のモデル（Alembicで作成した sample テーブル）
from db_control.models import Sample, Customers

# --- sample 用のPydantic ---
from datetime import datetime

class SampleIn(BaseModel):
    name: str

class SampleOut(BaseModel):
    id: int
    name: str
    created_at: datetime

# -------------------------------------------------------------

app = FastAPI()

# CORSミドルウェアの設定（既存のまま）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"message": "FastAPI top page!"}

# ===== 追加: DB ヘルスチェック =====
@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"db": "ok"}

# ===== 追加: sample の最小CRUD（煙テスト用） =====
@app.post("/sample", response_model=SampleOut)
def create_sample(payload: SampleIn, db: Session = Depends(get_db)):
    obj = Sample(name=payload.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return SampleOut(id=obj.id, name=obj.name, created_at=obj.created_at)

@app.get("/sample", response_model=list[SampleOut])
def list_sample(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(Sample).order_by(Sample.id.desc()).limit(limit).all()
    return [SampleOut(id=r.id, name=r.name, created_at=r.created_at) for r in rows]

# ===== 既存の customers 系（ORM版に置き換え） =====
class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str

@app.post("/customers")
def create_customer(customer: Customer, db: Session = Depends(get_db)):
    obj = Customers(
        customer_id=customer.customer_id,
        customer_name=customer.customer_name,
        age=customer.age,
        gender=customer.gender,
    )
    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Customer already exists")
    return {
        "customer_id": obj.customer_id,
        "customer_name": obj.customer_name,
        "age": obj.age,
        "gender": obj.gender,
    }

@app.get("/customers")
def read_one_customer(customer_id: str = Query(...), db: Session = Depends(get_db)):
    obj = db.get(Customers, customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "customer_id": obj.customer_id,
        "customer_name": obj.customer_name,
        "age": obj.age,
        "gender": obj.gender,
    }

@app.get("/allcustomers")
def read_all_customer(db: Session = Depends(get_db)):
    rows = db.query(Customers).order_by(Customers.customer_id).all()
    return [
        {
            "customer_id": r.customer_id,
            "customer_name": r.customer_name,
            "age": r.age,
            "gender": r.gender,
        }
        for r in rows
    ]

@app.put("/customers")
def update_customer(customer: Customer, db: Session = Depends(get_db)):
    obj = db.get(Customers, customer.customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    obj.customer_name = customer.customer_name
    obj.age = customer.age
    obj.gender = customer.gender
    db.commit()
    db.refresh(obj)
    return {
        "customer_id": obj.customer_id,
        "customer_name": obj.customer_name,
        "age": obj.age,
        "gender": obj.gender,
    }

@app.delete("/customers")
def delete_customer(customer_id: str = Query(...), db: Session = Depends(get_db)):
    obj = db.get(Customers, customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(obj)
    db.commit()
    return {"customer_id": customer_id, "status": "deleted"}

from sqlalchemy import text  # 既にあれば不要

@app.get("/health/info")
def health_info():
    with engine.connect() as conn:
        ver = conn.execute(text("SELECT VERSION()")).scalar_one()
        dbn = conn.execute(text("SELECT DATABASE()")).scalar_one()
        usr = conn.execute(text("SELECT CURRENT_USER()")).scalar_one()
    return {"db":"ok","version":ver,"database":dbn,"user":usr}

