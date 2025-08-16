# backend/db_control/mymodels_MySQL.py
from sqlalchemy import String, Integer, ForeignKey, Date, DECIMAL, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    # 各テーブルで utf8mb4 / InnoDB を使用
    pass

class Customers(Base):
    __tablename__ = "customers"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)

    # 関連
    purchases: Mapped[list["Purchases"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan", passive_deletes=True
    )

class Items(Base):
    __tablename__ = "items"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    item_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # 金額は小数安全に
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)

    details: Mapped[list["PurchaseDetails"]] = relationship(
        back_populates="item", passive_deletes=True
    )

class Purchases(Base):
    __tablename__ = "purchases"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    purchase_id: Mapped[str] = mapped_column(String(10), primary_key=True)

    customer_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    purchase_date: Mapped[Date] = mapped_column(Date, nullable=False)

    customer: Mapped["Customers"] = relationship(back_populates="purchases")
    details: Mapped[list["PurchaseDetails"]] = relationship(
        back_populates="purchase", cascade="all, delete-orphan", passive_deletes=True
    )

class PurchaseDetails(Base):
    __tablename__ = "purchase_details"
    __table_args__ = (
        UniqueConstraint("purchase_id", "item_id", name="uq_purchase_item"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )

    detail_id: Mapped[str] = mapped_column(String(10), primary_key=True)

    purchase_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("purchases.purchase_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("items.item_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    purchase: Mapped["Purchases"] = relationship(back_populates="details")
    item: Mapped["Items"] = relationship(back_populates="details")
