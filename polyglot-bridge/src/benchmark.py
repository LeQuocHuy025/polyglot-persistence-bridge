import time
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from mediation_layer import MediationLayer

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

NUM_RUNS     = 5
TOP_N        = 10
REVIEWS_EACH = 5


def measure(func, *args, **kwargs):
    start  = time.perf_counter()
    result = func(*args, **kwargs)
    return result, (time.perf_counter() - start) * 1000


def run_benchmark(ml):
    print("Benchmark — N+1 vs Batch  (5 runs each)\n")

    print("  strategy  n+1  ...")
    n1_times, n1_result = [], None
    for i in range(NUM_RUNS):
        result, ms = measure(ml.query_top10_with_reviews__n_plus_1,
                             top_n=TOP_N, reviews_per_product=REVIEWS_EACH)
        n1_times.append(ms)
        n1_result = result
        print(f"    run {i+1}   {ms:6.1f} ms")

    print()
    print("  strategy  batch  ...")
    batch_times, batch_result = [], None
    for i in range(NUM_RUNS):
        result, ms = measure(ml.query_top10_with_reviews__batch,
                             top_n=TOP_N, reviews_per_product=REVIEWS_EACH)
        batch_times.append(ms)
        batch_result = result
        print(f"    run {i+1}   {ms:6.1f} ms")

    return {
        "n1":    {"times": n1_times,    "avg": sum(n1_times)/NUM_RUNS,    "result": n1_result},
        "batch": {"times": batch_times, "avg": sum(batch_times)/NUM_RUNS, "result": batch_result},
    }


def print_summary(stats):
    n1, batch = stats["n1"], stats["batch"]
    speedup   = n1["avg"] / batch["avg"]

    print("\nResults\n")

    rows = [
        ["n+1   (slow)", f"{n1['avg']:.1f} ms",    f"{min(n1['times']):.1f}", f"{max(n1['times']):.1f}", f"1 + {TOP_N}"],
        ["batch (fast)", f"{batch['avg']:.1f} ms", f"{min(batch['times']):.1f}", f"{max(batch['times']):.1f}", "2"],
    ]
    print(tabulate(rows,
                   headers=["strategy", "avg", "min ms", "max ms", "queries"],
                   tablefmt="simple") if HAS_TABULATE else
          f"    n+1: {n1['avg']:.1f} ms    batch: {batch['avg']:.1f} ms")

    print(f"\n  batch is {speedup:.1f}x faster — saves {n1['avg']-batch['avg']:.1f} ms per query\n")
    return speedup


def print_top10(result):
    print("  Top 10 products · 5 latest reviews\n")
    for i, p in enumerate(result["results"], 1):
        print(f"  {i:2}. [{p['product_id']:2}] {p['product_name']}")
        print(f"      {p['order_count']} orders")
        for r in p["reviews"]:
            stars = r["rating"] * "*"
            print(f"      {stars:<5}  {r['review_date']}  {r['review_text'][:55]}")
        print()


def save_results(stats, speedup):
    os.makedirs("results", exist_ok=True)
    out = {
        "config":   {"top_n": TOP_N, "reviews_per_product": REVIEWS_EACH, "runs": NUM_RUNS},
        "n1":       {"avg_ms": round(stats["n1"]["avg"], 2),    "all": [round(x,2) for x in stats["n1"]["times"]],    "queries": TOP_N+1},
        "batch":    {"avg_ms": round(stats["batch"]["avg"], 2), "all": [round(x,2) for x in stats["batch"]["times"]], "queries": 2},
        "speedup":  round(speedup, 2),
    }
    with open("results/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("  saved → results/benchmark_results.json\n")


if __name__ == "__main__":
    ml    = MediationLayer("data/orders.csv", "data/product_reviews.json", "data/products.json")
    stats = run_benchmark(ml)
    print_top10(stats["n1"]["result"])
    speedup = print_summary(stats)
    save_results(stats, speedup)
