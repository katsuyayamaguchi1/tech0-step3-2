# backend/test_crud.py
from db_control import crud
from db_control.models import Customers
# ↑ パッケージ実行前提: `python -m backend.test_crud` で動かすと安全です

def run():
    # 何度も回す場合は以下のようにIDをずらすのもアリ:
    # import time; cid = f"c{int(time.time())}"
    cid = "c001"

    # 1) INSERT
    result = crud.myinsert(Customers, {
        "customer_id": cid,
        "customer_name": "テスト太郎",
        "age": 25,
        "gender": "M"
    })
    print("INSERT:", result)

    # 2) SELECT ALL
    result = crud.myselectAll(Customers)
    print("SELECT ALL:", result)

    # 3) UPDATE
    result = crud.myupdate(Customers, {
        "customer_id": cid,
        "customer_name": "更新後太郎",
        "age": 26,
        "gender": "M"
    })
    print("UPDATE:", result)

    # 4) DELETE
    result = crud.mydelete(Customers, cid)
    print("DELETE:", result)

if __name__ == "__main__":
    run()
