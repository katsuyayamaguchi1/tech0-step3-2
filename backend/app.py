from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from collections.abc import Generator

# --- 既存の customers 用（そのまま） ---
from db_control import crud, mymodels

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
from db_control.models import Sample  # id, name, created_at

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

# ===== 既存の customers 系（そのまま） =====
class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str

@app.post("/customers")
def create_customer(customer: Customer):
    values = customer.dict()
    _ = crud.myinsert(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, values.get("customer_id"))
    if result:
        result_obj = json.loads(result)
        return result_obj if result_obj else None
    return None

@app.get("/customers")
def read_one_customer(customer_id: str = Query(...)):
    result = crud.myselect(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None

@app.get("/allcustomers")
def read_all_customer():
    result = crud.myselectAll(mymodels.Customers)
    if not result:
        return []
    return json.loads(result)

@app.put("/customers")
def update_customer(customer: Customer):
    values = customer.dict()
    values_original = values.copy()
    _ = crud.myupdate(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, values_original.get("customer_id"))
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None

@app.delete("/customers")
def delete_customer(customer_id: str = Query(...)):
    result = crud.mydelete(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer_id": customer_id, "status": "deleted"}

@app.get("/fetchtest")
def fetchtest():
    response = requests.get("https://jsonplaceholder.typicode.com/users")
    return response.json()
