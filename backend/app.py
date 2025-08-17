# backend/app.py
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

# DB: セッションを一本化
# from db_control.session import get_db
# ORMモデル
# from db_control.models import Sample, Customers, Items

from .db_control.session import get_db
from .db_control.models import Sample, Customers, Items

app = FastAPI()

# CORS（Next.js から叩く場合は必要）
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

# ===== DB ヘルスチェック =====
@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    curdb = db.execute(text("SELECT DATABASE()")).scalar_one()
    return {"db": "ok", "database": curdb}

# ===== DB 情報可視化 =====
@app.get("/health/info")
def health_info(db: Session = Depends(get_db)):
    ver = db.execute(text("SELECT VERSION()")).scalar_one()
    dbn = db.execute(text("SELECT DATABASE()")).scalar_one()
    usr = db.execute(text("SELECT CURRENT_USER()")).scalar_one()
    return {"db": "ok", "version": ver, "database": dbn, "user": usr}

# ===== sample の最小CRUD（煙テスト用） =====
class SampleIn(BaseModel):
    name: str

class SampleOut(BaseModel):
    id: int
    name: str
    created_at: datetime

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

# ===== customers（ORM版） =====
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
    except Exception:
        db.rollback()
        # 一意制約違反などを409で返す（IntegrityErrorもここに入る）
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

# ===== Items API（DBの主キー item_id に合わせた版） =====
class ItemIn(BaseModel):
    item_name: str
    price: Decimal

@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    rows = db.query(Items).order_by(Items.created_at.desc()).all()
    return [
        {
            "item_id": r.item_id,
            "item_name": r.item_name,
            "price": str(r.price),  # Decimal を文字列化
            "id": r.id,             # 補助列（使わなければ無視）
            "created_at": r.created_at,
        }
        for r in rows
    ]

@app.post("/items")
def create_item(payload: ItemIn, db: Session = Depends(get_db)):
    # item_id は DBで自動採番されないのでアプリ側で発番（10文字）
    new_item_id = "I" + uuid4().hex[:9].upper()  # 例: I3F9A1B2C
    # id 列が AUTO_INCREMENT でない前提に対応（MAX+1）
    next_int_id = db.execute(text("SELECT COALESCE(MAX(id),0)+1 FROM items")).scalar_one()
    try:
        obj = Items(
            item_id=new_item_id,
            item_name=payload.item_name,
            price=payload.price,
            id=next_int_id,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {
            "item_id": obj.item_id,
            "item_name": obj.item_name,
            "price": str(obj.price),
            "id": obj.id,
            "created_at": obj.created_at,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"create_item failed: {e}")
