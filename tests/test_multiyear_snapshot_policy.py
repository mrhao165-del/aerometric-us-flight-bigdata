"""
tests/test_multiyear_snapshot_policy.py

Comprehensive Positive and Negative Regression Test Suite for Production Manifest Compatibility:
Enforces Findings M01, M02, M03, S01, S02, S03, and G6-C03.
Validates production RunManifest.to_dict(), ExecutionReceipt.to_dict(),
Parquet Thrift metadata, physical row count conservation, schema compliance,
and DC-11/12 balanced row accounting.
"""

from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT_DIR / "tools" / "qa"
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from flight_pipeline.ingestion.schema import (
    FORBIDDEN_COLUMNS,
    SEVEN_CORE_MEASURES,
)
from flight_pipeline.ingestion.source_validator import AUDITED_SOURCE_INVENTORY
from flight_pipeline.storage.publication import compute_file_sha256
from flight_pipeline.utils.run_manifest import RowAccounting, RunManifest
from flight_pipeline.ingestion.coordinator import ExecutionReceipt, main as coordinator_main
from verify_multiyear_snapshot import (
    SnapshotValidationResult,
    validate_multiyear_snapshot_registry,
    validate_single_annual_run,
    discover_physical_parquet_files,
)

CANONICAL_COUNTS = {
    year: entry.audited_row_count for year, entry in AUDITED_SOURCE_INVENTORY.items()
}


def _create_canonical_curated_parquet(
    target_file: Path,
    num_rows: int = 2,
    include_core_measures: bool = True,
    forbidden_col: Optional[str] = None,
) -> Tuple[int, str]:
    """Create a physically valid Parquet conforming to DATA_CONTRACT.md schema."""
    arrays = [
        pa.array(["2019-01-01"] * num_rows, type=pa.string()),
        pa.array(["AA"] * num_rows, type=pa.string()),
        pa.array(["JFK"] * num_rows, type=pa.string()),
        pa.array(["LAX"] * num_rows, type=pa.string()),
    ]
    names = ["FL_DATE", "OP_CARRIER", "ORIGIN", "DEST"]

    if include_core_measures:
        for m in SEVEN_CORE_MEASURES:
            names.append(m)
            arrays.append(pa.array([10.0] * num_rows, type=pa.float64()))

    if forbidden_col:
        names.append(forbidden_col)
        arrays.append(pa.array([0] * num_rows, type=pa.int32()))

    table = pa.Table.from_arrays(arrays, names=names)
    pq.write_table(table, str(target_file))
    data = target_file.read_bytes()
    return len(data), sha256(data).hexdigest()


def _create_production_manifest(
    run_id: str,
    year: int,
    raw_count: int,
    accepted_count: int,
    quarantined_count: int = 0,
    rejected_count: int = 0,
    status: str = "PUBLISHED",
    outputs: Optional[List[Dict[str, Any]]] = None,
    years_list: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Build a manifest strictly via production RunManifest.to_dict()."""
    acct = RowAccounting(
        raw_row_count=raw_count,
        accepted_row_count=accepted_count,
        quarantined_row_count=quarantined_count,
        rejected_row_count=rejected_count,
    )
    manifest = RunManifest(
        run_id=run_id,
        task_id="T-012",
        status=status,
        configuration={
            "years": years_list if years_list is not None else [year],
            "base_data_dir": "data",
            "upstream_identity_status": "IDENTITY_UNVERIFIED",
        },
        outputs=outputs or [],
        row_accounting=acct,
    )
    manifest.close(status=status)
    return manifest.to_dict()


def _create_production_receipt(
    run_id: str,
    manifest_file: Path,
    row_accounting: Dict[str, Any],
    status: str = "PUBLISHED",
    override_sha: Optional[str] = None,
    override_bytes: Optional[int] = None,
) -> Dict[str, Any]:
    """Build an execution receipt strictly via production ExecutionReceipt.to_dict()."""
    receipt = ExecutionReceipt(
        run_id=run_id,
        task_id="T-012",
        pipeline_state=status,
        publication_status=status,
        published_path=f"data/curated/runs/{run_id}",
        pointer_value=run_id,
        previous_pointer=None,
        manifest_path=str(manifest_file),
        manifest_bytes=override_bytes if override_bytes is not None else manifest_file.stat().st_size,
        manifest_sha256=override_sha if override_sha is not None else compute_file_sha256(manifest_file),
        row_accounting=row_accounting,
    )
    return receipt.to_dict()


class TestMultiyearSnapshotPolicyComprehensive(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.curated_dir = self.base_dir / "curated"
        self.runs_dir = self.curated_dir / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.meta_dir = self.base_dir / "metadata"
        self.meta_dir.mkdir(parents=True, exist_ok=True)

        # Build baseline valid 9-year dataset fixture
        self.years_entries = {}
        self.manifest_files = {}

        # Default fixture: 2 physical Parquet rows per year.
        # DC-11 conservation: raw = 2 (accepted) + (raw_count - 2) (quarantined) + 0 (rejected)
        # This preserves physical row count conservation: physical_rows (2) == accepted_rows (2).
        for year, raw_count in sorted(CANONICAL_COUNTS.items()):
            run_id = f"run_{year}_v1"
            run_path = self.runs_dir / run_id
            run_path.mkdir(parents=True, exist_ok=True)

            parquet_f = run_path / f"part-00000-{year}.parquet"
            f_bytes, f_sha = _create_canonical_curated_parquet(parquet_f, num_rows=2)

            # Outputs declared as relative path from run_id or base
            outputs = [
                {
                    "path": f"curated/runs/{run_id}/{parquet_f.name}",
                    "bytes": f_bytes,
                    "sha256": f_sha,
                }
            ]

            accepted_c = 2
            quarantined_c = raw_count - accepted_c
            rejected_c = 0

            manifest_content = _create_production_manifest(
                run_id=run_id,
                year=year,
                raw_count=raw_count,
                accepted_count=accepted_c,
                quarantined_count=quarantined_c,
                rejected_count=rejected_c,
                status="PUBLISHED",
                outputs=outputs,
            )

            manifest_path = run_path / "run_manifest.json"
            manifest_path.write_text(json.dumps(manifest_content, indent=2), encoding="utf-8")
            self.manifest_files[year] = manifest_path

            # Also write sidecar receipt in metadata/<run_id>/
            run_meta_dir = self.meta_dir / run_id
            run_meta_dir.mkdir(parents=True, exist_ok=True)
            receipt_content = _create_production_receipt(
                run_id=run_id,
                manifest_file=manifest_path,
                row_accounting=manifest_content["row_accounting"],
                status="PUBLISHED",
            )
            (run_meta_dir / "execution_receipt.json").write_text(
                json.dumps(receipt_content, indent=2), encoding="utf-8"
            )

            self.years_entries[str(year)] = {
                "year": year,
                "selected_run_id": run_id,
                "relative_curated_path": f"curated/runs/{run_id}",
                "accounting": {
                    "raw_row_count": raw_count,
                    "accepted_row_count": accepted_c,
                    "quarantined_row_count": quarantined_c,
                    "rejected_row_count": rejected_c,
                },
                "source_coverage_status": "PARTIAL" if year == 2024 else "VERIFIED_WITH_SCOPE",
            }

        self.registry_payload = {
            "registry_version": "1.0",
            "curated_storage_root": "curated/runs",
            "years": self.years_entries,
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    # -------------------------------------------------------------------------
    # POSITIVE TEST CASES (Production Manifest & Receipt)
    # -------------------------------------------------------------------------

    def test_pos_01_complete_canonical_9year_snapshot_passes(self):
        """Verifies that an authentic 9-year snapshot with valid RunManifest and Parquet passes."""
        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            require_execution_receipt=True,
        )
        self.assertTrue(res.valid)
        self.assertEqual(res.status, "VALID_SNAPSHOT_REGISTRY")
        self.assertEqual(res.total_raw_rows, 54674003)
        self.assertEqual(res.total_accepted_rows, 18) # 9 years * 2 physical rows
        self.assertEqual(len(res.selected_paths), 9)

    def test_pos_02_valid_snapshot_with_nonzero_quarantine_rejects_passes(self):
        """Verifies DC-11 conservation with realistic non-zero quarantine and rejects."""
        # Update Year 2019
        y19 = self.years_entries["2019"]
        raw = y19["accounting"]["raw_row_count"]
        acc = 2
        quar = raw - 10
        rej = 8
        y19["accounting"]["accepted_row_count"] = acc
        y19["accounting"]["quarantined_row_count"] = quar
        y19["accounting"]["rejected_row_count"] = rej

        # Update manifest to match
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["row_accounting"]["accepted_row_count"] = acc
        m_data["row_accounting"]["quarantined_row_count"] = quar
        m_data["row_accounting"]["rejected_row_count"] = rej
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        # Update receipt to match updated manifest
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = m_path.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(m_path)
        r_data["row_accounting"] = m_data["row_accounting"]
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertTrue(res.valid)
        self.assertEqual(res.status, "VALID_SNAPSHOT_REGISTRY")

    def test_pos_03_production_runmanifest_and_receipt_integration_passes(self):
        """Verifies full integration of RunManifest.to_dict() and ExecutionReceipt.to_dict()."""
        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            require_execution_receipt=True,
        )
        self.assertTrue(res.valid)
        self.assertIsNotNone(res.annual_details[2019]["receipt_path"])
        self.assertEqual(res.annual_details[2019]["physical_parquet_rows"], 2)

    def test_pos_04_multi_version_rerun_selection_passes(self):
        """Verifies that selecting an updated rerun (v2) correctly excludes old version (v1)."""
        run_v2 = "run_2019_v2"
        run_v2_path = self.runs_dir / run_v2
        run_v2_path.mkdir(parents=True, exist_ok=True)
        pq_v2 = run_v2_path / "part-00000-2019-v2.parquet"
        v2_bytes, v2_sha = _create_canonical_curated_parquet(pq_v2, num_rows=2)

        raw = CANONICAL_COUNTS[2019]
        manifest_v2 = _create_production_manifest(
            run_id=run_v2,
            year=2019,
            raw_count=raw,
            accepted_count=2,
            quarantined_count=raw - 2,
            rejected_count=0,
            status="PUBLISHED",
            outputs=[{"path": f"curated/runs/{run_v2}/{pq_v2.name}", "bytes": v2_bytes, "sha256": v2_sha}],
        )
        manifest_v2_path = run_v2_path / "run_manifest.json"
        manifest_v2_path.write_text(json.dumps(manifest_v2, indent=2), encoding="utf-8")

        # Write execution receipt for run_v2 per Finding R01/R04
        receipt_v2 = _create_production_receipt(
            run_id=run_v2,
            manifest_file=manifest_v2_path,
            row_accounting=manifest_v2["row_accounting"],
            status="PUBLISHED",
        )
        run_v2_meta_dir = self.meta_dir / run_v2
        run_v2_meta_dir.mkdir(parents=True, exist_ok=True)
        (run_v2_meta_dir / "execution_receipt.json").write_text(
            json.dumps(receipt_v2, indent=2), encoding="utf-8"
        )

        # Update registry to point to v2
        self.years_entries["2019"]["selected_run_id"] = run_v2
        self.years_entries["2019"]["relative_curated_path"] = f"curated/runs/{run_v2}"

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertTrue(res.valid)
        self.assertEqual(res.annual_details[2019]["selected_run_id"], run_v2)

    # -------------------------------------------------------------------------
    # NEGATIVE TEST CASES (Manifest, Receipt, Schema, Accounting, Confinement)
    # -------------------------------------------------------------------------

    def test_neg_01_manifest_status_failed_fails_closed(self):
        """Finding M02: Manifest with status='FAILED' MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["status"] = "FAILED"
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MANIFEST_STATUS_NOT_PUBLISHED")

    def test_neg_02_manifest_status_missing_or_invalid_fails_closed(self):
        """Finding M01/M02: Manifest with unknown or missing status MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["status"] = "UNKNOWN_PIPELINE_STATUS"
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MANIFEST_STATUS_NOT_PUBLISHED")

    def test_neg_03_manifest_missing_configuration_years_fails_closed(self):
        """Finding M01: Manifest missing configuration.years structure MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["configuration"]["years"] = None
        m_data.pop("years", None)
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MANIFEST_YEARS_STRUCTURE_INVALID")

    def test_neg_04_manifest_year_mismatch_fails_closed(self):
        """Finding M01: Manifest declaring different year than registry MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["configuration"]["years"] = [2018]
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MANIFEST_YEAR_MISMATCH")

    def test_neg_05_manifest_run_id_mismatch_fails_closed(self):
        """Finding S01: Manifest run_id mismatching directory run_id MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["run_id"] = "run_forged_id"
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MANIFEST_RUN_ID_MISMATCH")

    def test_neg_06_manifest_missing_outputs_fails_closed(self):
        """Finding M01/M02: Manifest declaring empty outputs list MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["outputs"] = []
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MISSING_MANIFEST_OUTPUTS")

    def test_neg_07_manifest_output_hash_mismatch_fails_closed(self):
        """Finding M02: Manifest declaring fake output SHA-256 MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["outputs"][0]["sha256"] = "f" * 64
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MANIFEST_FILE_HASH_MISMATCH")

    def test_neg_08_manifest_output_byte_size_mismatch_fails_closed(self):
        """Finding M02: Manifest declaring wrong byte size MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["outputs"][0]["bytes"] = 99999999
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MANIFEST_FILE_SIZE_MISMATCH")

    def test_neg_09_output_path_traversal_fails_closed(self):
        """Finding S03/M02: Output path with traversal (..) escaping boundary MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["outputs"][0]["path"] = "../outside/part.parquet"
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "OUTPUT_PATH_TRAVERSAL_DETECTED")

    def test_neg_10_unlisted_physical_parquet_fails_closed(self):
        """Finding M02: Physical Parquet file unlisted in manifest outputs MUST fail closed."""
        extra_pf = self.runs_dir / "run_2019_v1" / "part-99999-unlisted.parquet"
        _create_canonical_curated_parquet(extra_pf, num_rows=1)

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "UNLISTED_PHYSICAL_PARQUET_DETECTED")

    def test_neg_11_parquet_physical_row_count_mismatch_fails_closed(self):
        """Finding M03: Parquet physical row count != accepted_row_count MUST fail closed."""
        # Change registry and manifest accepted_row_count to 5, while physical parquet has 2 rows
        self.years_entries["2019"]["accounting"]["accepted_row_count"] = 5
        self.years_entries["2019"]["accounting"]["quarantined_row_count"] = (
            CANONICAL_COUNTS[2019] - 5
        )

        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["row_accounting"]["accepted_row_count"] = 5
        m_data["row_accounting"]["quarantined_row_count"] = CANONICAL_COUNTS[2019] - 5
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            verify_physical_row_counts=True,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "PARQUET_PHYSICAL_ROW_COUNT_MISMATCH")

    def test_neg_12_parquet_forbidden_column_schema_fails_closed(self):
        """Finding M02: Parquet schema containing forbidden columns MUST fail closed."""
        pq_path = self.runs_dir / "run_2019_v1" / "part-00000-2019.parquet"
        b, h = _create_canonical_curated_parquet(pq_path, num_rows=2, forbidden_col="DISTANCE")

        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["outputs"][0]["bytes"] = b
        m_data["outputs"][0]["sha256"] = h
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            verify_parquet_schema=True,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "FORBIDDEN_COLUMNS_IN_PARQUET_SCHEMA")

    def test_neg_13_parquet_missing_core_measures_schema_fails_closed(self):
        """Finding M02: Parquet schema missing any of the 7 CORE measures MUST fail closed."""
        pq_path = self.runs_dir / "run_2019_v1" / "part-00000-2019.parquet"
        b, h = _create_canonical_curated_parquet(pq_path, num_rows=2, include_core_measures=False)

        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["outputs"][0]["bytes"] = b
        m_data["outputs"][0]["sha256"] = h
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            verify_parquet_schema=True,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MISSING_CORE_MEASURES_IN_PARQUET_SCHEMA")

    def test_neg_14_manifest_registry_accounting_mismatch_fails_closed(self):
        """Finding M02: Manifest accounting differing from registry accounting MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        # Manifest claims 100 accepted rows instead of 2
        m_data["row_accounting"]["accepted_row_count"] = 100
        m_data["row_accounting"]["quarantined_row_count"] = CANONICAL_COUNTS[2019] - 100
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MANIFEST_REGISTRY_ACCOUNTING_MISMATCH")

    def test_neg_15_receipt_status_not_published_fails_closed(self):
        """Finding M01/M02: ExecutionReceipt with status != PUBLISHED MUST fail closed."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["publication_status"] = "FAILED"
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            require_execution_receipt=True,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "RECEIPT_STATUS_NOT_PUBLISHED")

    def test_neg_16_receipt_manifest_sha256_mismatch_fails_closed(self):
        """Finding M02: ExecutionReceipt with manifest SHA-256 mismatch MUST fail closed."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_sha256"] = "0" * 64
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            require_execution_receipt=True,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "RECEIPT_MANIFEST_SHA256_MISMATCH")

    def test_neg_17_multiyear_run_unverified_partition_fails_closed(self):
        """Finding M02: Multi-year run declaring multiple years without partitions MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["configuration"]["years"] = [2018, 2019]
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        # Update receipt so receipt manifest check doesn't fire before partition check
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = m_path.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(m_path)
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "UNVERIFIED_MULTIYEAR_PARTITION")

    def test_neg_18_empty_run_directory_fails_closed(self):
        """Finding S01: An empty curated run directory MUST fail closed."""
        empty_dir = self.runs_dir / "run_2016_v1"
        for f in empty_dir.glob("*"):
            f.unlink()

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "EMPTY_RUN_DIRECTORY_OR_NO_PARQUET")

    def test_neg_19_fake_corrupt_parquet_fails_closed(self):
        """Finding S01: Fake 0-byte or text file renamed to .parquet MUST fail closed."""
        # Replace the real parquet file with a corrupt text file matching declared output name
        fake_p = self.runs_dir / "run_2016_v1" / "part-00000-2016.parquet"
        fake_p.write_text("this is plain text not parquet", encoding="utf-8")

        # Update manifest output bytes and sha to match fake file so it tests Thrift metadata parser
        m_path = self.manifest_files[2016]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["outputs"][0]["bytes"] = fake_p.stat().st_size
        m_data["outputs"][0]["sha256"] = compute_file_sha256(fake_p)
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        # Update receipt
        receipt_p = self.meta_dir / "run_2016_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = m_path.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(m_path)
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "CORRUPT_OR_FAKE_PARQUET_DETECTED")

    def test_neg_20_duplicate_physical_directory_fails_closed(self):
        """Finding S03: Reusing the same physical run directory across multiple years MUST fail closed."""
        self.years_entries["2017"]["relative_curated_path"] = self.years_entries["2016"]["relative_curated_path"]
        self.years_entries["2017"]["selected_run_id"] = self.years_entries["2016"]["selected_run_id"]

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "DUPLICATE_PHYSICAL_PATH")

    def test_neg_21_unbalanced_row_accounting_fails_closed(self):
        """Finding S02: Unbalanced row accounting (raw != acc + quar + rej) MUST fail closed."""
        y16 = self.years_entries["2016"]
        y16["accounting"]["accepted_row_count"] = 100
        y16["accounting"]["quarantined_row_count"] = 5
        y16["accounting"]["rejected_row_count"] = 0
        y16["accounting"]["raw_row_count"] = 200 # 200 != 105

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "UNBALANCED_ROW_ACCOUNTING")

    def test_neg_22_non_integer_row_accounting_fails_closed(self):
        """Finding S02: Boolean, float, or string row count types MUST fail closed."""
        self.years_entries["2016"]["accounting"]["accepted_row_count"] = True

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "INVALID_NUMERIC_ACCOUNTING")

    def test_neg_23_negative_row_accounting_fails_closed(self):
        """Finding S02: Negative row count values MUST fail closed."""
        self.years_entries["2016"]["accounting"]["quarantined_row_count"] = -5

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "INVALID_NUMERIC_ACCOUNTING")

    def test_neg_24_canonical_raw_row_mismatch_fails_closed(self):
        """Finding S02: Annual raw count mismatching canonical 54,674,003 baseline MUST fail closed."""
        y16 = self.years_entries["2016"]
        y16["accounting"]["raw_row_count"] = 999999
        y16["accounting"]["accepted_row_count"] = 999999
        y16["accounting"]["quarantined_row_count"] = 0
        y16["accounting"]["rejected_row_count"] = 0

        # Update manifest to match so it fails at canonical raw check
        m_path = self.manifest_files[2016]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["row_accounting"]["raw_row_count"] = 999999
        m_data["row_accounting"]["accepted_row_count"] = 999999
        m_data["row_accounting"]["quarantined_row_count"] = 0
        m_data["row_accounting"]["rejected_row_count"] = 0
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        # Update receipt so receipt manifest check doesn't fire before canonical check
        receipt_p = self.meta_dir / "run_2016_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = m_path.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(m_path)
        r_data["row_accounting"] = m_data["row_accounting"]
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            verify_physical_row_counts=False,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "CANONICAL_RAW_COUNT_MISMATCH")

    def test_neg_25_missing_required_survey_year_fails_closed(self):
        """Finding S01: Missing any survey year in 2016–2024 MUST fail closed."""
        self.years_entries.pop("2020")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "YEARS_COMPLETENESS_ERROR")

    def test_neg_26_year_2024_requires_partial_coverage_status_fails_closed(self):
        """Finding S02: Year 2024 must declare source_coverage_status = 'PARTIAL' (OR-05)."""
        self.years_entries["2024"]["source_coverage_status"] = "FULL"

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "OR05_COVERAGE_STATUS_VIOLATION")

    def test_neg_27_path_traversal_curated_runs_escape_fails_closed(self):
        """Finding S03: Path attempting escape outside curated/runs MUST fail closed."""
        self.years_entries["2016"]["relative_curated_path"] = "curated/runs/../../outside"

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "PATH_TRAVERSAL_DETECTED")

    # -------------------------------------------------------------------------
    # FINDING R01 REGRESSION TESTS (Receipt Optionality Enforced Fail-Closed)
    # -------------------------------------------------------------------------
    def test_neg_r01a_missing_execution_receipt_fails_closed(self):
        """Finding R01: Missing execution receipt must fail closed with MISSING_EXECUTION_RECEIPT by default."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        if receipt_p.exists():
            receipt_p.unlink()

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MISSING_EXECUTION_RECEIPT")

    def test_neg_r01b_diagnostic_mode_missing_receipt_never_yields_production_pass(self):
        """Finding R01: Diagnostic mode without receipt never returns VALID_SNAPSHOT_REGISTRY."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        if receipt_p.exists():
            receipt_p.unlink()

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            require_execution_receipt=False,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "DIAGNOSTIC_PASS_RECEIPT_OMITTED_NOT_FOR_PRODUCTION")

    # -------------------------------------------------------------------------
    # FINDING R02 REGRESSION TESTS (Output Path Identity & Confinement)
    # -------------------------------------------------------------------------
    def test_neg_r02a_cross_run_output_path_fails_closed(self):
        """Finding R02: Manifest output referencing another run directory MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        # Add output pointing to run_2020_v1 instead of run_2019_v1
        m_data["outputs"] = [
            {
                "path": "curated/runs/run_2020_v1/part-00000-2019.parquet",
                "bytes": 100,
                "sha256": "a" * 64,
            }
        ]
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "OUTPUT_PATH_RUN_MISMATCH")

    def test_neg_r02b_duplicate_output_entry_fails_closed(self):
        """Finding R02: Duplicate output entries in manifest outputs MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        orig_out = m_data["outputs"][0]
        m_data["outputs"] = [orig_out, orig_out]
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "DUPLICATE_OUTPUT_ENTRY")

    def test_pos_r02c_subpartition_distinct_basenames_passes(self):
        """Finding R02: Subpartitions with same basename in different directories pass without collision."""
        run_path = self.runs_dir / "run_2019_v1"
        for f in run_path.glob("*.parquet"):
            f.unlink()

        q1_dir = run_path / "quarter=1"
        q2_dir = run_path / "quarter=2"
        q1_dir.mkdir(parents=True, exist_ok=True)
        q2_dir.mkdir(parents=True, exist_ok=True)

        pq1 = q1_dir / "part-0.parquet"
        pq2 = q2_dir / "part-0.parquet"
        b1, s1 = _create_canonical_curated_parquet(pq1, num_rows=1)
        b2, s2 = _create_canonical_curated_parquet(pq2, num_rows=1)

        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["outputs"] = [
            {"path": f"curated/runs/run_2019_v1/quarter=1/{pq1.name}", "bytes": b1, "sha256": s1},
            {"path": f"curated/runs/run_2019_v1/quarter=2/{pq2.name}", "bytes": b2, "sha256": s2},
        ]
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = m_path.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(m_path)
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertTrue(res.valid)
        self.assertEqual(res.status, "VALID_SNAPSHOT_REGISTRY")

    def test_neg_r02d_subpartition_path_mismatch_fails_closed(self):
        """Finding R02: Subpartition path declared in manifest missing from disk fails closed."""
        run_path = self.runs_dir / "run_2019_v1"
        for f in run_path.glob("*.parquet"):
            f.unlink()

        q1_dir = run_path / "quarter=1"
        q1_dir.mkdir(parents=True, exist_ok=True)
        pq1 = q1_dir / "part-0.parquet"
        b1, s1 = _create_canonical_curated_parquet(pq1, num_rows=2)

        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        m_data["outputs"] = [
            {"path": f"curated/runs/run_2019_v1/quarter=2/part-0.parquet", "bytes": b1, "sha256": s1},
        ]
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertIn(res.status, ("UNLISTED_PHYSICAL_PARQUET_DETECTED", "MANIFEST_FILE_NOT_FOUND"))

    # -------------------------------------------------------------------------
    # FINDING R03 REGRESSION TESTS (Missing Output Hash and Size)
    # -------------------------------------------------------------------------
    def test_neg_r03a_missing_output_bytes_fails_closed(self):
        """Finding R03: Manifest output missing 'bytes' field MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        del m_data["outputs"][0]["bytes"]
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MISSING_OUTPUT_BYTES")

    def test_neg_r03b_invalid_output_bytes_types_fail_closed(self):
        """Finding R03: Output 'bytes' as bool, negative int, or str MUST fail closed."""
        m_path = self.manifest_files[2019]
        for bad_val in [True, False, -10, "1024"]:
            m_data = json.loads(m_path.read_text(encoding="utf-8"))
            m_data["outputs"][0]["bytes"] = bad_val
            m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

            res = validate_multiyear_snapshot_registry(
                registry_data=self.registry_payload,
                base_data_dir=self.base_dir,
            )
            self.assertFalse(res.valid, f"Expected fail for bytes={bad_val!r}")
            self.assertEqual(res.status, "INVALID_OUTPUT_BYTES_METADATA")

    def test_neg_r03c_missing_output_sha256_fails_closed(self):
        """Finding R03: Manifest output missing 'sha256' field MUST fail closed."""
        m_path = self.manifest_files[2019]
        m_data = json.loads(m_path.read_text(encoding="utf-8"))
        del m_data["outputs"][0]["sha256"]
        m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MISSING_OUTPUT_SHA256")

    def test_neg_r03d_placeholder_output_sha256_fails_closed(self):
        """Finding R03: Output sha256 with placeholders ('PENDING', 'UNVERIFIED', '') MUST fail closed."""
        m_path = self.manifest_files[2019]
        for placeholder in ["PENDING", "UNVERIFIED", "", "   "]:
            m_data = json.loads(m_path.read_text(encoding="utf-8"))
            m_data["outputs"][0]["sha256"] = placeholder
            m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

            res = validate_multiyear_snapshot_registry(
                registry_data=self.registry_payload,
                base_data_dir=self.base_dir,
            )
            self.assertFalse(res.valid, f"Expected fail for sha256={placeholder!r}")
            self.assertEqual(res.status, "INVALID_OUTPUT_SHA256_METADATA")

    def test_neg_r03e_invalid_hex_sha256_fails_closed(self):
        """Finding R03: Output sha256 with non-hex or invalid length MUST fail closed."""
        m_path = self.manifest_files[2019]
        for bad_hash in ["g" * 64, "a" * 63, "a" * 65, "not_a_hash"]:
            m_data = json.loads(m_path.read_text(encoding="utf-8"))
            m_data["outputs"][0]["sha256"] = bad_hash
            m_path.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

            res = validate_multiyear_snapshot_registry(
                registry_data=self.registry_payload,
                base_data_dir=self.base_dir,
            )
            self.assertFalse(res.valid, f"Expected fail for sha256={bad_hash!r}")
            self.assertEqual(res.status, "INVALID_OUTPUT_SHA256_METADATA")

    def test_neg_r03f_disabled_checksum_verification_cannot_yield_production_pass(self):
        """Finding R03: Disabled checksum verification returns NON_PRODUCTION_CHECKSUM_SKIPPED."""
        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
            verify_file_checksums=False,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "NON_PRODUCTION_CHECKSUM_SKIPPED")

    # -------------------------------------------------------------------------
    # FINDING R04 REGRESSION TESTS (Receipt Fields Missing But Accepted)
    # -------------------------------------------------------------------------
    def test_neg_r04a_receipt_missing_task_id_fails_closed(self):
        """Finding R04: Receipt missing or empty 'task_id' MUST fail closed."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        del r_data["task_id"]
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "RECEIPT_FIELD_MISSING")

    def test_neg_r04b_receipt_missing_manifest_bytes_fails_closed(self):
        """Finding R04: Receipt missing 'manifest_bytes' MUST fail closed."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        del r_data["manifest_bytes"]
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "RECEIPT_FIELD_MISSING")

    def test_neg_r04c_receipt_missing_manifest_sha256_fails_closed(self):
        """Finding R04: Receipt missing or invalid 'manifest_sha256' MUST fail closed."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        del r_data["manifest_sha256"]
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "RECEIPT_FIELD_MISSING")

    def test_neg_r04d_receipt_published_path_mismatch_fails_closed(self):
        """Finding R04: Receipt published_path pointing to wrong run MUST fail closed."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["published_path"] = "curated/runs/run_2020_v1"
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "RECEIPT_PUBLISHED_PATH_MISMATCH")

    def test_neg_r04e_receipt_manifest_path_mismatch_fails_closed(self):
        """Finding R04: Receipt manifest_path pointing to wrong manifest MUST fail closed."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_path"] = "curated/runs/run_2020_v1/run_manifest.json"
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "RECEIPT_MANIFEST_PATH_MISMATCH")

    def test_neg_r04f_receipt_row_accounting_missing_or_mismatch_fails_closed(self):
        """Finding R04: Receipt row_accounting missing or mismatching manifest MUST fail closed."""
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"

        # Case 1: missing row_accounting
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        del r_data["row_accounting"]
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "RECEIPT_FIELD_MISSING")

        # Case 2: mismatching row count
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["row_accounting"] = {
            "raw_row_count": CANONICAL_COUNTS[2019],
            "accepted_row_count": 9999,
            "quarantined_row_count": CANONICAL_COUNTS[2019] - 9999,
            "rejected_row_count": 0,
        }
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "RECEIPT_ROW_ACCOUNTING_MISMATCH")

    # -------------------------------------------------------------------------
    # FINDING R05: Deep Recursive Parquet Discovery Tests
    # -------------------------------------------------------------------------

    def test_neg_r05a_unlisted_deep_partition_parquet_fails_closed(self):
        """Finding R05: Parquet in nested partition unlisted in manifest outputs MUST fail closed."""
        sub_dir = self.runs_dir / "run_2019_v1" / "nested_partition"
        sub_dir.mkdir(parents=True, exist_ok=True)
        unlisted_parquet = sub_dir / "unlisted.parquet"
        _create_canonical_curated_parquet(unlisted_parquet, num_rows=1)

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "UNLISTED_PHYSICAL_PARQUET_DETECTED")
        self.assertIn("unlisted.parquet", res.error_message)

    def test_neg_r05b_manifest_declares_deep_parquet_missing_from_disk_fails_closed(self):
        """Finding R05: Manifest declares nested parquet that does NOT exist on disk MUST fail closed."""
        manifest_p = self.manifest_files[2019]
        m_data = json.loads(manifest_p.read_text(encoding="utf-8"))
        m_data["outputs"].append({
            "path": "curated/runs/run_2019_v1/deep/sub/missing.parquet",
            "bytes": 1024,
            "sha256": "e" * 64,
        })
        manifest_p.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        # Update receipt so it matches manifest SHA and bytes
        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = manifest_p.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(manifest_p)
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MANIFEST_FILE_NOT_FOUND")

    def test_pos_r05c_multilevel_partition_hierarchy_passes(self):
        """Finding R05: Multi-level partition hierarchy (year=2019/month=X) passes when declared."""
        run_p = self.runs_dir / "run_2019_v1"
        # Remove root parquet
        root_parquets = list(run_p.glob("*.parquet"))
        for p in root_parquets:
            p.unlink()

        part1_dir = run_p / "year=2019" / "month=1"
        part2_dir = run_p / "year=2019" / "month=2"
        part1_dir.mkdir(parents=True, exist_ok=True)
        part2_dir.mkdir(parents=True, exist_ok=True)

        f1 = part1_dir / "part-00000.parquet"
        f2 = part2_dir / "part-00001.parquet"
        b1, s1 = _create_canonical_curated_parquet(f1, num_rows=1)
        b2, s2 = _create_canonical_curated_parquet(f2, num_rows=1)

        manifest_p = self.manifest_files[2019]
        m_data = json.loads(manifest_p.read_text(encoding="utf-8"))
        m_data["outputs"] = [
            {"path": f"curated/runs/run_2019_v1/year=2019/month=1/{f1.name}", "bytes": b1, "sha256": s1},
            {"path": f"curated/runs/run_2019_v1/year=2019/month=2/{f2.name}", "bytes": b2, "sha256": s2},
        ]
        manifest_p.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = manifest_p.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(manifest_p)
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertTrue(res.valid)
        self.assertEqual(res.status, "VALID_SNAPSHOT_REGISTRY")

    def test_pos_r05d_mixed_root_and_deep_parquet_passes(self):
        """Finding R05: Mixed root and nested partition parquets pass when all declared."""
        run_p = self.runs_dir / "run_2018_v1"
        root_parquets = list(run_p.glob("*.parquet"))
        for p in root_parquets:
            p.unlink()

        f_root = run_p / "part-root.parquet"
        sub_dir = run_p / "subpartition"
        sub_dir.mkdir(parents=True, exist_ok=True)
        f_sub = sub_dir / "part-sub.parquet"

        b_root, s_root = _create_canonical_curated_parquet(f_root, num_rows=1)
        b_sub, s_sub = _create_canonical_curated_parquet(f_sub, num_rows=1)

        manifest_p = self.manifest_files[2018]
        m_data = json.loads(manifest_p.read_text(encoding="utf-8"))
        m_data["outputs"] = [
            {"path": f"curated/runs/run_2018_v1/{f_root.name}", "bytes": b_root, "sha256": s_root},
            {"path": f"curated/runs/run_2018_v1/subpartition/{f_sub.name}", "bytes": b_sub, "sha256": s_sub},
        ]
        manifest_p.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        receipt_p = self.meta_dir / "run_2018_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = manifest_p.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(manifest_p)
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertTrue(res.valid)
        self.assertEqual(res.status, "VALID_SNAPSHOT_REGISTRY")

    def test_neg_r05e_deep_partition_row_count_mismatch_fails_closed(self):
        """Finding R05: Deep partition parquet row count mismatch fails closed."""
        run_p = self.runs_dir / "run_2019_v1"
        root_parquets = list(run_p.glob("*.parquet"))
        for p in root_parquets:
            p.unlink()

        deep_dir = run_p / "deep_folder"
        deep_dir.mkdir(parents=True, exist_ok=True)
        f_deep = deep_dir / "part-000.parquet"
        # 5 physical rows on disk instead of 2
        b_deep, s_deep = _create_canonical_curated_parquet(f_deep, num_rows=5)

        manifest_p = self.manifest_files[2019]
        m_data = json.loads(manifest_p.read_text(encoding="utf-8"))
        m_data["outputs"] = [
            {"path": f"curated/runs/run_2019_v1/deep_folder/{f_deep.name}", "bytes": b_deep, "sha256": s_deep}
        ]
        # accepted_row_count is still 2 in manifest and registry
        manifest_p.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        receipt_p = self.meta_dir / "run_2019_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = manifest_p.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(manifest_p)
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_multiyear_snapshot_registry(
            registry_data=self.registry_payload,
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "PARQUET_PHYSICAL_ROW_COUNT_MISMATCH")

    def test_neg_r05f_symlink_or_reparse_point_in_hierarchy_fails_closed(self):
        """Finding R05: Symlink or reparse point detected in parquet hierarchy fails closed."""
        from unittest.mock import patch
        with patch("verify_multiyear_snapshot.is_symlink_or_reparse") as mock_sym:
            # Let root pass, but flag any subfolder
            mock_sym.side_effect = lambda p: "run_2019_v1" in str(p) and "sym_flag" in str(p)
            fake_dir = self.runs_dir / "run_2019_v1" / "sym_flag"
            fake_dir.mkdir(parents=True, exist_ok=True)
            files, err_status, err_msg = discover_physical_parquet_files(self.runs_dir / "run_2019_v1")
            self.assertIsNone(files)
            self.assertEqual(err_status, "UNSAFE_SYMLINK_DETECTED")

    # -------------------------------------------------------------------------
    # FINDINGS E01 & E02: Single Annual Run Verification Tests
    # -------------------------------------------------------------------------

    def test_pos_e02a_valid_single_annual_run_passes(self):
        """Finding E02: validate_single_annual_run succeeds on an authentic single-year execution run."""
        res = validate_single_annual_run(
            year=2016,
            run_id="run_2016_v1",
            base_data_dir=self.base_dir,
            require_execution_receipt=True,
        )
        self.assertTrue(res.valid)
        self.assertEqual(res.status, "VALID_SINGLE_RUN_ANNUAL_BATCH")
        self.assertEqual(res.total_raw_rows, CANONICAL_COUNTS[2016])
        self.assertEqual(res.total_accepted_rows, 2)

    def test_neg_e02b_single_annual_run_row_mismatch_fails_closed(self):
        """Finding E01 & E02: Single-run verification fails if raw rows mismatch canonical audited baseline."""
        manifest_p = self.manifest_files[2016]
        m_data = json.loads(manifest_p.read_text(encoding="utf-8"))
        # Inject old typo count: 5617658 instead of canonical 5537987
        m_data["row_accounting"]["raw_row_count"] = 5617658
        m_data["row_accounting"]["quarantined_row_count"] = 5617658 - 2
        manifest_p.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

        receipt_p = self.meta_dir / "run_2016_v1" / "execution_receipt.json"
        r_data = json.loads(receipt_p.read_text(encoding="utf-8"))
        r_data["manifest_bytes"] = manifest_p.stat().st_size
        r_data["manifest_sha256"] = compute_file_sha256(manifest_p)
        r_data["row_accounting"] = m_data["row_accounting"]
        receipt_p.write_text(json.dumps(r_data, indent=2), encoding="utf-8")

        res = validate_single_annual_run(
            year=2016,
            run_id="run_2016_v1",
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "CANONICAL_RAW_COUNT_MISMATCH")

    def test_neg_e02c_single_annual_run_missing_receipt_fails_closed(self):
        """Finding E02: Single-run verification fails if execution receipt is missing."""
        receipt_p = self.meta_dir / "run_2016_v1" / "execution_receipt.json"
        receipt_p.unlink()

        res = validate_single_annual_run(
            year=2016,
            run_id="run_2016_v1",
            base_data_dir=self.base_dir,
            require_execution_receipt=True,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "MISSING_EXECUTION_RECEIPT")

    def test_neg_e02d_single_annual_run_unlisted_deep_parquet_fails_closed(self):
        """Finding E02 & R05: Single-run verification detects unlisted nested parquet and fails closed."""
        sub_dir = self.runs_dir / "run_2016_v1" / "nested_dir"
        sub_dir.mkdir(parents=True, exist_ok=True)
        unlisted = sub_dir / "leak.parquet"
        _create_canonical_curated_parquet(unlisted, num_rows=1)

        res = validate_single_annual_run(
            year=2016,
            run_id="run_2016_v1",
            base_data_dir=self.base_dir,
        )
        self.assertFalse(res.valid)
        self.assertEqual(res.status, "UNLISTED_PHYSICAL_PARQUET_DETECTED")


class TestFindingE03CoordinatorCLI(unittest.TestCase):
    def test_coordinator_cli_help(self):
        """Finding E03: CLI --help exits cleanly with code 0."""
        with self.assertRaises(SystemExit) as ctx:
            coordinator_main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_coordinator_cli_dry_run_preflight(self):
        """Finding E03: CLI --dry-run-preflight completes preflight check and exits 0."""
        code = coordinator_main(["--years", "2016", "--run-id", "run_dry_run_preflight_test", "--dry-run-preflight", "--base-data-dir", "data"])
        self.assertEqual(code, 0)

    def test_coordinator_cli_live_run_blocked_by_d5(self):
        """Finding E03: CLI live execution without D5 approval exits 1 under governance hold."""
        code = coordinator_main(["--years", "2016", "--run-id", "run_2016_v1", "--base-data-dir", "data"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
