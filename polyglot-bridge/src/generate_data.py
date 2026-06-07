"""
  FILE: generate_data.py
  MỤC ĐÍCH: Tạo dữ liệu giả cho 2 nguồn:
    1. orders.csv      → mô phỏng PostgreSQL (dữ liệu quan hệ)
    2. product_reviews.json → mô phỏng MongoDB (dữ liệu JSON)
"""

import csv
import json
import random
import os
from datetime import datetime, timedelta

# CẤU HÌNH — thay đổi nếu muốn nhiều/ít dữ liệu hơn
NUM_PRODUCTS  = 50       # số lượng sản phẩm
NUM_ORDERS    = 5000     # số lượng đơn hàng
NUM_REVIEWS   = 50000    # số lượng reviews — nhiều để benchmark rõ hơn
NUM_CUSTOMERS = 500      # số lượng khách hàng

# Tên sản phẩm mẫu
PRODUCT_NAMES = [
    "Laptop Gaming", "Tai nghe Bluetooth", "Bàn phím cơ", "Chuột không dây",
    "Màn hình 4K", "Điện thoại Samsung", "iPhone 15", "iPad Pro",
    "Loa JBL", "Webcam HD", "Ổ cứng SSD", "RAM 16GB",
    "Card màn hình RTX", "CPU Intel i9", "Mainboard ASUS",
    "Balo laptop", "Cáp sạc USB-C", "Hub USB", "Đèn LED bàn làm việc",
    "Giá đỡ laptop", "Ghế gaming", "Bàn gaming", "Tay cầm Xbox",
    "Máy in laser", "Scanner tài liệu", "Máy chiếu mini",
    "Loa Bluetooth mini", "Đồng hồ thông minh", "Vòng đeo tay thể thao",
    "Tai nghe có dây", "Microphone podcast", "Capture card", "Router WiFi 6",
    "Modem ADSL", "Switch mạng", "Cáp HDMI 4K", "Bộ chuyển đổi VGA",
    "Pin dự phòng 20000mAh", "Sạc không dây", "Ốp lưng điện thoại",
    "Dán màn hình", "Túi chống sốc laptop", "Bộ vệ sinh máy tính",
    "Keo tản nhiệt", "Quạt tản nhiệt CPU", "Case máy tính ATX",
    "Nguồn máy tính 750W", "UPS lưu điện", "Màn hình phụ 24 inch",
    "Bàn phím không dây"
]

# Trạng thái đơn hàng
ORDER_STATUSES = ["completed", "pending", "shipped", "cancelled", "returned"]

#Sinh ngày ngẫu nhiên
def random_date(start_year=2023, end_year=2024):
    """Tạo ngày ngẫu nhiên trong khoảng thời gian cho trước."""
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")

#Tạo file orders.csv
def generate_orders(output_path):
    """Tạo file orders.csv"""
    print("Đang tạo orders.csv ...")

    fieldnames = ["order_id", "product_id", "customer_id",
                  "amount", "status", "order_date"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for order_id in range(1, NUM_ORDERS + 1):
            writer.writerow({
                "order_id":    order_id,
                "product_id":  random.randint(1, NUM_PRODUCTS),
                "customer_id": random.randint(1, NUM_CUSTOMERS),
                "amount":      round(random.uniform(50_000, 50_000_000), 0),  # VNĐ
                "status":      random.choice(ORDER_STATUSES),
                "order_date":  random_date()
            })

    print(f"Tạo xong orders.csv — {NUM_ORDERS} đơn hàng")

#Tạo file product_reviews.json
def generate_reviews(output_path):
    
    print("Đang tạo product_reviews.json ...")

    review_texts_positive = [
        "Sản phẩm rất tốt, đúng như mô tả!",
        "Chất lượng tuyệt vời, sẽ mua lại.",
        "Giao hàng nhanh, đóng gói cẩn thận.",
        "Dùng được 1 tuần rồi, vẫn hoạt động tốt.",
        "Giá cả hợp lý, chất lượng xứng đáng.",
        "Shop tư vấn nhiệt tình, sản phẩm ổn.",
        "Hàng chính hãng, tem nhãn đầy đủ.",
        "Mua lần 2 rồi, vẫn hài lòng như lần đầu.",
    ]
    review_texts_negative = [
        "Sản phẩm không như mong đợi.",
        "Giao hàng chậm, hơi thất vọng.",
        "Chất lượng tạm được, không xuất sắc lắm.",
        "Có lỗi nhỏ nhưng shop hỗ trợ xử lý ổn.",
        "Màu sắc khác hình một chút.",
    ]

    reviews = []
    for review_id in range(1, NUM_REVIEWS + 1):
        rating = random.randint(1, 5)
        # Rating cao → text tích cực, thấp → tiêu cực
        if rating >= 4:
            text = random.choice(review_texts_positive)
        else:
            text = random.choice(review_texts_negative)

        reviews.append({
            "review_id":  review_id,
            "product_id": random.randint(1, NUM_PRODUCTS),
            "customer_id": random.randint(1, NUM_CUSTOMERS),
            "rating":     rating,
            "review_text": text,
            "review_date": random_date()
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

    print(f"Tạo xong product_reviews.json — {NUM_REVIEWS} reviews")

#Tạo file products.json — danh sách tên sản phẩm
def generate_products_catalog(output_path):

    print("Đang tạo products.json ...")

    products = []
    for pid in range(1, NUM_PRODUCTS + 1):
        products.append({
            "product_id":   pid,
            "product_name": PRODUCT_NAMES[pid - 1] if pid <= len(PRODUCT_NAMES)
                            else f"Sản phẩm #{pid}",
            "category":     random.choice(["Laptop", "Điện thoại", "Phụ kiện",
                                           "Màn hình", "Âm thanh", "Mạng"]),
            "price":        round(random.uniform(100_000, 30_000_000), 0)
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"Tạo xong products.json — {NUM_PRODUCTS} sản phẩm")


# CHẠY CHÍNH
if __name__ == "__main__":
    # Đảm bảo thư mục data/ tồn tại
    os.makedirs("data", exist_ok=True)

    generate_orders("data/orders.csv")
    generate_reviews("data/product_reviews.json")
    generate_products_catalog("data/products.json")

    print("\nHoàn tất! Kiểm tra thư mục data/")
    print("data/orders.csv")
    print("data/product_reviews.json")
    print("data/products.json")
