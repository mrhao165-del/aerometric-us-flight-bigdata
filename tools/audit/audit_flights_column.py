#!/usr/bin/env python3
"""Audit the FLIGHTS column across 2016-2024 tabular flight datasets.
Streams line-by-line using constant memory (O(1) RAM).
Records row counts, nulls, NaNs, non-finites, min, max, distinct values and frequencies.
"""
import csv
import math
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "tabular"

def audit_year(year: int):
    csv_path = RAW_DIR / str(year) / f"flight_with_weather_{year}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    start_t = time.time()
    total_rows = 0
    null_count = 0
    nan_count = 0
    inf_count = 0
    non_numeric_count = 0
    min_val = float("inf")
    max_val = float("-inf")
    distinct_counts = Counter()

    # Streaming read with csv.reader
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        try:
            col_idx = header.index("FLIGHTS")
        except ValueError:
            raise ValueError(f"FLIGHTS column not found in header of {year}: {header}")

        for row in reader:
            total_rows += 1
            if len(row) <= col_idx:
                null_count += 1
                continue

            raw_val = row[col_idx].strip()
            if not raw_val or raw_val.lower() == "null" or raw_val.lower() == "none":
                null_count += 1
                distinct_counts["<NULL>"] += 1
                continue

            try:
                val = float(raw_val)
                if math.isnan(val):
                    nan_count += 1
                    distinct_counts["<NAN>"] += 1
                elif math.isinf(val):
                    inf_count += 1
                    distinct_counts["<INF>"] += 1
                else:
                    if val < min_val:
                        min_val = val
                    if val > max_val:
                        max_val = val
                    distinct_counts[raw_val] += 1
            except ValueError:
                non_numeric_count += 1
                distinct_counts[f"<NON_NUMERIC:{raw_val}>"] += 1

    elapsed = time.time() - start_t
    return {
        "year": year,
        "csv_path": str(csv_path.relative_to(ROOT)),
        "total_rows": total_rows,
        "null_count": null_count,
        "nan_count": nan_count,
        "inf_count": inf_count,
        "non_numeric_count": non_numeric_count,
        "min_val": min_val if min_val != float("inf") else None,
        "max_val": max_val if max_val != float("-inf") else None,
        "distinct_counts": dict(distinct_counts),
        "elapsed_sec": round(elapsed, 2),
    }

def main():
    years = list(range(2016, 2025))
    if len(sys.argv) > 1:
        years = [int(y) for y in sys.argv[1:]]

    print(f"Auditing FLIGHTS column for years: {years}")
    all_results = []
    grand_total_rows = 0

    for y in years:
        res = audit_year(y)
        all_results.append(res)
        grand_total_rows += res["total_rows"]
        print(f"[{y}] Rows: {res['total_rows']:,} | Nulls: {res['null_count']} | NaNs: {res['nan_count']} | "
              f"Min: {res['min_val']} | Max: {res['max_val']} | Distinct: {res['distinct_counts']} | Time: {res['elapsed_sec']}s")

    print("\n--- AUDIT SUMMARY ---")
    print(f"Grand Total Rows: {grand_total_rows:,}")
    all_distinct = Counter()
    for r in all_results:
        for k, v in r["distinct_counts"].items():
            all_distinct[k] += v
    print(f"Grand Total Distinct Values in FLIGHTS: {dict(all_distinct)}")

if __name__ == "__main__":
    main()
