from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from db_control.connect_MySQL import engine
from db_control.mymodels_MySQL import Base, Customers

# セッションファクトリ（共通で使い回し）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """存在しないテーブルのみ作成（冪等）"""
    print("Creating tables if not exist ...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


def insert_sample_data() -> None:
    """customers の初期データ（冪等：既にあればスキップ）"""
    seed = [
        Customers(customer_id="C1111", customer_name="ああさん", age=6, gender="男"),
        Customers(customer_id="C110",  customer_name="桃太郎さん", age=30, gender="女"),
    ]

    with SessionLocal() as session:
        try:
            # 既存チェック（PK重複を避ける）
            for c in seed:
                if session.get(Customers, c.customer_id) is None:
                    session.add(c)
            session.commit()
            print("Sample data inserted or already present.")
        except IntegrityError:
            session.rollback()
            print("Some sample rows already existed. Skipped duplicates.")
        except Exception as e:
            session.rollback()
            raise e


if __name__ == "__main__":
    init_db()
    insert_sample_data()
