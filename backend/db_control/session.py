# backend/db_control/session.py
import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _db_url() -> str:
    user = urllib.parse.quote_plus(os.getenv("DB_USER", ""))
    pwd  = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "goodsun")
    # 文字化け防止
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}?charset=utf8mb4"

# 環境変数からSSL CAを読む（例: backend/certs/DigiCertGlobalRootG2.crt.pem）
ssl_ca = os.getenv("SSL_CA")
connect_args = {}
if ssl_ca and os.path.exists(ssl_ca):
    connect_args["ssl"] = {"ca": ssl_ca}
else:
    # Azure MySQLはTLS必須。CA未指定でもTLS自体は張られますが、
    # 証明書検証のためにCA指定を推奨します。
    connect_args["ssl"] = {}

engine = create_engine(
    _db_url(),
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=5,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
