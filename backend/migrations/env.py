# backend/migrations/env.py

import os
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# backend/.env を明示して読み込む（migrations の1つ上 = backend）
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Alembic Config
config = context.config

# .env の DATABASE_URL を採用（SSL 付き URL）
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError(f"DATABASE_URL is not set. Looked at {ENV_PATH}")
config.set_main_option("sqlalchemy.url", db_url)

# ロギング
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# モデルの metadata を渡す（自動検出用）
from db_control.models import Base
target_metadata = Base.metadata

# DB にだけ存在（metadata に無い）オブジェクトは無視＝不要な DROP を出さない
def include_object(object, name, type_, reflected, compare_to):
    if reflected and compare_to is None:
        return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=False,             # ← 型差分も無視して静かに
        compare_server_default=False,   # ← サーバーデフォルト差分も無視
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=False,             # ← 同上
            compare_server_default=False,   # ← 同上
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
