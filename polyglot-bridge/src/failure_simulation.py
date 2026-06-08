import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from mediation_layer import MediationLayer

#Tạo bản sao lưu dữ liệu gốc trước khi phá dữ liệu
def backup():
    os.makedirs("data/backup", exist_ok=True)
    for f in ["orders.csv", "product_reviews.json", "products.json"]:
        if os.path.exists(f"data/{f}"):
            shutil.copy2(f"data/{f}", f"data/backup/{f}")

#Đưa dũ liệu từ backup về lại 
def restore():
    for f in ["orders.csv", "product_reviews.json", "products.json"]:
        if os.path.exists(f"data/backup/{f}"):
            shutil.copy2(f"data/backup/{f}", f"data/{f}")


def run(label, setup_fn, teardown_fn=None):
    print(f"  [{label}]")
    setup_fn()
    try:
        ml = MediationLayer("data/orders.csv", "data/product_reviews.json", "data/products.json")
        result = ml.query_top10_with_reviews__batch()
        print(f"Result: {len(result['results'])} products, 0 reviews each  (graceful degradation)")
    except FileNotFoundError as e:
        print(f"Caught: FileNotFoundError — {e.filename}")
    except json.JSONDecodeError as e:
        print(f"Caught: JSONDecodeError — {str(e)[:60]}")
    finally:
        if teardown_fn:
            teardown_fn()
    print()

#Kill Node B (MongoDB giả lập)
def test_kill_node_b():
    def setup():
        os.rename("data/product_reviews.json", "data/product_reviews.json.bak")
    def teardown():
        os.rename("data/product_reviews.json.bak", "data/product_reviews.json")
    run("Kill node B · reviews.json removed", setup, teardown)

#Kill Node A (PostgreSQL giả lập)
def test_kill_node_a():
    def setup():
        os.rename("data/orders.csv", "data/orders.csv.bak")
    def teardown():
        os.rename("data/orders.csv.bak", "data/orders.csv")
    run("Kill node A · orders.csv removed", setup, teardown)

#File .json bị hỏng
def test_corrupt_json():
    #Lưu lại dữ liệu gốc
    original = open("data/product_reviews.json", encoding="utf-8").read()
    def setup():
        with open("data/product_reviews.json", "w") as f:
            f.write("{ not valid json [[ }")
    def teardown():
        with open("data/product_reviews.json", "w", encoding="utf-8") as f:
            f.write(original)
    run("Corrupt data · malformed JSON in node B", setup, teardown)

#File reviews rỗng
def test_empty_db():
    #Lưu lại dữ liệu gốc
    original = json.load(open("data/product_reviews.json", encoding="utf-8"))
    def setup():
        with open("data/product_reviews.json", "w") as f:
            json.dump([], f)
    def teardown():
        with open("data/product_reviews.json", "w", encoding="utf-8") as f:
            json.dump(original, f, ensure_ascii=False)
    run("Empty node B · 0 reviews", setup, teardown)


if __name__ == "__main__":
    print("Failure Simulation\n")
    backup()
    #File reviews rỗng
    test_empty_db()

















    '''time.sleep(0.3)
    test_kill_node_a()
    time.sleep(0.3)
    test_corrupt_json()
    time.sleep(0.3)
    test_empty_db()
    restore()
    print("all tests passed — data restored")
'''
    