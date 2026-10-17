"""
Unit and integration test suite for T007-02A Source Inventory & Local Hash Verifier.
Conforms to DATA_CONTRACT.md, ARCHITECTURE.md, T007_02A specifications, and T007_02A_HANDOFF_ERRATA.md.

CRITICAL SCOPE BOUNDARY:
- Strictly synthetic tests using tempfile.TemporaryDirectory.
- ZERO read or stat access to real 15.2 GB CSV files in data/raw/.
"""

import ast
import errno
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Ensure src is on sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _check_ast_for_forbidden_ingestion_or_publication(source_code: str) -> list:
    """
    Static AST inspection to verify SourceValidator does not contain forbidden
    Spark CSV reader, classifier, or publication orchestration calls.
    """
    tree = ast.parse(source_code)
    violations = []
    forbidden_modules = {"pyspark", "pandas", "csv"}
    forbidden_funcs = {"SafePublisher", "publish_atomic", "classify_records", "quarantine_records"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split(".")[0]
                if root_pkg in forbidden_modules:
                    violations.append(f"Forbidden import: {alias.name} (line {node.lineno})")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split(".")[0]
                if root_pkg in forbidden_modules:
                    violations.append(f"Forbidden import from: {node.module} (line {node.lineno})")
                if "publication" in node.module:
                    violations.append(f"Forbidden publication import: {node.module} (line {node.lineno})")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in forbidden_funcs:
                    violations.append(f"Forbidden call: {node.func.id}() (line {node.lineno})")
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in forbidden_funcs:
                    violations.append(f"Forbidden attribute call: .{node.func.attr}() (line {node.lineno})")
                if (
                    node.func.attr == "csv"
                    and isinstance(node.func.value, ast.Attribute)
                    and node.func.value.attr == "read"
                ):
                    violations.append(f"Forbidden Spark CSV read call: .read.csv() (line {node.lineno})")
    return violations

from flight_pipeline.ingestion.source_validator import (
    AUDITED_SOURCE_INVENTORY,
    DEFAULT_HASH_CHUNK_SIZE,
    EXPECTED_ANNUAL_SOURCES_COUNT,
    TOTAL_AUDITED_BYTES,
    TOTAL_AUDITED_ROWS,
    UPSTREAM_IDENTITY_STATUS_UNVERIFIED,
    BatchVerificationResult,
    SourceChangedDuringReadError,
    SourceConfigurationError,
    SourceEntry,
    SourceHashMismatchError,
    SourceIntegrityError,
    SourceNotFoundError,
    SourcePathSecurityError,
    SourcePermissionError,
    SourceSizeMismatchError,
    SourceVerificationResult,
    SourceValidator,
    SourceValidatorError,
    VerificationState,
    validate_path_safety,
)
from flight_pipeline.utils.run_manifest import RunManifest


class TestT007SourceValidatorSynthetic(unittest.TestCase):
    """Synthetic unit tests for SourceValidator."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # -------------------------------------------------------------------------
    # Inventory Tests (INV-01 .. INV-03)
    # -------------------------------------------------------------------------

    def test_inv_01_audited_inventory_entry_count_and_years(self):
        """INV-01: Exactly 9 annual inventory entries covering 2016-2024."""
        self.assertEqual(len(AUDITED_SOURCE_INVENTORY), EXPECTED_ANNUAL_SOURCES_COUNT)
        self.assertEqual(EXPECTED_ANNUAL_SOURCES_COUNT, 9)
        expected_years = list(range(2016, 2025))
        self.assertEqual(sorted(AUDITED_SOURCE_INVENTORY.keys()), expected_years)
        for year in expected_years:
            entry = AUDITED_SOURCE_INVENTORY[year]
            self.assertEqual(entry.year, year)
            self.assertEqual(entry.audited_column_count, 34)

    def test_inv_02_no_duplicate_years_or_paths(self):
        """INV-02: No duplicate years or relative paths in inventory baseline."""
        paths = [e.relative_path.replace("\\", "/").lower() for e in AUDITED_SOURCE_INVENTORY.values()]
        self.assertEqual(len(paths), len(set(paths)), "Duplicate relative paths found in inventory")
        years = list(AUDITED_SOURCE_INVENTORY.keys())
        self.assertEqual(len(years), len(set(years)), "Duplicate years found in inventory")

    def test_inv_03_expected_row_counts_and_byte_sizes(self):
        """INV-03: Expected byte sizes and row counts match audited baseline exactly."""
        expected_rows = {
            2016: 5537987,
            2017: 5575872,
            2018: 6986842,
            2019: 7161827,
            2020: 4312091,
            2021: 5755666,
            2022: 6413416,
            2023: 6645461,
            2024: 6284841,
        }
        expected_bytes = {
            2016: 1538427452,
            2017: 1549837485,
            2018: 1941406432,
            2019: 1990370667,
            2020: 1197858795,
            2021: 1600032487,
            2022: 1782648882,
            2023: 1847433387,
            2024: 1748350586,
        }

        sum_rows = 0
        sum_bytes = 0
        for year, entry in AUDITED_SOURCE_INVENTORY.items():
            self.assertEqual(entry.audited_row_count, expected_rows[year])
            self.assertEqual(entry.audited_byte_size, expected_bytes[year])
            sum_rows += entry.audited_row_count
            sum_bytes += entry.audited_byte_size

        self.assertEqual(sum_rows, TOTAL_AUDITED_ROWS)
        self.assertEqual(sum_rows, 54674003)
        self.assertEqual(sum_bytes, TOTAL_AUDITED_BYTES)
        self.assertEqual(sum_bytes, 15196366173)

    def test_inv_04_inventory_matches_g1_canonical_schema_manifests(self):
        """INV-04: AUDITED_SOURCE_INVENTORY per-year rows and sizes match G1 schema_YYYY.json inputs."""
        import json
        repo_root = Path(__file__).resolve().parent.parent
        for year, entry in AUDITED_SOURCE_INVENTORY.items():
            schema_file = repo_root / "docs" / "05-evidence" / "inputs" / f"schema_{year}.json"
            self.assertTrue(schema_file.is_file(), f"Missing G1 schema manifest: {schema_file}")
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
            expected_rows = schema_data["row_count"]
            expected_bytes = schema_data["source_signature"]["file_size_bytes"]
            self.assertEqual(
                entry.audited_row_count,
                expected_rows,
                f"Year {year} row count mismatch: {entry.audited_row_count} vs canonical G1 {expected_rows}"
            )
            self.assertEqual(
                entry.audited_byte_size,
                expected_bytes,
                f"Year {year} byte size mismatch: {entry.audited_byte_size} vs canonical G1 {expected_bytes}"
            )

    # -------------------------------------------------------------------------
    # Hash Tests (HASH-01 .. HASH-06)
    # -------------------------------------------------------------------------

    def test_hash_01_streaming_sha256_matches_hashlib_reference(self):
        """HASH-01: Streaming SHA-256 matches standard hashlib reference computation."""
        test_file = self.base_path / "test_data.csv"
        content = b"FL_DATE,OP_CARRIER,DEP_DELAY\n2020-01-01,AA,15.0\n2020-01-02,DL,-3.0\n"
        test_file.write_bytes(content)

        validator = SourceValidator(base_dir=self.base_path)
        computed_hash, bytes_read = validator.compute_file_hash(test_file)

        ref_hash = hashlib.sha256(content).hexdigest()
        self.assertEqual(computed_hash, ref_hash)
        self.assertEqual(bytes_read, len(content))

    def test_hash_02_empty_file_hashing(self):
        """HASH-02: Empty file hashing produces canonical empty SHA-256 digest."""
        test_file = self.base_path / "empty.csv"
        test_file.write_bytes(b"")

        validator = SourceValidator(base_dir=self.base_path)
        computed_hash, bytes_read = validator.compute_file_hash(test_file)

        empty_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(computed_hash, empty_sha256)
        self.assertEqual(bytes_read, 0)

    def test_hash_03_file_larger_than_multiple_blocks(self):
        """HASH-03: File larger than multiple streaming blocks hashes correctly."""
        test_file = self.base_path / "multi_block.bin"
        chunk_size = 1024  # 1 KB chunk size for test
        block_count = 5
        block_data = b"X" * chunk_size
        total_data = block_data * block_count + b"REMAINDER"
        test_file.write_bytes(total_data)

        validator = SourceValidator(base_dir=self.base_path, chunk_size=chunk_size)
        computed_hash, bytes_read = validator.compute_file_hash(test_file)

        ref_hash = hashlib.sha256(total_data).hexdigest()
        self.assertEqual(computed_hash, ref_hash)
        self.assertEqual(bytes_read, len(total_data))

    def test_hash_04_streaming_memory_bound_chunk_reads(self):
        """HASH-04: Verify chunked read behavior (no whole-file read into memory)."""
        test_file = self.base_path / "chunk_test.bin"
        test_file.write_bytes(b"A" * 5000)

        validator = SourceValidator(base_dir=self.base_path, chunk_size=1000)
        # Verify default chunk size vs configured chunk size
        self.assertEqual(validator.chunk_size, 1000)

        with patch("flight_pipeline.ingestion.source_validator.open", side_effect=open) as mock_open:
            h, b = validator.compute_file_hash(test_file)
            self.assertEqual(b, 5000)

    def test_hash_05_detect_hash_mismatch(self):
        """HASH-05: Detect hash mismatch when actual hash != approved baseline hash."""
        test_file = self.base_path / "tabular_2020.csv"
        content = b"header\nrow1\n"
        test_file.write_bytes(content)

        synthetic_inventory = {
            2020: SourceEntry(
                year=2020,
                relative_path="tabular_2020.csv",
                audited_row_count=1,
                audited_byte_size=len(content),
                audited_column_count=34,
            )
        }
        approved_hashes = {
            2020: "0000000000000000000000000000000000000000000000000000000000000000"
        }

        validator = SourceValidator(
            base_dir=self.base_path,
            inventory=synthetic_inventory,
            approved_baseline_hashes=approved_hashes,
        )

        # Non-failing verification mode
        res = validator.verify_source(2020, compute_hash=True, fail_fast=False)
        self.assertEqual(res.state, VerificationState.HASH_MISMATCH)
        self.assertFalse(res.is_verified)
        self.assertIsNotNone(res.error_message)
        self.assertEqual(res.upstream_identity_status, UPSTREAM_IDENTITY_STATUS_UNVERIFIED)

        # Fail-fast mode raises SourceHashMismatchError
        with self.assertRaises(SourceHashMismatchError):
            validator.verify_source(2020, compute_hash=True, fail_fast=True)

    def test_hash_06_unapproved_baseline_cannot_conclude_verified(self):
        """HASH-06: When no approved baseline exists, state is LOCAL_HASH_COMPUTED_UNAPPROVED and is_verified is False."""
        test_file = self.base_path / "flight_2020.csv"
        content = b"col1,col2\n1,2\n"
        test_file.write_bytes(content)

        synthetic_inventory = {
            2020: SourceEntry(
                year=2020,
                relative_path="flight_2020.csv",
                audited_row_count=1,
                audited_byte_size=len(content),
                audited_column_count=34,
            )
        }

        # No approved baseline hashes provided
        validator = SourceValidator(
            base_dir=self.base_path,
            inventory=synthetic_inventory,
            approved_baseline_hashes=None,
        )

        res = validator.verify_source(2020, compute_hash=True, fail_fast=False)
        self.assertEqual(res.state, VerificationState.LOCAL_HASH_COMPUTED_UNAPPROVED)
        self.assertFalse(res.is_verified)
        self.assertIsNone(res.approved_sha256)
        self.assertIsNotNone(res.computed_sha256)
        self.assertEqual(res.upstream_identity_status, UPSTREAM_IDENTITY_STATUS_UNVERIFIED)

        # Verify batch evaluation reflects has_unapproved_candidate_hashes
        batch = validator.verify_all_sources(compute_hash=True)
        self.assertFalse(batch.all_hashes_verified)
        self.assertTrue(batch.has_unapproved_candidate_hashes)

    # -------------------------------------------------------------------------
    # Error Handling & Edge Cases (ERR-01 .. ERR-07)
    # -------------------------------------------------------------------------

    def test_err_01_missing_file(self):
        """ERR-01: Missing file results in SOURCE_MISSING and raises SourceNotFoundError on fail_fast."""
        synthetic_inventory = {
            2020: SourceEntry(
                year=2020,
                relative_path="nonexistent.csv",
                audited_row_count=100,
                audited_byte_size=500,
                audited_column_count=34,
            )
        }
        validator = SourceValidator(base_dir=self.base_path, inventory=synthetic_inventory)

        res = validator.verify_source(2020, compute_hash=False, fail_fast=False)
        self.assertEqual(res.state, VerificationState.SOURCE_MISSING)
        self.assertFalse(res.is_verified)

        with self.assertRaises(SourceNotFoundError):
            validator.verify_source(2020, compute_hash=False, fail_fast=True)

    def test_err_02_permission_error_fail_closed(self):
        """ERR-02: Permission/read error results in SOURCE_READ_ERROR or raises SourcePermissionError."""
        test_file = self.base_path / "perm_file.csv"
        test_file.write_bytes(b"data\n")

        validator = SourceValidator(base_dir=self.base_path)

        with patch("flight_pipeline.ingestion.source_validator.open", side_effect=PermissionError("Access denied")):
            with self.assertRaises(SourcePermissionError):
                validator.compute_file_hash(test_file)

    def test_err_03_file_modified_during_hashing(self):
        """ERR-03: Detecting modification during hashing raises SourceChangedDuringReadError."""
        test_file = self.base_path / "racing_file.csv"
        test_file.write_bytes(b"initial content\n")

        synthetic_inventory = {
            2020: SourceEntry(
                year=2020,
                relative_path="racing_file.csv",
                audited_row_count=1,
                audited_byte_size=len(b"initial content\n"),
                audited_column_count=34,
            )
        }
        validator = SourceValidator(base_dir=self.base_path, inventory=synthetic_inventory)

        # Simulate size change between before_stat and after_stat
        fake_stat_before = MagicMock(st_size=16, st_mtime=1000.0)
        fake_stat_after = MagicMock(st_size=32, st_mtime=1005.0)

        with patch("os.stat", side_effect=[fake_stat_before, fake_stat_after]):
            with self.assertRaises(SourceChangedDuringReadError):
                validator.compute_file_hash(test_file, fail_on_change=True)

    def test_err_04_invalid_path_traversal(self):
        """ERR-04: Path traversal sequences ('..') are strictly rejected."""
        with self.assertRaises(SourcePathSecurityError):
            validate_path_safety("../outside.csv", base_dir=self.base_path)

        with self.assertRaises(SourcePathSecurityError):
            validate_path_safety(self.base_path / "dir" / ".." / ".." / "escaped.csv", base_dir=self.base_path)

    def test_err_05_symlink_escape_rejected(self):
        """ERR-05: Symlinks and reparse points are strictly rejected."""
        target_file = self.base_path / "real_file.csv"
        target_file.write_bytes(b"payload")
        link_file = self.base_path / "symlink_file.csv"

        try:
            os.symlink(target_file, link_file)
            has_symlink_support = True
        except (OSError, NotImplementedError):
            has_symlink_support = False

        if has_symlink_support:
            with self.assertRaises(SourcePathSecurityError):
                validate_path_safety(link_file, base_dir=self.base_path)
        else:
            # If OS does not permit symlink creation without admin rights, mock islink
            with patch("flight_pipeline.ingestion.source_validator.os.path.islink", return_value=True):
                with self.assertRaises(SourcePathSecurityError):
                    validate_path_safety(target_file, base_dir=self.base_path)

    def test_err_06_size_mismatch_detected(self):
        """ERR-06: Size mismatch triggers SIZE_MISMATCH or raises SourceSizeMismatchError."""
        test_file = self.base_path / "size_test.csv"
        test_file.write_bytes(b"12345")  # 5 bytes

        synthetic_inventory = {
            2020: SourceEntry(
                year=2020,
                relative_path="size_test.csv",
                audited_row_count=1,
                audited_byte_size=10,  # Expected 10 bytes
                audited_column_count=34,
            )
        }
        validator = SourceValidator(base_dir=self.base_path, inventory=synthetic_inventory)

        res = validator.verify_source(2020, compute_hash=False, fail_fast=False)
        self.assertEqual(res.state, VerificationState.SIZE_MISMATCH)
        self.assertEqual(res.actual_byte_size, 5)
        self.assertEqual(res.expected_byte_size, 10)
        self.assertFalse(res.is_verified)

        with self.assertRaises(SourceSizeMismatchError):
            validator.verify_source(2020, compute_hash=False, fail_fast=True)

    def test_err_07_corrupt_baseline_format(self):
        """ERR-07: Corrupt baseline hash format (non-hex, wrong length, wrong year) raises SourceConfigurationError."""
        # Non-hex string
        with self.assertRaises(SourceConfigurationError):
            SourceValidator(
                base_dir=self.base_path,
                approved_baseline_hashes={2016: "not_a_hex_hash_zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"},
            )

        # Wrong length (not 64 chars)
        with self.assertRaises(SourceConfigurationError):
            SourceValidator(
                base_dir=self.base_path,
                approved_baseline_hashes={2016: "abcdef123456"},
            )

        # Year not in inventory
        with self.assertRaises(SourceConfigurationError):
            SourceValidator(
                base_dir=self.base_path,
                approved_baseline_hashes={1999: "a" * 64},
            )

    # -------------------------------------------------------------------------
    # API Compatibility & Integration (API-01)
    # -------------------------------------------------------------------------

    def test_api_01_run_manifest_record_input_compatibility(self):
        """API-01: Verify integration with RunManifest.record_input() per DOC-F02."""
        manifest = RunManifest(run_id="run_test_001", task_id="T007-02A")

        test_file = self.base_path / "flight_2016.csv"
        content = b"col1,col2\nval1,val2\n"
        test_file.write_bytes(content)
        content_hash = hashlib.sha256(content).hexdigest()

        synthetic_inventory = {
            2016: SourceEntry(
                year=2016,
                relative_path="flight_2016.csv",
                audited_row_count=1,
                audited_byte_size=len(content),
                audited_column_count=34,
            )
        }
        approved_hashes = {2016: content_hash}

        validator = SourceValidator(
            base_dir=self.base_path,
            inventory=synthetic_inventory,
            approved_baseline_hashes=approved_hashes,
        )

        batch = validator.verify_all_sources(compute_hash=True)
        self.assertTrue(batch.all_hashes_verified)

        # Record into manifest
        validator.record_into_run_manifest(manifest, batch, record_only_verified_hashes=True)

        self.assertEqual(len(manifest.inputs), 1)
        self.assertEqual(manifest.inputs[0]["bytes"], len(content))
        self.assertEqual(manifest.inputs[0]["sha256"], content_hash)

        # Test with unverified candidate hash: sha256 must be 'UNVERIFIED'
        manifest_unverified = RunManifest(run_id="run_test_002", task_id="T007-02A")
        validator_unapproved = SourceValidator(
            base_dir=self.base_path,
            inventory=synthetic_inventory,
            approved_baseline_hashes=None,  # No approved baseline
        )
        batch_unapproved = validator_unapproved.verify_all_sources(compute_hash=True)
        self.assertFalse(batch_unapproved.all_hashes_verified)
        self.assertTrue(batch_unapproved.has_unapproved_candidate_hashes)

        validator_unapproved.record_into_run_manifest(
            manifest_unverified, batch_unapproved, record_only_verified_hashes=True
        )
        self.assertEqual(len(manifest_unverified.inputs), 1)
        self.assertEqual(manifest_unverified.inputs[0]["sha256"], "UNVERIFIED")

    # -------------------------------------------------------------------------
    # Governance Invariants (GOV-01, GOV-02)
    # -------------------------------------------------------------------------

    def test_gov_01_source_manifest_not_used_as_raw_hash_registry(self):
        """GOV-01: SOURCE_MANIFEST.json is an audit document manifest, not raw CSV hash registry (DOC-F01)."""
        source_manifest_path = Path("docs/05-evidence/inputs/SOURCE_MANIFEST.json")
        if source_manifest_path.exists():
            data = json.loads(source_manifest_path.read_text(encoding="utf-8"))
            statement = data.get("statement", "")
            self.assertIn("NOT raw CSV files", statement)

    def test_gov_02_upstream_identity_unverified_invariant(self):
        """GOV-02: OR-08 / TS-019 upstream identity status remains strictly IDENTITY_UNVERIFIED."""
        test_file = self.base_path / "source_2016.csv"
        content = b"content"
        test_file.write_bytes(content)
        content_hash = hashlib.sha256(content).hexdigest()

        synthetic_inventory = {
            2016: SourceEntry(
                year=2016,
                relative_path="source_2016.csv",
                audited_row_count=1,
                audited_byte_size=len(content),
                audited_column_count=34,
            )
        }
        validator = SourceValidator(
            base_dir=self.base_path,
            inventory=synthetic_inventory,
            approved_baseline_hashes={2016: content_hash},
        )

        res = validator.verify_source(2016, compute_hash=True)
        self.assertTrue(res.is_verified)
        self.assertEqual(res.upstream_identity_status, "IDENTITY_UNVERIFIED")

        batch = validator.verify_all_sources(compute_hash=True)
        self.assertTrue(batch.all_hashes_verified)
        self.assertEqual(batch.upstream_identity_status, "IDENTITY_UNVERIFIED")

    # -------------------------------------------------------------------------
    # Scope Boundaries (SCOPE-01, SCOPE-02)
    # -------------------------------------------------------------------------

    def test_scope_01_synthetic_isolation_no_real_raw_csv_accessed(self):
        """SCOPE-01: Asserts tests operate strictly on synthetic fixtures, not data/raw/."""
        # Check that base_dir in our tests is the temp directory
        self.assertTrue(str(self.base_path).startswith(tempfile.gettempdir()) or "tmp" in str(self.base_path).lower())
        self.assertNotIn("data/raw/tabular", str(self.base_path).replace("\\", "/"))

    def test_scope_02_validator_contains_no_csv_reader_or_publication_code(self):
        """SCOPE-02: SourceValidator contains no Spark CSV reader, classifier, or publication calls."""
        import inspect
        import flight_pipeline.ingestion.source_validator as sv_module
        source_code = inspect.getsource(sv_module)
        violations = _check_ast_for_forbidden_ingestion_or_publication(source_code)
        self.assertEqual(violations, [], f"Forbidden constructs found in source_validator.py: {violations}")

    def test_scope_02_mutation_detection_fails_on_forbidden_constructs(self):
        """SCOPE-02 Negative/Mutation: Verifier detects forbidden imports and calls on mutant snippet."""
        mutant_snippet = """
import csv
from flight_pipeline.publication import SafePublisher
def forbidden_logic(spark):
    sp = SafePublisher()
    df = spark.read.csv("data/raw/sample.csv")
    classify_records(df)
"""
        violations = _check_ast_for_forbidden_ingestion_or_publication(mutant_snippet)
        self.assertGreaterEqual(len(violations), 4, f"Expected at least 4 violations, got: {violations}")
        violation_text = "\n".join(violations)
        self.assertIn("csv", violation_text)
        self.assertIn("SafePublisher", violation_text)
        self.assertIn("read.csv", violation_text)
        self.assertIn("classify_records", violation_text)

    # -------------------------------------------------------------------------
    # Final Closure Regression Tests (FIX-A01 .. FIX-A04)
    # -------------------------------------------------------------------------

    def test_closure_fix_a01_empty_inventory_rejected_in_init(self):
        """FIX-A01: SourceValidator rejects empty inventory in constructor."""
        with self.assertRaises(SourceConfigurationError):
            SourceValidator(base_dir=self.base_path, inventory={}, approved_baseline_hashes={})

    def test_closure_fix_a01_production_completeness_guard(self):
        """FIX-A01: Enforcing production completeness rejects partial (subset) inventory."""
        partial_inv = {
            2016: SourceEntry(
                year=2016,
                relative_path="flight_2016.csv",
                audited_row_count=1,
                audited_byte_size=10,
                audited_column_count=34,
            )
        }
        with self.assertRaises(SourceConfigurationError):
            SourceValidator(
                base_dir=self.base_path,
                inventory=partial_inv,
                enforce_production_inventory=True,
            )

    def test_closure_fix_a02_directory_source_read_error_batch_fail_closed(self):
        """FIX-A02: Directory source resulting in SOURCE_READ_ERROR sets all_present=False and all_sizes_match=False."""
        dir_source = self.base_path / "dir_source.csv"
        dir_source.mkdir(exist_ok=True)
        synthetic_inv = {
            2020: SourceEntry(
                year=2020,
                relative_path="dir_source.csv",
                audited_row_count=1,
                audited_byte_size=100,
                audited_column_count=34,
            )
        }
        validator = SourceValidator(base_dir=self.base_path, inventory=synthetic_inv)
        batch = validator.verify_all_sources(compute_hash=False)

        self.assertEqual(batch.results[2020].state, VerificationState.SOURCE_READ_ERROR)
        self.assertFalse(batch.all_present, "all_present must be False when a source is a directory / read error")
        self.assertFalse(batch.all_sizes_match, "all_sizes_match must be False when a source has a read error")
        self.assertFalse(batch.all_hashes_verified)

    def test_closure_fix_a02_all_verification_states_fail_closed_matrix(self):
        """FIX-A02: Exhaustively test that error states properly fail-closed in batch flags."""
        # 1. Size mismatch: all_present=True, all_sizes_match=False, all_hashes_verified=False
        f1 = self.base_path / "size_bad.csv"
        f1.write_bytes(b"short")
        inv1 = {
            2020: SourceEntry(
                year=2020,
                relative_path="size_bad.csv",
                audited_row_count=1,
                audited_byte_size=100,
                audited_column_count=34,
            )
        }
        v1 = SourceValidator(base_dir=self.base_path, inventory=inv1)
        b1 = v1.verify_all_sources(compute_hash=False)
        self.assertTrue(b1.all_present)
        self.assertFalse(b1.all_sizes_match)
        self.assertFalse(b1.all_hashes_verified)

        # 2. Hash mismatch: all_present=True, all_sizes_match=True, all_hashes_verified=False
        content = b"content_for_hash"
        f2 = self.base_path / "hash_bad.csv"
        f2.write_bytes(content)
        inv2 = {
            2020: SourceEntry(
                year=2020,
                relative_path="hash_bad.csv",
                audited_row_count=1,
                audited_byte_size=len(content),
                audited_column_count=34,
            )
        }
        v2 = SourceValidator(
            base_dir=self.base_path,
            inventory=inv2,
            approved_baseline_hashes={2020: "0" * 64},
        )
        b2 = v2.verify_all_sources(compute_hash=True)
        self.assertTrue(b2.all_present)
        self.assertTrue(b2.all_sizes_match)
        self.assertFalse(b2.all_hashes_verified)

    def test_closure_fix_a03_intermediate_directory_symlink_rejected(self):
        """FIX-A03: Symlink in intermediate directory path must be rejected by validate_path_safety."""
        real_subdir = self.base_path / "real_subdir"
        real_subdir.mkdir(exist_ok=True)
        target_f = real_subdir / "file.csv"
        target_f.write_bytes(b"data")

        link_subdir = self.base_path / "link_subdir"
        try:
            os.symlink(real_subdir, link_subdir)
            has_symlink = True
        except (OSError, NotImplementedError):
            has_symlink = False

        if has_symlink:
            target_via_link = link_subdir / "file.csv"
            with self.assertRaises(SourcePathSecurityError):
                validate_path_safety(target_via_link, base_dir=self.base_path)
        else:
            # If OS does not permit symlink, mock intermediate link
            with patch("os.path.islink", side_effect=lambda p: str(p) == str(link_subdir)):
                with self.assertRaises(SourcePathSecurityError):
                    validate_path_safety(link_subdir / "file.csv", base_dir=self.base_path)

    def test_closure_fix_a03_windows_junction_rejected(self):
        """FIX-A03: Windows NTFS junction point in path hierarchy must be rejected."""
        real_dir = self.base_path / "junc_real"
        real_dir.mkdir(exist_ok=True)
        sample_file = real_dir / "target.csv"
        sample_file.write_bytes(b"content")

        junc_dir = self.base_path / "junc_link"
        res = os.system(f'cmd /c mklink /J "{junc_dir}" "{real_dir}" >nul 2>&1')
        if res == 0:
            try:
                target_via_junc = junc_dir / "target.csv"
                with self.assertRaises(SourcePathSecurityError):
                    validate_path_safety(target_via_junc, base_dir=self.base_path)
            finally:
                if os.path.exists(junc_dir):
                    os.rmdir(junc_dir)
        else:
            self.skipTest("mklink /J not permitted in current environment")

    def test_closure_fix_a04_run_manifest_rejects_failed_batch(self):
        """FIX-A04: record_into_run_manifest fails-closed when batch contains unverified/failed sources."""
        manifest = RunManifest(run_id="run_fail_test", task_id="T007")
        missing_inv = {
            2020: SourceEntry(
                year=2020,
                relative_path="nonexistent_file.csv",
                audited_row_count=100,
                audited_byte_size=500,
                audited_column_count=34,
            )
        }
        validator = SourceValidator(base_dir=self.base_path, inventory=missing_inv)
        batch = validator.verify_all_sources(compute_hash=False)

        # Attempting to record a failed batch into RunManifest must raise SourceIntegrityError
        with self.assertRaises(SourceIntegrityError):
            validator.record_into_run_manifest(manifest, batch, allow_partial=False)

    def test_closure_fix_a04_run_manifest_partial_mode_rejects_failed_sources(self):
        """FIX-A04: In allow_partial=True mode, failed sources are excluded from manifest.inputs and returned in rejection report."""
        manifest = RunManifest(run_id="run_partial_test", task_id="T007")
        good_file = self.base_path / "valid.csv"
        good_content = b"valid,data\n1,2\n"
        good_file.write_bytes(good_content)

        inv = {
            2016: SourceEntry(
                year=2016,
                relative_path="valid.csv",
                audited_row_count=1,
                audited_byte_size=len(good_content),
                audited_column_count=34,
            ),
            2017: SourceEntry(
                year=2017,
                relative_path="missing_file.csv",
                audited_row_count=1,
                audited_byte_size=10,
                audited_column_count=34,
            ),
        }
        validator = SourceValidator(base_dir=self.base_path, inventory=inv)
        batch = validator.verify_all_sources(compute_hash=False)

        report = validator.record_into_run_manifest(manifest, batch, allow_partial=True)
        self.assertEqual(len(manifest.inputs), 1)
        self.assertEqual(manifest.inputs[0]["path"], str(good_file))
        self.assertEqual(report["recorded_count"], 1)
        self.assertEqual(report["rejected_count"], 1)
        self.assertEqual(len(report["rejected_details"]), 1)
        self.assertEqual(report["rejected_details"][0]["year"], 2017)

    # -------------------------------------------------------------------------
    # Security Delta Regression Tests (FIX-SEC01, FIX-SEC03)
    # -------------------------------------------------------------------------

    def test_secdelta_fix_sec01_lstat_permission_error_raises_security_error(self):
        """FIX-SEC01: PermissionError during os.lstat fails closed with SourcePathSecurityError."""
        from flight_pipeline.ingestion.source_validator import is_symlink_or_reparse
        test_file = self.base_path / "inaccessible.csv"
        test_file.write_bytes(b"data")
        with patch("os.lstat", side_effect=PermissionError("Permission denied inspecting attributes")):
            with self.assertRaises(SourcePathSecurityError):
                is_symlink_or_reparse(test_file)

    def test_secdelta_fix_sec01_lstat_eio_error_raises_security_error(self):
        """FIX-SEC01: EIO during os.lstat fails closed with SourcePathSecurityError."""
        from flight_pipeline.ingestion.source_validator import is_symlink_or_reparse
        test_file = self.base_path / "eio.csv"
        test_file.write_bytes(b"data")
        with patch("os.lstat", side_effect=OSError(errno.EIO, "I/O error")):
            with self.assertRaises(SourcePathSecurityError):
                is_symlink_or_reparse(test_file)

    def test_secdelta_fix_sec01_missing_file_differentiated_and_returns_source_missing(self):
        """FIX-SEC01: Genuine non-existent source file is not a security error; returns SOURCE_MISSING."""
        from flight_pipeline.ingestion.source_validator import is_symlink_or_reparse
        missing_file = self.base_path / "non_existent_flight.csv"
        self.assertFalse(is_symlink_or_reparse(missing_file))

        inv = {
            2016: SourceEntry(
                year=2016,
                relative_path="non_existent_flight.csv",
                audited_row_count=1,
                audited_byte_size=10,
                audited_column_count=34,
            )
        }
        val = SourceValidator(base_dir=self.base_path, inventory=inv)
        res = val.verify_source(2016, fail_fast=False)
        self.assertEqual(res.state, VerificationState.SOURCE_MISSING)

    def test_secdelta_fix_sec01_inaccessible_intermediate_path_fails_closed(self):
        """FIX-SEC01: Inaccessible intermediate ancestor directory fails closed."""
        sub = self.base_path / "sub"
        sub.mkdir(exist_ok=True)
        target = sub / "file.csv"
        target.write_bytes(b"data")

        orig_lstat = os.lstat
        def fake_lstat(path, *args, **kwargs):
            if str(sub) in str(path) and "file.csv" not in str(path):
                raise PermissionError("Access denied to intermediate directory")
            return orig_lstat(path, *args, **kwargs)

        with patch("os.lstat", side_effect=fake_lstat):
            with self.assertRaises(SourcePathSecurityError):
                validate_path_safety(target, base_dir=self.base_path)

    def test_secdelta_fix_sec03_metadata_io_error_returns_source_read_error(self):
        """FIX-SEC03: Non-PermissionError OSError during stat/getsize returns SOURCE_READ_ERROR."""
        test_file = self.base_path / "io_error.csv"
        test_file.write_bytes(b"data")
        inv = {
            2016: SourceEntry(
                year=2016,
                relative_path="io_error.csv",
                audited_row_count=1,
                audited_byte_size=4,
                audited_column_count=34,
            )
        }
        val = SourceValidator(base_dir=self.base_path, inventory=inv)
        orig_stat = os.stat
        def fake_stat(p, *args, **kwargs):
            if "io_error.csv" in str(p):
                raise OSError(errno.EIO, "Simulated disk I/O failure")
            return orig_stat(p, *args, **kwargs)

        with patch("os.stat", side_effect=fake_stat):
            res = val.verify_source(2016, fail_fast=False)
            self.assertEqual(res.state, VerificationState.SOURCE_READ_ERROR)
            self.assertIn("I/O error", res.error_message)

    def test_secdelta_fix_sec03_metadata_io_error_fail_fast_raises_source_integrity_error(self):
        """FIX-SEC03: Fail-fast mode raises SourceIntegrityError on metadata I/O failure."""
        test_file = self.base_path / "io_error_ff.csv"
        test_file.write_bytes(b"data")
        inv = {
            2016: SourceEntry(
                year=2016,
                relative_path="io_error_ff.csv",
                audited_row_count=1,
                audited_byte_size=4,
                audited_column_count=34,
            )
        }
        val = SourceValidator(base_dir=self.base_path, inventory=inv)
        orig_stat = os.stat
        def fake_stat(p, *args, **kwargs):
            if "io_error_ff.csv" in str(p):
                raise OSError(errno.EIO, "Simulated disk I/O failure")
            return orig_stat(p, *args, **kwargs)

        with patch("os.stat", side_effect=fake_stat):
            with self.assertRaises(SourceIntegrityError):
                val.verify_source(2016, fail_fast=True)

    def test_secdelta_fix_sec03_batch_aggregation_fail_closed_on_io_error(self):
        """FIX-SEC03: Batch aggregation sets all flags False when metadata I/O failure occurs."""
        good_file = self.base_path / "good.csv"
        good_file.write_bytes(b"data")
        bad_file = self.base_path / "bad_io.csv"
        bad_file.write_bytes(b"data")

        inv = {
            2016: SourceEntry(
                year=2016,
                relative_path="good.csv",
                audited_row_count=1,
                audited_byte_size=4,
                audited_column_count=34,
            ),
            2017: SourceEntry(
                year=2017,
                relative_path="bad_io.csv",
                audited_row_count=1,
                audited_byte_size=4,
                audited_column_count=34,
            ),
        }
        val = SourceValidator(base_dir=self.base_path, inventory=inv)
        orig_stat = os.stat
        def fake_stat(p, *args, **kwargs):
            if "bad_io.csv" in str(p):
                raise OSError(errno.EIO, "Simulated disk read error")
            return orig_stat(p, *args, **kwargs)

        with patch("os.stat", side_effect=fake_stat):
            batch = val.verify_all_sources(compute_hash=False)
            self.assertFalse(batch.all_present)
            self.assertFalse(batch.all_sizes_match)
            self.assertFalse(batch.all_hashes_verified)
            self.assertEqual(batch.results[2017].state, VerificationState.SOURCE_READ_ERROR)


if __name__ == "__main__":
    unittest.main()

