#!/usr/bin/env python3
"""
tools/qa/test_ts018_negative_witness_verification.py

Automated Negative Test Suite for TS-018 Sample Witness Verifier (Hardened & Dossier-Reconciled):
- Runs in an isolated temporary directory; never mutates production or reference data.
- Systematically tests 14 distinct error injections against witness verification logic:
  [Category A: Process-Level Mutation Verification]
  1. NEG-W01: Witness value mismatch with raw project CSV (-999.0 vs real -6.0).
  2. NEG-W02: Non-existent composite key in witness (2019-01-01|ZZ|9999|XYZ|ZZZ).
  3. NEG-W03: Sealed witness checksum tampering caught fail-closed by pinned hash check (H05).
  4. NEG-W04: Slipped sign on delay field (-6.0 -> +6.0).
  5. NEG-W05: Duplicate key collision in witness detected fail-closed (H05).
  6. NEG-W06: Non-zero measure replaced with zero (TAXI_OUT 13.0 -> 0.0).
  7. NEG-W07: Tolerance-only deviation (+0.00005 vs real) under strict exact check (H01).
  8. NEG-W08: Genuine null disagreement (empty string for AIR_TIME vs 98.0).
  9. NEG-W09: Non-finite token injection ("NaN" in CRS_ELAPSED_TIME) caught strictly as NONFINITE_OR_INVALID_TOKEN (H02/H04/E05).
  10. NEG-W10: Authentic flight date discrepancy (NK 314 date mutated to 2019-01-20).
  [Category B: Component Parser & IEEE-754 Classifier Verification]
  11. NEG-W11: Two sources both containing "NaN" rejected as non-finite, NOT null-null (H02).
  12. NEG-W12: Signed zero (+0.0 vs -0.0) separated from bitwise exact match (H03).
  13. NEG-W13: Parser rejects unparsable text tokens from silently becoming None/null (H02).
  [Category C: Strict Exact Policy Guard Verification]
  14. NEG-W14: Synthetic null-null evaluates strictly to NULL_NULL_AGREEMENT, rejected from bitwise exact (E04/E05).
- Asserts that every injected fault is caught fail-closed with non-zero exit code
  and target-specific diagnostic messages (no unhandled traceback fallbacks).
"""

import csv
import hashlib
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[2]
REAL_WITNESS = ROOT / "docs" / "05-evidence" / "TS018_201901_MATCHED_SAMPLE_WITNESS.csv"
VERIFIER_SCRIPT = ROOT / "tools" / "qa" / "verify_ts018_two_source_sample_witness.py"

sys.path.insert(0, str(ROOT))
import tools.qa.verify_ts018_two_source_sample_witness as v

results = []


def run_verifier_on_custom_witness(
    custom_witness_path: Path,
    strict_exact: bool = True,
    verify_pinned_hash: bool = False,
) -> subprocess.CompletedProcess:
    """Run verification logic targeting a custom witness path."""
    cmd = [
        sys.executable,
        "-c",
        f"""
import sys
from pathlib import Path
sys.path.insert(0, r"{ROOT}")
import tools.qa.verify_ts018_two_source_sample_witness as verifier

verifier.WITNESS_PATH = Path(r"{custom_witness_path}")
verifier.REQUIRE_STRICT_EXACT = {strict_exact}
verifier.VERIFY_WITNESS_PINNED_HASH = {verify_pinned_hash}
verifier.main()
""",
    ]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))


def record_result(test_id: str, passed: bool, description: str, detail: str = ""):
    results.append((test_id, passed, description, detail))
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {test_id}: {description}" + (f" -> {detail}" if detail else ""))


def main():
    print("=" * 80)
    print("RUNNING TS-018 COMPREHENSIVE NEGATIVE WITNESS FAULT INJECTION TEST SUITE")
    print("=" * 80)

    if not REAL_WITNESS.is_file():
        raise SystemExit(f"Real witness file missing at {REAL_WITNESS}")

    with tempfile.TemporaryDirectory(prefix="ts018_neg_test_") as tmp_dir:
        tmp_path = Path(tmp_dir)

        rows = []
        with open(REAL_WITNESS, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            header = reader[0]
            rows = reader[1:]

        arr_idx = header.index("RAW_DATASET_ARR_DELAY")
        tax_idx = header.index("RAW_DATASET_TAXI_OUT")
        air_idx = header.index("RAW_DATASET_AIR_TIME")
        crs_idx = header.index("RAW_DATASET_CRS_ELAPSED_TIME")

        # ---------------------------------------------------------------------
        # NEG-W01: Witness value mismatch with raw project CSV
        # ---------------------------------------------------------------------
        w01_path = tmp_path / "witness_w01.csv"
        rows_w01 = [list(r) for r in rows]
        rows_w01[0][arr_idx] = "-999.0"

        with open(w01_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows_w01)

        res_w01 = run_verifier_on_custom_witness(w01_path)
        out_w01 = res_w01.stdout + res_w01.stderr
        caught_w01 = res_w01.returncode != 0 and "mismatches between raw CSV and witness" in out_w01
        record_result(
            "NEG-W01",
            caught_w01,
            "Injected value mismatch in witness (-999.0 vs real) is caught fail-closed",
            f"exit={res_w01.returncode}",
        )

        # ---------------------------------------------------------------------
        # NEG-W02: Non-existent flight key in witness
        # ---------------------------------------------------------------------
        w02_path = tmp_path / "witness_w02.csv"
        rows_w02 = [list(r) for r in rows]
        rows_w02[0][0] = "2019-01-01"
        rows_w02[0][1] = "ZZ"
        rows_w02[0][2] = "9999"
        rows_w02[0][3] = "XYZ"
        rows_w02[0][4] = "ZZZ"

        with open(w02_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows_w02)

        res_w02 = run_verifier_on_custom_witness(w02_path)
        out_w02 = res_w02.stdout + res_w02.stderr
        caught_w02 = res_w02.returncode != 0 and "missing from raw CSV" in out_w02
        record_result(
            "NEG-W02",
            caught_w02,
            "Non-existent flight key in witness is caught fail-closed",
            f"exit={res_w02.returncode}",
        )

        # ---------------------------------------------------------------------
        # NEG-W03: Sealed witness checksum tampering caught by pinned hash check (H05)
        # ---------------------------------------------------------------------
        w03_path = tmp_path / "witness_w03.csv"
        corrupted_bytes = REAL_WITNESS.read_bytes() + b"\nEXTRA_CORRUPT_TRAILING_LINE\n"
        w03_path.write_bytes(corrupted_bytes)

        # Explicitly verify with verify_pinned_hash = True to test H05 pinned check
        res_w03 = run_verifier_on_custom_witness(w03_path, verify_pinned_hash=True)
        out_w03 = res_w03.stdout + res_w03.stderr
        caught_w03 = res_w03.returncode != 0 and "Sealed witness checksum mismatch" in out_w03
        record_result(
            "NEG-W03",
            caught_w03,
            "Tampered witness checksum is caught fail-closed by pinned SHA-256 validator (H05)",
            f"exit={res_w03.returncode}",
        )

        # ---------------------------------------------------------------------
        # NEG-W04: Slipped sign on delay field (-6.0 -> +6.0)
        # ---------------------------------------------------------------------
        w04_path = tmp_path / "witness_w04.csv"
        rows_w04 = [list(r) for r in rows]
        for r in rows_w04:
            if r[0] == "2019-01-10" and r[1] == "NK" and r[2] == "314":
                r[arr_idx] = "6.0"
                break

        with open(w04_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows_w04)

        res_w04 = run_verifier_on_custom_witness(w04_path)
        out_w04 = res_w04.stdout + res_w04.stderr
        caught_w04 = res_w04.returncode != 0 and "mismatches between raw CSV and witness" in out_w04
        record_result(
            "NEG-W04",
            caught_w04,
            "Slipped sign on arrival delay (-6.0 -> +6.0) is caught fail-closed",
            f"exit={res_w04.returncode}",
        )

        # ---------------------------------------------------------------------
        # NEG-W05: Duplicate key collision in witness (H05)
        # ---------------------------------------------------------------------
        w05_path = tmp_path / "witness_w05.csv"
        rows_w05 = [list(r) for r in rows]
        rows_w05[1] = list(rows_w05[0])

        with open(w05_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows_w05)

        res_w05 = run_verifier_on_custom_witness(w05_path)
        out_w05 = res_w05.stdout + res_w05.stderr
        caught_w05 = res_w05.returncode != 0 and "Duplicate composite key detected in witness" in out_w05
        record_result(
            "NEG-W05",
            caught_w05,
            "Duplicate key collision in witness is detected fail-closed before ingestion (H05)",
            f"exit={res_w05.returncode}",
        )

        # ---------------------------------------------------------------------
        # NEG-W06: Non-zero measure replaced with zero (TAXI_OUT 13.0 -> 0.0)
        # ---------------------------------------------------------------------
        w06_path = tmp_path / "witness_w06.csv"
        rows_w06 = [list(r) for r in rows]
        rows_w06[0][tax_idx] = "0.0"

        with open(w06_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows_w06)

        res_w06 = run_verifier_on_custom_witness(w06_path)
        out_w06 = res_w06.stdout + res_w06.stderr
        caught_w06 = res_w06.returncode != 0 and "mismatches between raw CSV and witness" in out_w06
        record_result(
            "NEG-W06",
            caught_w06,
            "Non-zero numeric measure replaced with 0.0 is caught fail-closed",
            f"exit={res_w06.returncode}",
        )

        # ---------------------------------------------------------------------
        # NEG-W07: Tolerance-only deviation (+0.00005 vs real) under strict exact check (H01)
        # ---------------------------------------------------------------------
        w07_path = tmp_path / "witness_w07.csv"
        rows_w07 = [list(r) for r in rows]
        rows_w07[0][arr_idx] = "-5.99995"  # Actual is -6.0, diff = 0.00005 <= 1e-4

        with open(w07_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows_w07)

        res_w07 = run_verifier_on_custom_witness(w07_path, strict_exact=True)
        out_w07 = res_w07.stdout + res_w07.stderr
        caught_w07 = res_w07.returncode != 0 and ("STRICT_FAIL" in out_w07 or "mismatches between raw CSV and witness" in out_w07 or "Strict exact mode violation" in out_w07)
        record_result(
            "NEG-W07",
            caught_w07,
            "Tolerance-only deviation (+0.00005) under strict exact check is rejected fail-closed (H01)",
            f"exit={res_w07.returncode}",
        )

        # ---------------------------------------------------------------------
        # NEG-W08: Genuine null disagreement (empty string for AIR_TIME vs real 98.0)
        # ---------------------------------------------------------------------
        w08_path = tmp_path / "witness_w08.csv"
        rows_w08 = [list(r) for r in rows]
        rows_w08[0][air_idx] = ""

        with open(w08_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows_w08)

        res_w08 = run_verifier_on_custom_witness(w08_path)
        out_w08 = res_w08.stdout + res_w08.stderr
        caught_w08 = res_w08.returncode != 0 and "mismatches between raw CSV and witness" in out_w08
        record_result(
            "NEG-W08",
            caught_w08,
            "Genuine null-to-value disagreement on AIR_TIME is caught fail-closed",
            f"exit={res_w08.returncode}",
        )

        # ---------------------------------------------------------------------
        # NEG-W09: Non-finite token injection ("NaN" in CRS_ELAPSED_TIME) (H02/H04)
        # ---------------------------------------------------------------------
        w09_path = tmp_path / "witness_w09.csv"
        rows_w09 = [list(r) for r in rows]
        rows_w09[0][crs_idx] = "NaN"

        with open(w09_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows_w09)

        res_w09 = run_verifier_on_custom_witness(w09_path)
        out_w09 = res_w09.stdout + res_w09.stderr
        caught_w09 = res_w09.returncode != 0 and "NONFINITE_OR_INVALID_TOKEN" in out_w09
        record_result(
            "NEG-W09",
            caught_w09,
            "Non-finite numeric value ('NaN') is caught fail-closed as invalid token (H02/H04/E05)",
            f"exit={res_w09.returncode}",
        )

        # ---------------------------------------------------------------------
        # NEG-W10: Authentic flight date discrepancy (NK 314 date mutated to 2019-01-20)
        # ---------------------------------------------------------------------
        w10_path = tmp_path / "witness_w10.csv"
        rows_w10 = [list(r) for r in rows]
        rows_w10[0][0] = "2019-01-20"

        with open(w10_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows_w10)

        res_w10 = run_verifier_on_custom_witness(w10_path)
        out_w10 = res_w10.stdout + res_w10.stderr
        caught_w10 = res_w10.returncode != 0 and ("mismatches between raw CSV and witness" in out_w10 or "missing from raw CSV" in out_w10)
        record_result(
            "NEG-W10",
            caught_w10,
            "Flight date mismatch (2019-01-10 mutated to 2019-01-20) is caught fail-closed",
            f"exit={res_w10.returncode}",
        )

    # -------------------------------------------------------------------------
    # NEG-W11: Two sources both containing "NaN" (Anti-False-Pass Verification) (H02)
    # -------------------------------------------------------------------------
    nan_cell_a = v.parse_numeric_cell("NaN")
    nan_cell_b = v.parse_numeric_cell("NaN")
    cat_w11, diff_w11 = v.classify_cells(nan_cell_a, nan_cell_b)
    passed_w11 = (
        nan_cell_a.kind == "NONFINITE_OR_INVALID_TOKEN"
        and nan_cell_b.kind == "NONFINITE_OR_INVALID_TOKEN"
        and cat_w11 == "NONFINITE_OR_INVALID_TOKEN"
        and cat_w11 != "NULL_NULL_AGREEMENT"
    )
    record_result(
        "NEG-W11",
        passed_w11,
        "Two sources both containing 'NaN' are rejected as NONFINITE, never NULL_NULL (H02)",
        f"category={cat_w11}",
    )

    # -------------------------------------------------------------------------
    # NEG-W12: Signed zero (+0.0 vs -0.0) semantic separation (H03)
    # -------------------------------------------------------------------------
    pos_zero_cell = v.parse_numeric_cell("0.0")
    neg_zero_cell = v.parse_numeric_cell("-0.0")
    cat_w12, diff_w12 = v.classify_cells(pos_zero_cell, neg_zero_cell)
    passed_w12 = (
        cat_w12 == "NUMERIC_EQUAL_SIGNED_ZERO_DIFF"
        and cat_w12 != "EXACT_BITWISE_MATCH"
        and diff_w12 == 0.0
    )
    record_result(
        "NEG-W12",
        passed_w12,
        "Signed zero (+0.0 vs -0.0) is classified as NUMERIC_EQUAL_SIGNED_ZERO_DIFF, not bitwise exact (H03)",
        f"category={cat_w12}",
    )

    # -------------------------------------------------------------------------
    # NEG-W13: Parser rejects unparsable text tokens from becoming None/null (H02)
    # -------------------------------------------------------------------------
    bad_tokens = ["CORRUPT_TOKEN", "Infinity", "-Infinity", "12.34.56", "NoneValid"]
    parsed_kinds = [v.parse_numeric_cell(tok).kind for tok in bad_tokens]
    passed_w13 = all(k == "NONFINITE_OR_INVALID_TOKEN" for k in parsed_kinds) and all(k != "VALID_NULL" for k in parsed_kinds)
    record_result(
        "NEG-W13",
        passed_w13,
        "Parser strictly classifies malformed / infinite text tokens as invalid, never valid null (H02)",
        f"kinds={parsed_kinds[:2]}",
    )

    # -------------------------------------------------------------------------
    # NEG-W14: Synthetic null-null agreement policy guard (E04/E05)
    # Proves null-null evaluates strictly to NULL_NULL_AGREEMENT and cannot masquerade as bitwise exact
    # -------------------------------------------------------------------------
    null_cell_a = v.parse_numeric_cell("")
    null_cell_b = v.parse_numeric_cell("")
    cat_w14, diff_w14 = v.classify_cells(null_cell_a, null_cell_b)
    passed_w14 = (
        null_cell_a.kind == "VALID_NULL"
        and null_cell_b.kind == "VALID_NULL"
        and cat_w14 == "NULL_NULL_AGREEMENT"
        and cat_w14 != "EXACT_BITWISE_MATCH"
        and diff_w14 == 0.0
    )
    record_result(
        "NEG-W14",
        passed_w14,
        "Synthetic null-null evaluates strictly to NULL_NULL_AGREEMENT, rejected from bitwise exact (E04)",
        f"category={cat_w14}",
    )

    print("=" * 80)
    passed_count = sum(1 for _, p, _, _ in results if p)
    failed_count = sum(1 for _, p, _, _ in results if not p)
    print(f"NEGATIVE TEST SUITE SUMMARY: {passed_count} PASS, {failed_count} FAIL (Total: {len(results)})")
    print("=" * 80)

    if failed_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
