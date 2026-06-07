# Polyglot Persistence Bridge — Orders & Reviews

> Đồ án #57 — Distributed Database Systems  
> **Mediation Layer** kết hợp dữ liệu từ CSV (PostgreSQL-style) và JSON (MongoDB-style)

## Người thực hiện

**Tên**: Lê Quốc Huy
**MSSV**: N23DCCN025
**Lớp** : D23CQCN01-N
**Môn học**: Cơ sở dữ liệu phân tán

## Mô tả đồ án

Hệ thống này xây dựng một **Mediation Layer** (lớp trung gian) thực hiện
**Distributed Join** giữa hai nguồn dữ liệu khác kiểu:

| Node    | Nguồn dữ liệu               | Kiểu cơ sở dữ liệu                     | Nội dung                     |
| ------- | --------------------------- | -------------------------------------- | ---------------------------- |
| Node A  | `data/orders.csv`           | Relational Database (PostgreSQL-style) | Lưu thông tin đơn hàng       |
| Node B  | `data/product_reviews.json` | Document Database (MongoDB-style)      | Lưu đánh giá sản phẩm        |
| Catalog | `data/products.json`        | JSON File                              | Lưu danh mục và tên sản phẩm |

### Mục tiêu chính

Phân tích và chứng minh **N+1 Query Problem** trong distributed systems:

- **Chiến lược N+1** (tệ): Gọi ReviewsDB `N+1` lần riêng lẻ
- **Chiến lược Batch** (tốt): Gọi ReviewsDB đúng 2 lần, join trong RAM

### Cài đặt & Chạy

### Yêu cầu

- Python 3.8+
- pip

### Bước 1: Clone repository

```bash
git clone https://github.com/LeQuocHuy025/polyglot-bridge.git
cd polyglot-bridge
```

### Bước 2: Cài thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Tạo dữ liệu

```bash
python src/generate_data.py
```

### Bước 4: Chạy benchmark

```bash
python src/benchmark.py
```

### Bước 5: Chạy failure simulation (demo video)

```bash
python src/failure_simulation.py
```

## Cấu trúc Project

```
polyglot-bridge/
├── data/                          # Dữ liệu
│   ├── orders.csv                 # Node A: 5.000 đơn hàng (CSV)
│   ├── product_reviews.json       # Node B: 50.000 reviews (JSON)
│   └── products.json              # Danh sách 50 sản phẩm
├── src/                           # Source code
│   ├── generate_data.py           # Script tạo dữ liệu giả lập
│   ├── mediation_layer.py         # Core: Lớp trung gian
│   ├── benchmark.py               # Đo hiệu năng 2 chiến lược
│   └── failure_simulation.py      # Demo failure cases
├── results/                       # Kết quả benchmark (tự sinh)
│   └── benchmark_results.json
├── requirements.txt
└── README.md
```

---

## Kết quả mẫu

strategy avg min ms max ms queries

---

n+1 (slow) 43.5 ms 42.8 44.4 1 + 10
batch (fast) 20.5 ms 19.7 21.8 2

batch is 2.1x faster — saves 23.0 ms per query

saved → results/benchmark_results.json

## Failure Cases được Demo

| Test         | Mô tả                    | Kết quả mong đợi                       |
| ------------ | ------------------------ | -------------------------------------- |
| Kill Node B  | Xóa file JSON            | FileNotFoundError — dừng an toàn       |
| Kill Node A  | Xóa file CSV             | FileNotFoundError — dừng an toàn       |
| Corrupt JSON | Ghi dữ liệu rác vào JSON | JSONDecodeError — phát hiện đúng       |
| Empty DB     | Node B có 0 records      | Graceful degradation — partial results |
