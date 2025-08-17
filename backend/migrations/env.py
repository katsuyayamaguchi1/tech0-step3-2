# backend/migrations/env.py
from __future__ import annotations

from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool
from pathlib import Path
import sys
import os

# ---- どこから実行しても import できるように、プロジェクトルートを sys.path に追加
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---- .env 読み込み（backend/.env）
from dotenv import load_dotenv
load_dotenv(ROOT / "backend" / ".env")

# ---- アプリ側の Base と URL を再利用
from backend.db_control.models import Base
from backend.db_control.session import _db_url

# Alembic 標準設定
config = context.config

# ログ設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# メタデータ（autogenerate用）
target_metadata = Base.metadata


def _resolve_ca_path() -> str | None:
    """SSL_CA があればそれ、無ければ certifi、最後に mac の既定CA を試す"""
    p = os.getenv("SSL_CA")
    if p and os.path.exists(p):
        return p
    try:
        import certifi
        return certifi.where()
    except Exception:
        pass
    if os.path.exists("/etc/ssl/cert.pem"):
        return "/etc/ssl/cert.pem"
    return None


def get_url() -> str:
    return _db_url()  # mysql+pymysql://.../goodsun?charset=utf8mb4


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    ca = _resolve_ca_path()
    connect_args = {"ssl": {"ca": ca}} if ca else {"ssl": {}}

    # デバッグ用：どの CA を使ったかを INFO ログに出す
    print(f"[alembic] Using SSL CA: {ca}", flush=True)

    engine = create_engine(
        get_url(),
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
