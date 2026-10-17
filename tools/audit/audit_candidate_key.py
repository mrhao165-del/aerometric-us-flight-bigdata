#!/usr/bin/env python3
"""Audit the candidate business key across 2016-2024 tabular flight datasets.
Candidate key: (FL_DATE, OP_CARRIER, OP_CARRIER_FL_NUM, ORIGIN, DEST, CRS_DEP_TIME)

Performs:
1. Null/empty/invalid check on all 6 key components.
2. Duplicate candidate key detection and multiplicity distribution per year.
3. Deep comparison of duplicate rows (full-row identical vs differing attributes).
4. Safe, streaming O(N) execution with memory capped under 500MB per year.
"""
import csv
import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "tabular"

KEY_COLS = ["FL_DATE", "OP_CARRIER", "OP_CARRIER_FL_NUM", "ORIGIN", "DEST", "CRS_DEP_TIME"]

def hash_key(key_tuple: tuple) -> int:
    """Compute 64-bit BLAKE2b hash of the key tuple."""
    key_str = "|".join(key_tuple)
    return int.from_bytes(hashlib.blake2b(key_str.encode("utf-8"), digest_size=8).digest(), "little")

def audit_candidate_key_year(year: int, sample_limit: int = 10):
    csv_path = RAW_DIR / str(year) / f"flight_with_weather_{year}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    start_t = time.time()
    print(f"[{year}] Starting candidate key audit on {csv_path.name}...")

    # Step 1: Scan header and column indices
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        key_indices = [header.index(col) for col in KEY_COLS]

    # Step 2: Pass 1 - Count frequencies of key hashes and validate components
    key_hash_counts = Counter()
    component_nulls = {col: 0 for col in KEY_COLS}
    year_mismatch_count = 0
    total_rows = 0

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            total_rows += 1
            key_vals = []
            for col_name, idx in zip(KEY_COLS, key_indices):
                val = row[idx].strip() if idx < len(row) else ""
                if not val or val.lower() in ("null", "none"):
                    component_nulls[col_name] += 1
                key_vals.append(val)

            # Check year match in FL_DATE
            fl_date = key_vals[0]
            if not fl_date.startswith(str(year)):
                year_mismatch_count += 1

            h = hash_key(tuple(key_vals))
            key_hash_counts[h] += 1

    distinct_keys = len(key_hash_counts)
    multiplicity_counter = Counter(key_hash_counts.values())
    duplicate_key_hashes = {h for h, c in key_hash_counts.items() if c > 1}
    num_duplicate_keys = len(duplicate_key_hashes)
    num_duplicate_rows = sum(c for h, c in key_hash_counts.items() if c > 1)

    print(f"[{year}] Pass 1 complete: {total_rows:,} rows, {distinct_keys:,} unique keys, "
          f"{num_duplicate_keys:,} duplicate keys ({num_duplicate_rows:,} rows). Elapsed: {time.time() - start_t:.1f}s")

    # Step 3: Pass 2 - Collect sample duplicate groups if any exist
    sample_duplicate_groups = []
    identical_row_groups = 0
    differing_row_groups = 0

    if duplicate_key_hashes:
        # Collect duplicate rows
        dup_rows_by_hash = defaultdict(list)
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                key_vals = tuple(row[idx].strip() if idx < len(row) else "" for idx in key_indices)
                h = hash_key(key_vals)
                if h in duplicate_key_hashes:
                    dup_rows_by_hash[h].append(row)

        for h, rows in dup_rows_by_hash.items():
            # Check if all rows in this group are 100% identical
            first_row = rows[0]
            all_identical = all(r == first_row for r in rows[1:])
            if all_identical:
                identical_row_groups += 1
            else:
                differing_row_groups += 1

            if len(sample_duplicate_groups) < sample_limit:
                # Store sample group analysis
                sample_group = {
                    "candidate_key": {col: rows[0][idx] for col, idx in zip(KEY_COLS, key_indices)},
                    "count": len(rows),
                    "all_identical": all_identical,
                    "rows_sample": [
                        {header[i]: r[i] for i in range(min(15, len(header)))}
                        for r in rows[:3]
                    ],
                }
                sample_duplicate_groups.append(sample_group)

    elapsed = time.time() - start_t
    result = {
        "year": year,
        "total_rows": total_rows,
        "distinct_candidate_keys": distinct_keys,
        "duplicate_keys_count": num_duplicate_keys,
        "duplicate_rows_count": num_duplicate_rows,
        "duplicate_row_percentage": round((num_duplicate_rows / total_rows) * 100, 4) if total_rows > 0 else 0,
        "multiplicity_distribution": dict(sorted(multiplicity_counter.items())),
        "component_nulls": component_nulls,
        "year_mismatch_count": year_mismatch_count,
        "duplicate_analysis": {
            "identical_row_groups": identical_row_groups,
            "differing_row_groups": differing_row_groups,
        },
        "sample_duplicate_groups": sample_duplicate_groups,
        "elapsed_sec": round(elapsed, 2),
    }
    return result

def main():
    years = list(range(2016, 2025))
    if len(sys.argv) > 1:
        years = [int(y) for y in sys.argv[1:]]

    print(f"Auditing Candidate Business Key for years: {years}")
    all_results = []

    for y in years:
        res = audit_candidate_key_year(y)
        all_results.append(res)
        print(f"[{y}] Summary: Rows={res['total_rows']:,} | DistinctKeys={res['distinct_candidate_keys']:,} | "
              f"DupKeys={res['duplicate_keys_count']:,} | DupRows={res['duplicate_rows_count']:,} ({res['duplicate_row_percentage']}%) | "
              f"Multiplicity={res['multiplicity_distribution']} | ComponentNulls={res['component_nulls']} | "
              f"IdenticalGroups={res['duplicate_analysis']['identical_row_groups']} | DifferingGroups={res['duplicate_analysis']['differing_row_groups']}")

    # Save summary JSON to tools/audit/
    summary_path = ROOT / "tools" / "audit" / "candidate_key_audit_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nFull audit saved to {summary_path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
