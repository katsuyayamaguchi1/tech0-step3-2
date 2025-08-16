from backend.db_control import crud
from backend.db_control.mymodels import Customers   # ← ここを修正

def run():
    # 1) INSERT
    result = crud.myinsert(Customers, {
        "customer_id": "c001",
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
        "customer_id": "c001",
        "customer_name": "更新後太郎",
        "age": 26,
        "gender": "M"
    })
    print("UPDATE:", result)

    # 4) DELETE
    result = crud.mydelete(Customers, "c001")
    print("DELETE:", result)

if __name__ == "__main__":
    run()
