# backend/db_control/models.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column, Integer, String, DateTime, MetaData, Numeric, text, Index
)

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
Base = declarative_base(metadata=MetaData(naming_convention=NAMING_CONVENTION))

class Sample(Base):
    __tablename__ = "sample"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class Customers(Base):
    __tablename__ = "customers"
    customer_id = Column(String(10), primary_key=True)
    customer_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)

Index("ix_customers_customer_name", Customers.customer_name)

class Items(Base):
    __tablename__ = "items"
    item_id = Column(String(10), primary_key=True)  # DBの主キーに合わせる
    item_name = Column(String(100), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    id = Column(Integer)  # DBにあるので残す（主キーではない）
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
