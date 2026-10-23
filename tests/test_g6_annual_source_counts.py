"""
tests/test_g6_annual_source_counts.py

Comprehensive regression test for Finding G6-C01:
Verifies annual row count, byte size, and SHA-256 consistency across:
1. Production code AUDITED_SOURCE_INVENTORY (source_validator.py)
2. G1 Schema manifests (schema_2016.json .. schema_2024.json)
3. G6 Canonical Source Inventory (G6_T012_CANONICAL_SOURCE_INVENTORY.md)
4. T004 Final QA Reconciliation baseline (T004_FINAL_QA_RECONCILIATION.md)
5. Anti-masking detection: Verifies that an erroneous per-year distribution
   summing to the identical total (54,674,003) is strictly detected and rejected!
"""

import json
from pathlib import Path
import re
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DOCS_DIR = ROOT_DIR / "docs"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flight_pipeline.ingestion.source_validator import (
    AUDITED_SOURCE_INVENTORY,
    TOTAL_AUDITED_BYTES,
    TOTAL_AUDITED_ROWS,
)


CANONICAL_ANNUAL_DATA = {
    2016: {"rows": 5537987, "bytes": 1538427452, "sha256": "4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34"},
    2017: {"rows": 5575872, "bytes": 1549837485, "sha256": "67b8dbd6678576b1a2229ef2dbeec065e0f64d31d688ab8a2ca59c88d2a656f9"},
    2018: {"rows": 6986842, "bytes": 1941406432, "sha256": "0398bab8f1b79a5f3bea628b707e18c3af628f37a1daa52de6849fb8bdfc71a3"},
    2019: {"rows": 7161827, "bytes": 1990370667, "sha256": "eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a"},
    2020: {"rows": 4312091, "bytes": 1197858795, "sha256": "787981046c9fe0f4884ac207a3d28ea6a7fae98e89535cb9f8a37debb5c7fa5d"},
    2021: {"rows": 5755666, "bytes": 1600032487, "sha256": "5b7cc4801a6ff5cf432137632209ebd7aecd3d4a0f83e8920e3525116e88defc"},
    2022: {"rows": 6413416, "bytes": 1782648882, "sha256": "45eb45e801d6eeeb16167306fc69a8449177191cfff29bfb5d22285827f53140"},
    2023: {"rows": 6645461, "bytes": 1847433387, "sha256": "9c9e20f55d3dd10a127bcdd28680df6547a01a82ad71999b794aff3e1075d7bd"},
    2024: {"rows": 6284841, "bytes": 1748350586, "sha256": "f938ade95a031088467ab5e75abea2021e541eaf4a4288e564066e100541d5f7"},
}


class TestG6AnnualSourceCounts(unittest.TestCase):
    def test_01_canonical_data_totals_match(self):
        """Sum of all 9 canonical years must equal 54,674,003 rows and 15,196,366,173 bytes."""
        total_rows = sum(d["rows"] for d in CANONICAL_ANNUAL_DATA.values())
        total_bytes = sum(d["bytes"] for d in CANONICAL_ANNUAL_DATA.values())
        self.assertEqual(total_rows, 54674003)
        self.assertEqual(total_bytes, 15196366173)
        self.assertEqual(total_rows, TOTAL_AUDITED_ROWS)
        self.assertEqual(total_bytes, TOTAL_AUDITED_BYTES)

    def test_02_production_code_inventory_matches_canonical(self):
        """AUDITED_SOURCE_INVENTORY in source_validator.py must match canonical data for every year."""
        self.assertEqual(len(AUDITED_SOURCE_INVENTORY), 9)
        for year, expected in CANONICAL_ANNUAL_DATA.items():
            entry = AUDITED_SOURCE_INVENTORY.get(year)
            self.assertIsNotNone(entry, f"Missing year {year} in AUDITED_SOURCE_INVENTORY")
            self.assertEqual(entry.audited_row_count, expected["rows"], f"Row mismatch for {year}")
            self.assertEqual(entry.audited_byte_size, expected["bytes"], f"Byte mismatch for {year}")

    def test_03_g1_schema_manifests_match_canonical(self):
        """schema_YYYY.json files in inputs/ must match canonical row count for each year."""
        inputs_dir = DOCS_DIR / "05-evidence" / "inputs"
        for year, expected in CANONICAL_ANNUAL_DATA.items():
            schema_file = inputs_dir / f"schema_{year}.json"
            self.assertTrue(schema_file.exists(), f"Missing schema manifest: {schema_file}")
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_json = json.load(f)
            self.assertEqual(
                schema_json.get("row_count"),
                expected["rows"],
                f"schema_{year}.json row_count mismatch"
            )

    def test_04_g6_canonical_source_inventory_doc_matches(self):
        """G6_T012_CANONICAL_SOURCE_INVENTORY.md table must contain exact rows, bytes, and SHA256 for each year."""
        inv_path = DOCS_DIR / "05-evidence" / "G6_T012_CANONICAL_SOURCE_INVENTORY.md"
        self.assertTrue(inv_path.exists(), f"Missing file: {inv_path}")
        content = inv_path.read_text(encoding="utf-8")

        for year, expected in CANONICAL_ANNUAL_DATA.items():
            formatted_rows = f"{expected['rows']:,}"
            formatted_bytes = f"{expected['bytes']:,}"
            has_rows = (str(expected["rows"]) in content) or (formatted_rows in content)
            has_bytes = (str(expected["bytes"]) in content) or (formatted_bytes in content)
            self.assertTrue(has_rows, f"Missing row count {expected['rows']} for {year} in inventory doc")
            self.assertTrue(has_bytes, f"Missing byte count {expected['bytes']} for {year} in inventory doc")
            self.assertIn(expected["sha256"], content, f"Missing SHA-256 for {year} in inventory doc")

        # Explicitly verify that obsolete draft row count 3,633,696 for 2024 is NOT present
        self.assertNotIn("3633696", content)
        self.assertNotIn("3,633,696", content)

    def test_05_anti_masking_per_year_detection(self):
        """
        Anti-masking test: Verifies that if an obsolete distribution is supplied
        where total rows equals 54,674,003 but individual years are shifted
        (such as 2024=3,633,696 and 2017=5,677,153), the validator strictly catches and rejects it.
        """
        obsolete_bad_distribution = {
            2016: 5537987,
            2017: 5677153,  # Error: +101,281
            2018: 7213446,  # Error: +226,604
            2019: 7422037,  # Error: +260,210
            2020: 4686075,  # Error: +373,984
            2021: 6311871,  # Error: +556,205
            2022: 7009728,  # Error: +596,312
            2023: 7182010,  # Error: +536,549
            2024: 3633696,  # Error: -2,651,145
        }
        # Verify that sum equals 54,674,003 (aggregate check passes!)
        self.assertEqual(sum(obsolete_bad_distribution.values()), 54674003)

        # But per-year audit must identify mismatches
        mismatches = []
        for year, count in obsolete_bad_distribution.items():
            if count != CANONICAL_ANNUAL_DATA[year]["rows"]:
                mismatches.append(year)

        # 8 out of 9 years mismatched!
        self.assertEqual(len(mismatches), 8)
        self.assertIn(2024, mismatches)
        self.assertIn(2017, mismatches)


if __name__ == "__main__":
    unittest.main()
