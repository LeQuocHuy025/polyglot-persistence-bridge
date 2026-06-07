import csv
import json
import time
from collections import defaultdict

#Mô phỏng PostgreSQL dưới dạng file .CSV
class OrdersDB:
    def __init__(self, csv_path: str): #Nhận đường dẫn đến .CSV
        self._path = csv_path #Lưu đường dẫn
        self._data = [] #Lưu dữ liệu của file sau khi load

    #Đọc file .CSV
    def load(self):
        with open(self._path, "r", encoding="utf-8") as f:
            self._data = list(csv.DictReader(f)) #Đọc .CSV thành list của các dict
        print(f"  orders.csv       {len(self._data):>6,} rows")

    #Lấy toàn bộ đơn hàng 
    def get_all_orders(self):
        return self._data
    #Tìm top 10 sp bán chạy
    def get_top_products_by_orders(self, top_n=10):
        counter = defaultdict(int)
        for row in self._data:
            counter[int(row["product_id"])] += 1 #Đếm số lần xuất hiện của từng sp
        #Lấy product_ID theo đơn hàng giảm dần
        return [pid for pid, _ in sorted(counter.items(), key=lambda x: x[1], reverse=True)[:top_n]]

#Mô phỏng MongoDB dưới dạng file .json
class ReviewsDB:
    def __init__(self, json_path: str): 
        self._path = json_path #Lưu đường dẫn JSON
        self._data = [] #Chứa reviews

    #Đọc file product_reviews.json
    def load(self):
        with open(self._path, "r", encoding="utf-8") as f:
            self._data = json.load(f) #Đọc file .json
        print(f"  product_reviews.json {len(self._data):>6,} rows")

    #Tìm review theo sản phẩm
    def find_reviews_by_product(self, product_id, limit=5, simulate_latency_ms=2.0):
        #Giả lập độ trễ 0.002s
        if simulate_latency_ms > 0:
            time.sleep(simulate_latency_ms / 1000.0)
        #Lọc tất cả review của sản phẩm
        results = [r for r in self._data if r["product_id"] == product_id]
        #Sắp xếp mới nhất trước
        results.sort(key=lambda r: r["review_date"], reverse=True)
        #Lấy tối đa 5 review
        return results[:limit]
    #Lấy hết tất cả review
    def get_all_reviews(self):
        return self._data

#Tầng trung gian giữa PostgreSQL và MongoDB
class MediationLayer:
    def __init__(self, orders_path, reviews_path, products_path):
        print("Polyglot Persistence Bridge")
        print(f"  connecting to data sources...")

        self.orders_db  = OrdersDB(orders_path) #Khởi tạo nguồn dữ liệu Orders
        self.reviews_db = ReviewsDB(reviews_path) #Khởi tạo nguồn dữ liệu Reviews
        
        #Mở products.json
        with open(products_path, "r", encoding="utf-8") as f:
            products_list = json.load(f) #Đọc danh sách sản phẩm
        #Chuyển list thành dict
        self._products_map = {p["product_id"]: p for p in products_list}

        self.orders_db.load() #load .CSV
        self.reviews_db.load()#load.json
        print(f"  ready.\n")

    #Lấy tên sản phẩm
    def get_product_name(self, product_id):
        p = self._products_map.get(product_id, {})
        return p.get("product_name", f"Product #{product_id}")

    def query_top10_with_reviews__n_plus_1(self, top_n=10, reviews_per_product=5):
        #Lấy top 10 sản phẩm
        top_products = self.orders_db.get_top_products_by_orders(top_n)
        results = []
        #Duyệt từng sản phẩm trong top_n
        for product_id in top_products:
            reviews = self.reviews_db.find_reviews_by_product(
                product_id, limit=reviews_per_product, simulate_latency_ms=2.0
            )
            results.append({
                "product_id":   product_id,
                "product_name": self.get_product_name(product_id),
                "order_count":  self._count_orders_for_product(product_id),
                "reviews":      reviews,
                "review_count": len(reviews),
            })
        return {"strategy": "n+1", "results": results}

    def query_top10_with_reviews__batch(self, top_n=10, reviews_per_product=5):
        #Số sản phẩm bán chạy
        top_products = self.orders_db.get_top_products_by_orders(top_n)
        #Lấy toàn bộ review
        all_reviews  = self.reviews_db.get_all_reviews()

        reviews_by_product = defaultdict(list)
        #Duyệt review của từng product
        for review in all_reviews:
            reviews_by_product[review["product_id"]].append(review)
        #Sắp xếp review theo ngày tháng mới nhất của từng product
        for pid in reviews_by_product:
            reviews_by_product[pid].sort(key=lambda r: r["review_date"], reverse=True)

        results = []
        #Duyệt từng sản phẩm bán chạy
        for product_id in top_products:
            #Lấy review sản phẩm, ko có thì trả về [], lấy tối đa 5 review
            reviews = reviews_by_product.get(product_id, [])[:reviews_per_product]
            results.append({
                "product_id":   product_id,
                "product_name": self.get_product_name(product_id),
                "order_count":  self._count_orders_for_product(product_id),
                "reviews":      reviews,
                "review_count": len(reviews),
            })
        return {"strategy": "batch", "results": results}
    
    #Đếm số đơn hàng của sản phẩm.
    def _count_orders_for_product(self, product_id):
        return sum(1 for row in self.orders_db.get_all_orders()
                   if int(row["product_id"]) == product_id)
