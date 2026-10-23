#!/usr/bin/env python3
"""
tools/qa/verify_ts018_two_source_sample_witness.py

Independent Two-Source Replay Verifier for TS-018:
- Verifies TS018_201901_MATCHED_SAMPLE_WITNESS.csv against BOTH physical files:
  1. Authentic raw project CSV: data/raw/tabular/2019/flight_with_weather_2019.csv
  2. Authentic BTS reference ZIP: data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip
- Ensures the witness was NOT fabricated from a single source or synthetic fixture.
- Pin-verifies SHA-256 and byte size of witness and physical sources.
- Independently reads all 1,500 composite keys from the witness.
- Detects duplicate keys in witness and both physical sources (prevents dictionary overwrite masking).
- Distinguishes canonical valid NULL from invalid / nonfinite tokens (NaN, Inf, corrupt parse).
- Distinguishes strict IEEE-754 bitwise equality from numeric signed-zero equality (+0.0 vs -0.0) and tolerance-only.
- Enforces REQUIRE_STRICT_EXACT = True by default for signoff acceptance.
- Asserts 100% record-level bitwise parity across all 10,500 comparisons (1,500 flights x 7 fields).
- Fails with non-zero exit code if any mismatch, tolerance-only match, missing record, duplicate key, or checksum violation is detected.
"""

from collections import Counter
import csv
import hashlib
import io
import math
from pathlib import Path
import struct
import sys
from typing import Any, Dict, List, Optional, Tuple
import zipfile

ROOT = Path(__file__).resolve().parents[2]

WITNESS_PATH = ROOT / "docs" / "05-evidence" / "TS018_201901_MATCHED_SAMPLE_WITNESS.csv"
RAW_CSV_PATH = ROOT / "data" / "raw" / "tabular" / "2019" / "flight_with_weather_2019.csv"
BTS_ZIP_PATH = ROOT / "data" / "reference" / "bts_transtats" / "original" / "T_ONTIME_REPORTING_20261019_112232.zip"

EXPECTED_BTS_ZIP_SHA256 = "342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6"
EXPECTED_BTS_ZIP_BYTES = 29975383

EXPECTED_RAW_CSV_SHA256 = "eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a"
EXPECTED_RAW_CSV_BYTES = 1990370667

EXPECTED_WITNESS_SHA256 = "942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1"
EXPECTED_WITNESS_BYTES = 294436

# H01: Strict exact is required by default for signoff verification
REQUIRE_STRICT_EXACT = True

# H05: Pin witness SHA-256 by default; can be disabled only by custom mutation tests
VERIFY_WITNESS_PINNED_HASH = True

CORE_NUMERIC_FIELDS = [
    "ARR_DELAY",
    "DEP_DELAY",
    "TAXI_OUT",
    "TAXI_IN",
    "AIR_TIME",
    "ACTUAL_ELAPSED_TIME",
    "CRS_ELAPSED_TIME",
]


class ParsedCell:
    """
    Explicit representation of a parsed numeric cell:
    - VALID_FLOAT: Parsed finite float value.
    - VALID_NULL: Canonical valid null representation per Data Contract (empty string or 'null'/'none').
    - NONFINITE_OR_INVALID_TOKEN: Invalid string, NaN, Inf, or unparsable token.
    """
    def __init__(self, kind: str, value: Optional[float] = None, raw_token: str = ""):
        self.kind = kind
        self.value = value
        self.raw_token = raw_token

    def __repr__(self) -> str:
        return f"ParsedCell({self.kind}, {self.value}, {self.raw_token!r})"


def normalize_iso_date(raw_date_str: str) -> str:
    cleaned = raw_date_str.strip().split()[0]
    if "/" in cleaned:
        parts = cleaned.split("/")
        m, d, y = int(parts[0]), int(parts[1]), int(parts[2])
        return f"{y:04d}-{m:02d}-{d:02d}"
    elif "-" in cleaned:
        parts = cleaned.split("-")
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        return f"{y:04d}-{m:02d}-{d:02d}"
    return cleaned


def normalize_flight_number(raw_fl_num: str) -> str:
    val = raw_fl_num.strip()
    if not val:
        return ""
    try:
        fval = float(val)
        return str(int(fval))
    except ValueError:
        return val


def parse_numeric_cell(raw_val: str) -> ParsedCell:
    """
    H02: Parse cell distinguishing genuine valid null from invalid numeric tokens.
    Never silently converts 'NaN', 'Inf', or malformed tokens to None or 0.0.
    """
    val = raw_val.strip()
    if val == "" or val.lower() in ("null", "none"):
        return ParsedCell("VALID_NULL", None, raw_val)

    if val.lower() in ("nan", "na", "inf", "-inf", "infinity", "-infinity"):
        return ParsedCell("NONFINITE_OR_INVALID_TOKEN", None, raw_val)

    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return ParsedCell("NONFINITE_OR_INVALID_TOKEN", None, raw_val)
        return ParsedCell("VALID_FLOAT", f, raw_val)
    except ValueError:
        return ParsedCell("NONFINITE_OR_INVALID_TOKEN", None, raw_val)


def classify_cells(cell_a: ParsedCell, cell_b: ParsedCell) -> Tuple[str, float]:
    """
    H03: Strictly classify comparison between two parsed cells:
    1. EXACT_BITWISE_MATCH: Finite floats with identical IEEE-754 64-bit bits (diff == 0.0).
    2. NUMERIC_EQUAL_SIGNED_ZERO_DIFF: val_a == val_b (0.0), but bits differ (+0.0 vs -0.0).
    3. TOLERANCE_ONLY_MATCH: Finite floats with 0.0 < abs(val_a - val_b) <= 1e-4.
    4. NULL_NULL_AGREEMENT: Both cells are genuinely VALID_NULL.
    5. MISMATCH: Value difference > 1e-4 or null disagreement.
    6. NONFINITE_OR_INVALID_TOKEN: Either cell contains a non-finite or invalid token.
    """
    # Category 4: Both valid nulls
    if cell_a.kind == "VALID_NULL" and cell_b.kind == "VALID_NULL":
        return ("NULL_NULL_AGREEMENT", 0.0)

    # Category 6: Any non-finite or invalid token encountered
    if cell_a.kind == "NONFINITE_OR_INVALID_TOKEN" or cell_b.kind == "NONFINITE_OR_INVALID_TOKEN":
        return ("NONFINITE_OR_INVALID_TOKEN", float("nan"))

    # Category 5a: Null vs float disagreement
    if cell_a.kind == "VALID_NULL" or cell_b.kind == "VALID_NULL":
        return ("MISMATCH", float("inf"))

    # Both are VALID_FLOAT
    val_a = cell_a.value
    val_b = cell_b.value
    assert val_a is not None and val_b is not None

    diff = abs(val_a - val_b)
    bits_a = struct.pack(">d", val_a)
    bits_b = struct.pack(">d", val_b)

    if bits_a == bits_b:
        return ("EXACT_BITWISE_MATCH", 0.0)
    elif val_a == val_b:
        # e.g., +0.0 (0x0000000000000000) vs -0.0 (0x8000000000000000)
        return ("NUMERIC_EQUAL_SIGNED_ZERO_DIFF", 0.0)
    elif diff <= 1e-4:
        return ("TOLERANCE_ONLY_MATCH", diff)
    else:
        return ("MISMATCH", diff)


def verify_file_sha256(path: Path, expected_sha: str, expected_bytes: Optional[int], label: str) -> str:
    if not path.is_file():
        raise SystemExit(f"[FAIL] {label} missing at {path}")
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024 * 8), b""):
            digest.update(chunk)
    actual_sha = digest.hexdigest()
    actual_bytes = path.stat().st_size

    if actual_sha != expected_sha:
        raise SystemExit(f"[FAIL] {label} checksum mismatch: got {actual_sha}, expected {expected_sha}")
    if expected_bytes is not None and actual_bytes != expected_bytes:
        raise SystemExit(f"[FAIL] {label} byte size mismatch: got {actual_bytes}, expected {expected_bytes}")

    print(f"[OK] {label} checksum & size verified: {actual_sha} ({actual_bytes} bytes)")
    return actual_sha


def main():
    print("=" * 80)
    print("INDEPENDENT TWO-SOURCE SAMPLE WITNESS VERIFIER (TS-018 - HARDENED)")
    print("=" * 80)

    # 1. Verify physical files and checksums
    if not WITNESS_PATH.is_file():
        raise SystemExit(f"[FAIL] Witness CSV missing at {WITNESS_PATH}")
    witness_sha = hashlib.sha256(WITNESS_PATH.read_bytes()).hexdigest()
    witness_bytes = WITNESS_PATH.stat().st_size
    print(f"[WITNESS] Path:   {WITNESS_PATH}")
    print(f"[WITNESS] Bytes:  {witness_bytes}")
    print(f"[WITNESS] SHA256: {witness_sha}")

    if VERIFY_WITNESS_PINNED_HASH:
        if witness_sha != EXPECTED_WITNESS_SHA256:
            raise SystemExit(f"[FAIL] Sealed witness checksum mismatch: got {witness_sha}, expected {EXPECTED_WITNESS_SHA256}")
        if witness_bytes != EXPECTED_WITNESS_BYTES:
            raise SystemExit(f"[FAIL] Sealed witness byte size mismatch: got {witness_bytes}, expected {EXPECTED_WITNESS_BYTES}")
        print("[OK] Sealed witness pinned SHA-256 and byte size verified.")

    verify_file_sha256(BTS_ZIP_PATH, EXPECTED_BTS_ZIP_SHA256, EXPECTED_BTS_ZIP_BYTES, "Candidate BTS ZIP")
    verify_file_sha256(RAW_CSV_PATH, EXPECTED_RAW_CSV_SHA256, EXPECTED_RAW_CSV_BYTES, "Raw 2019 Dataset CSV")

    # 2. Ingest Witness CSV with duplicate detection
    print(f"\n[PHASE 1] Ingesting sample witness records from CSV...")
    witness_records = {}
    witness_key_counts = Counter()

    with open(WITNESS_PATH, "r", encoding="utf-8") as wf:
        reader = csv.DictReader(wf)
        for r in reader:
            key = (
                r["FL_DATE"].strip(),
                r["OP_CARRIER"].strip(),
                r["OP_CARRIER_FL_NUM"].strip(),
                r["ORIGIN"].strip(),
                r["DEST"].strip(),
            )
            witness_key_counts[key] += 1
            witness_records[key] = {
                "STRATUM": r["STRATUM"].strip(),
                "SELECTION_SCORE": r["SELECTION_SCORE"].strip(),
                "RAW_DATASET": {col: parse_numeric_cell(r[f"RAW_DATASET_{col}"]) for col in CORE_NUMERIC_FIELDS},
                "BTS": {col: parse_numeric_cell(r[f"BTS_{col}"]) for col in CORE_NUMERIC_FIELDS},
            }

    witness_count = len(witness_records)
    print(f"[WITNESS STATS] Total unique witness keys loaded: {witness_count}")

    # Check for duplicate keys in witness (H05)
    dup_witness_keys = [k for k, count in witness_key_counts.items() if count > 1]
    if dup_witness_keys:
        raise SystemExit(f"[FAIL] Duplicate composite key detected in witness: count={len(dup_witness_keys)}, sample={dup_witness_keys[:3]}")

    if witness_count != 1500:
        raise SystemExit(f"[FAIL] Expected exactly 1500 witness records, got {witness_count}")

    # 3. Independent verification against Raw Dataset CSV with duplicate detection
    print(f"\n[PHASE 2] Replaying against physical Raw Dataset CSV ({RAW_CSV_PATH.name})...")
    raw_found = {}
    raw_key_occurrences = Counter()
    raw_mismatches = []

    with open(RAW_CSV_PATH, "r", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        header = next(reader)
        d_idx = header.index("FL_DATE")
        c_idx = header.index("OP_CARRIER")
        fn_idx = header.index("OP_CARRIER_FL_NUM")
        o_idx = header.index("ORIGIN")
        dst_idx = header.index("DEST")
        num_indices = {col: header.index(col) for col in CORE_NUMERIC_FIELDS}

        for row in reader:
            d_str = row[d_idx].split()[0]
            if d_str.startswith("2019-01-"):
                k = (
                    d_str,
                    row[c_idx].strip(),
                    normalize_flight_number(row[fn_idx]),
                    row[o_idx].strip(),
                    row[dst_idx].strip(),
                )
                if k in witness_records:
                    raw_key_occurrences[k] += 1
                    actual_cells = {col: parse_numeric_cell(row[idx]) for col, idx in num_indices.items()}
                    raw_found[k] = actual_cells
                    expected_cells = witness_records[k]["RAW_DATASET"]

                    for col in CORE_NUMERIC_FIELDS:
                        ac = actual_cells[col]
                        ec = expected_cells[col]
                        cat, diff = classify_cells(ac, ec)
                        if cat in ("MISMATCH", "NONFINITE_OR_INVALID_TOKEN"):
                            raw_mismatches.append((k, col, cat, ac, ec))
                        elif REQUIRE_STRICT_EXACT and cat in ("TOLERANCE_ONLY_MATCH", "NUMERIC_EQUAL_SIGNED_ZERO_DIFF"):
                            raw_mismatches.append((k, col, f"STRICT_FAIL({cat})", ac, ec))

    # Audit duplicate occurrences in Raw CSV (H05)
    raw_duplicates = [k for k, count in raw_key_occurrences.items() if count > 1]
    print(f"[DATASET REPLAY] Witness keys matched in Raw CSV: {len(raw_found)} / 1500")
    print(f"[DATASET REPLAY] Duplicate key collisions in Raw CSV: {len(raw_duplicates)}")
    if raw_duplicates:
        raise SystemExit(f"[FAIL] Duplicate composite keys detected in Raw CSV: {len(raw_duplicates)}")

    if len(raw_found) != 1500:
        missing = set(witness_records.keys()) - set(raw_found.keys())
        raise SystemExit(f"[FAIL] {len(missing)} witness keys missing from raw CSV! Sample: {list(missing)[:3]}")

    if raw_mismatches:
        first_cat = raw_mismatches[0][2]
        raise SystemExit(f"[FAIL] {len(raw_mismatches)} value mismatches between raw CSV and witness (includes {first_cat})! Sample: {raw_mismatches[:3]}")
    print("[OK] All 1,500 witness rows match raw project CSV across all 7 fields (10,500/10,500 exact).")

    # 4. Independent verification against Candidate BTS ZIP with duplicate detection
    print(f"\n[PHASE 3] Replaying against physical BTS Reference CSV inside ZIP...")
    bts_found = {}
    bts_key_occurrences = Counter()
    bts_mismatches = []

    with zipfile.ZipFile(BTS_ZIP_PATH, "r") as zf:
        if zf.testzip() is not None:
            raise SystemExit("[FAIL] BTS ZIP CRC test failed!")
        with zf.open("T_ONTIME_REPORTING.csv") as bf:
            wrapper = io.TextIOWrapper(bf, encoding="utf-8", errors="replace")
            reader = csv.reader(wrapper)
            header = next(reader)
            b_d_idx = header.index("FL_DATE")
            b_c_idx = header.index("OP_CARRIER")
            b_fn_idx = header.index("OP_CARRIER_FL_NUM")
            b_o_idx = header.index("ORIGIN")
            b_dst_idx = header.index("DEST")
            b_num_indices = {col: header.index(col) for col in CORE_NUMERIC_FIELDS}

            for row in reader:
                iso_d = normalize_iso_date(row[b_d_idx])
                k = (
                    iso_d,
                    row[b_c_idx].strip(),
                    normalize_flight_number(row[b_fn_idx]),
                    row[b_o_idx].strip(),
                    row[b_dst_idx].strip(),
                )
                if k in witness_records:
                    bts_key_occurrences[k] += 1
                    actual_cells = {col: parse_numeric_cell(row[idx]) for col, idx in b_num_indices.items()}
                    bts_found[k] = actual_cells
                    expected_cells = witness_records[k]["BTS"]

                    for col in CORE_NUMERIC_FIELDS:
                        ac = actual_cells[col]
                        ec = expected_cells[col]
                        cat, diff = classify_cells(ac, ec)
                        if cat in ("MISMATCH", "NONFINITE_OR_INVALID_TOKEN"):
                            bts_mismatches.append((k, col, cat, ac, ec))
                        elif REQUIRE_STRICT_EXACT and cat in ("TOLERANCE_ONLY_MATCH", "NUMERIC_EQUAL_SIGNED_ZERO_DIFF"):
                            bts_mismatches.append((k, col, f"STRICT_FAIL({cat})", ac, ec))

    # Audit duplicate occurrences in BTS CSV (H05)
    bts_duplicates = [k for k, count in bts_key_occurrences.items() if count > 1]
    print(f"[BTS REPLAY] Witness keys matched in BTS CSV:     {len(bts_found)} / 1500")
    print(f"[BTS REPLAY] Duplicate key collisions in BTS CSV: {len(bts_duplicates)}")
    if bts_duplicates:
        raise SystemExit(f"[FAIL] Duplicate composite keys detected in BTS CSV: {len(bts_duplicates)}")

    if len(bts_found) != 1500:
        missing = set(witness_records.keys()) - set(bts_found.keys())
        raise SystemExit(f"[FAIL] {len(missing)} witness keys missing from BTS CSV! Sample: {list(missing)[:3]}")

    if bts_mismatches:
        raise SystemExit(f"[FAIL] {len(bts_mismatches)} value mismatches between BTS CSV and witness! Sample: {bts_mismatches[:3]}")
    print("[OK] All 1,500 witness rows match BTS CSV across all 7 fields (10,500/10,500 exact).")

    # 5. Direct Cross-Source Parity Verification (Raw CSV vs BTS CSV)
    print(f"\n[PHASE 4] Direct Cross-Source Parity Verification (Raw CSV vs BTS CSV)...")
    parity_stats = {
        col: {
            "exact_bitwise": 0,
            "signed_zero_diff": 0,
            "tolerance_only": 0,
            "null_null": 0,
            "mismatch": 0,
            "nonfinite_invalid": 0,
            "max_abs_diff": 0.0,
        }
        for col in CORE_NUMERIC_FIELDS
    }
    cross_source_diffs = []

    for k in witness_records:
        rv = raw_found[k]
        bv = bts_found[k]
        for col in CORE_NUMERIC_FIELDS:
            rc = rv[col]
            bc = bv[col]
            cat, diff = classify_cells(rc, bc)

            if cat == "EXACT_BITWISE_MATCH":
                parity_stats[col]["exact_bitwise"] += 1
            elif cat == "NUMERIC_EQUAL_SIGNED_ZERO_DIFF":
                parity_stats[col]["signed_zero_diff"] += 1
                cross_source_diffs.append((k, col, "SIGNED_ZERO_DIFF", rc, bc))
            elif cat == "TOLERANCE_ONLY_MATCH":
                parity_stats[col]["tolerance_only"] += 1
                if diff > parity_stats[col]["max_abs_diff"]:
                    parity_stats[col]["max_abs_diff"] = diff
                cross_source_diffs.append((k, col, "TOLERANCE_ONLY", rc, bc))
            elif cat == "NULL_NULL_AGREEMENT":
                parity_stats[col]["null_null"] += 1
            elif cat == "NONFINITE_OR_INVALID_TOKEN":
                parity_stats[col]["nonfinite_invalid"] += 1
                cross_source_diffs.append((k, col, "NONFINITE_OR_INVALID_TOKEN", rc, bc))
            else:
                parity_stats[col]["mismatch"] += 1
                if diff > parity_stats[col]["max_abs_diff"]:
                    parity_stats[col]["max_abs_diff"] = diff
                cross_source_diffs.append((k, col, "MISMATCH", rc, bc))

    total_exact_bitwise = sum(parity_stats[c]["exact_bitwise"] for c in CORE_NUMERIC_FIELDS)
    total_signed_zero = sum(parity_stats[c]["signed_zero_diff"] for c in CORE_NUMERIC_FIELDS)
    total_tol_only = sum(parity_stats[c]["tolerance_only"] for c in CORE_NUMERIC_FIELDS)
    total_null_null = sum(parity_stats[c]["null_null"] for c in CORE_NUMERIC_FIELDS)
    total_mismatches = sum(parity_stats[c]["mismatch"] for c in CORE_NUMERIC_FIELDS)
    total_nonfinite_invalid = sum(parity_stats[c]["nonfinite_invalid"] for c in CORE_NUMERIC_FIELDS)

    print(f"\n[PARITY FIELD-BY-FIELD BREAKDOWN]")
    print(f"{'Field':<22} | {'Bitwise Exact':<13} | {'Signed Zero':<11} | {'Tol Only':<9} | {'Null-Null':<9} | {'Mismatch':<9} | {'Max Diff':<10}")
    print("-" * 105)
    for col in CORE_NUMERIC_FIELDS:
        st = parity_stats[col]
        print(f"{col:<22} | {st['exact_bitwise']:<13} | {st['signed_zero_diff']:<11} | {st['tolerance_only']:<9} | {st['null_null']:<9} | {st['mismatch']:<9} | {st['max_abs_diff']:<10.6f}")
    print("-" * 105)
    print(f"{'TOTAL':<22} | {total_exact_bitwise:<13} | {total_signed_zero:<11} | {total_tol_only:<9} | {total_null_null:<9} | {total_mismatches:<9} |")

    print(f"\n[CROSS-SOURCE PARITY SUMMARY]")
    print(f"  Total Comparisons:                10,500 (1,500 flights x 7 fields)")
    print(f"  EXACT_BITWISE_MATCH:              {total_exact_bitwise}")
    print(f"  NUMERIC_EQUAL_SIGNED_ZERO_DIFF:   {total_signed_zero}")
    print(f"  TOLERANCE_ONLY_MATCH:             {total_tol_only}")
    print(f"  NULL_NULL_AGREEMENT:              {total_null_null}")
    print(f"  MISMATCH:                         {total_mismatches}")
    print(f"  NONFINITE_OR_INVALID_TOKEN:       {total_nonfinite_invalid}")

    total_comparisons = len(witness_records) * len(CORE_NUMERIC_FIELDS)

    if total_mismatches > 0 or total_nonfinite_invalid > 0:
        raise SystemExit(f"[FAIL] Cross-source discrepancy detected! Count: {len(cross_source_diffs)}")

    if REQUIRE_STRICT_EXACT:
        if total_tol_only > 0:
            raise SystemExit(f"[FAIL] Strict exact mode violation: {total_tol_only} tolerance-only matches detected!")
        if total_signed_zero > 0:
            raise SystemExit(f"[FAIL] Strict bitwise exact mode violation: {total_signed_zero} signed zero differences detected!")
        if total_null_null > 0:
            raise SystemExit(f"[FAIL] Strict exact mode violation: {total_null_null} null-null agreements detected, but strict signoff mandates 100% bitwise exact floating-point numbers!")
        if total_exact_bitwise != total_comparisons:
            raise SystemExit(f"[FAIL] Strict exact parity incomplete: got {total_exact_bitwise}/{total_comparisons} bitwise exact matches!")

    # Banner selection: ONLY print 100% REPRODUCIBLE STRICT EXACT if total_exact_bitwise == total_comparisons and all deviations are 0
    if (
        total_exact_bitwise == total_comparisons
        and total_signed_zero == 0
        and total_tol_only == 0
        and total_null_null == 0
        and total_mismatches == 0
        and total_nonfinite_invalid == 0
    ):
        print("\n" + "=" * 80)
        print("VERIFICATION RESULT: 100% REPRODUCIBLE STRICT EXACT TWO-SOURCE PARITY PASS")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("VERIFICATION RESULT: NON-STRICT TWO-SOURCE PARITY PASS (WITH NULL/TOLERANCE AGREEMENTS)")
        print("=" * 80)
    print(f"  Witness File:        {WITNESS_PATH.name} (SHA-256: {witness_sha})")
    print(f"  Physical Raw Source: flight_with_weather_2019.csv (SHA-256: {EXPECTED_RAW_CSV_SHA256})")
    print(f"  Physical BTS Source: T_ONTIME_REPORTING_20261019_112232.zip (SHA-256: {EXPECTED_BTS_ZIP_SHA256})")
    print(f"  Total Checked Rows:  1,500 unique keys (0 duplicates)")
    print(f"  Total Fields:        10,500 (7 CORE fields x 1,500 flights)")
    print(f"  Bitwise Exact Rate:  {total_exact_bitwise / 10500 * 100:.2f}% ({total_exact_bitwise} / 10,500 exact)")
    print(f"  Signed Zero Diff:    {total_signed_zero}")
    print(f"  Tolerance-Only:      {total_tol_only}")
    print(f"  Null-Null:           {total_null_null}")
    print("=" * 80)
    sys.exit(0)


if __name__ == "__main__":
    main()
