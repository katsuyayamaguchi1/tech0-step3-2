# backend/db_control/connect_MySQL.py
from pathlib import Path
import os, sys, traceback
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"
load_dotenv(ENV_PATH)

db_url = os.getenv("DATABASE_URL", "")
ssl_ca  = os.getenv("SSL_CA", "").strip()

# .env の相対パスはリポジトリルート基準に直す
if ssl_ca and not Path(ssl_ca).is_absolute():
    ssl_ca = str((REPO_ROOT / ssl_ca).resolve())

# SSL CA が無い/合わない場合は certifi に自動フォールバック
def resolve_cafile():
    # 1) .env 指定があり、かつ実在すればそれを使う
    if ssl_ca and Path(ssl_ca).is_file():
        return ssl_ca
    # 2) certifi バンドルを使う（DigiCert G2 収録済）
    try:
        import certifi
        return certifi.where()
    except Exception:
        return ""  # 何も渡さずにPyMySQLのデフォルトへ

cafile = resolve_cafile()

print("== Diagnostics ==")
print("env file        :", ENV_PATH)
print("DATABASE_URL set:", bool(db_url))
print("SSL_CA (.env)   :", os.getenv("SSL_CA", "(none)"))
print("SSL cafile used :", cafile if cafile else "(default)")
print("=================")

kwargs = {}
if cafile:
    kwargs["connect_args"] = {"ssl": {"ca": cafile}}

engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=1800, **kwargs)

def main():
    if not db_url:
        print("ERROR: DATABASE_URL が空です。.env を確認してください。")
        sys.exit(1)

    kwargs = {}
    if cafile:
        kwargs["connect_args"] = {"ssl": {"ca": cafile}}

    try:
        engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=1800, **kwargs)
        with engine.connect() as conn:
            val = conn.execute(text("SELECT 1")).scalar()
            print("SELECT 1 =", val)
    except Exception:
        print("\n!!! 接続エラー発生 !!!")
        traceback.print_exc()
        print("\nチェック項目:")
        print("- ユーザー名: tech0gen01student（ダメなら tech0gen01student@rdbs-002-gen10-step3-2-oshima2）")
        print("- パスワード: 受領の8桁英数字")
        print("- DB名: goodsun が存在するか（Unknown database ならAzureで作成）")
        print("- ファイアウォール: 現在のグローバルIPが許可されているか")

if __name__ == "__main__":
    main()
