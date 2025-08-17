# backend/db_control/crud.py
from typing import Any, Dict
from sqlalchemy import insert, delete, update, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from sqlalchemy.exc import IntegrityError
import json
import os

# ✅ 接続は db_control.session に一本化
#   - engine を個別に作らず、同じ SessionLocal を共有
from .session import SessionLocal  # type: ignore

def _row_to_dict(obj) -> dict:
    """SQLAlchemy モデル → {col: value} に汎用変換"""
    mapper = sqlalchemy_inspect(obj).mapper
    return {col.key: getattr(obj, col.key) for col in mapper.column_attrs}

def myselect(mymodel, pk_value: Any) -> str:
    """PK で1件取得 → JSON（単一PK想定）"""
    with SessionLocal() as session:
        pk_col = sqlalchemy_inspect(mymodel).primary_key[0]
        rows = session.execute(
            select(mymodel).where(pk_col == pk_value)
        ).scalars().all()
        return json.dumps([_row_to_dict(r) for r in rows], ensure_ascii=False, default=str)

def myselectAll(mymodel) -> str:
    """全件取得 → JSON"""
    with SessionLocal() as session:
        rows = session.execute(select(mymodel)).scalars().all()
        return json.dumps([_row_to_dict(r) for r in rows], ensure_ascii=False, default=str)

def myinsert(mymodel, values: Dict[str, Any]) -> str:
    """挿入 → 'inserted:<pk>' / 'unique_violation'"""
    with SessionLocal() as session:
        try:
            result = session.execute(insert(mymodel).values(values))
            session.commit()
            # PK返却（AUTO_INCREMENT 等に対応）
            pks = result.inserted_primary_key
            return f"inserted:{pks[0]}" if pks else "inserted"
        except IntegrityError:
            session.rollback()
            return "unique_violation"
        except Exception:
            session.rollback()
            raise

def myupdate(mymodel, values: Dict[str, Any]) -> str:
    """更新 → 'updated' / 'not_found' / 'unique_violation' / 'missing_<pk>' / 'no_changes'"""
    pk_name = sqlalchemy_inspect(mymodel).primary_key[0].key
    pk_value = values.get(pk_name)
    if pk_value is None:
        return f"missing_{pk_name}"

    update_values = {k: v for k, v in values.items() if k != pk_name}
    if not update_values:
        return "no_changes"

    with SessionLocal() as session:
        try:
            pk_col = sqlalchemy_inspect(mymodel).primary_key[0]
            result = session.execute(
                update(mymodel).where(pk_col == pk_value).values(**update_values)
            )
            session.commit()
            return "updated" if result.rowcount else "not_found"
        except IntegrityError:
            session.rollback()
            return "unique_violation"
        except Exception:
            session.rollback()
            raise

def mydelete(mymodel, pk_value: Any) -> str:
    """削除 → '<pk> is deleted' / 'not_found' / 'unique_violation'"""
    with SessionLocal() as session:
        try:
            pk_col = sqlalchemy_inspect(mymodel).primary_key[0]
            result = session.execute(delete(mymodel).where(pk_col == pk_value))
            session.commit()
            return f"{pk_value} is deleted" if result.rowcount else "not_found"
        except IntegrityError:
            session.rollback()
            return "unique_violation"
        except Exception:
            session.rollback()
            raise


