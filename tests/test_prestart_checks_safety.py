#!/usr/bin/env python3
"""
tests/test_prestart_checks_safety.py

Targeted Regression Tests for Prestart Runner Safety (Task A: G6-T012-2016-PRESTART).
Verifies:
1. Source integrity failure causes nonzero exit code and accurate step reporting.
2. The prestart runner does not invoke live coordinator against production data directories.
3. Fail-closed behavior on mandatory check failures.
"""

from pathlib import Path
import tempfile
import unittest

from tools.qa.run_g6_t012_prestart_checks import evaluate_source_integrity, run_checks


class TestPrestartChecksSafety(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_source_integrity_missing_file_fails(self):
        """Scenario 1: Missing source file evaluates to valid=False and fails prestart with nonzero exit."""
        nonexistent = self.temp_path / "nonexistent.csv"
        res = evaluate_source_integrity(nonexistent)
        self.assertFalse(res["valid"])
        self.assertFalse(res["exists"])

        # Running run_checks with nonexistent source must return 1
        log_file = self.temp_path / "test_log.txt"
        code = run_checks(raw_path_override=nonexistent, allow_resource_hold=True, output_log_path=log_file)
        self.assertEqual(code, 1)

        # Verify step recorded exit code 1
        log_content = log_file.read_text(encoding="utf-8")
        self.assertIn(">>> STEP: Canonical 2016 RAW File Inspection\nCommand: internal_hash_check\nExit Code: 1", log_content)
        self.assertIn("PRESTART OVERALL VERDICT: FAIL", log_content)

    def test_02_source_integrity_size_mismatch_fails(self):
        """Scenario 2: Source file with incorrect size evaluates to valid=False and fails prestart."""
        dummy = self.temp_path / "bad_size.csv"
        dummy.write_bytes(b"short content")
        res = evaluate_source_integrity(dummy, expected_size=1538427452)
        self.assertFalse(res["valid"])
        self.assertTrue(res["exists"])
        self.assertFalse(res["size_match"])

        log_file = self.temp_path / "test_log.txt"
        code = run_checks(raw_path_override=dummy, allow_resource_hold=True, output_log_path=log_file)
        self.assertEqual(code, 1)

    def test_03_no_live_coordinator_invocation_in_runner(self):
        """Scenario 3: Prestart runner must not contain live coordinator invocations without --dry-run-preflight."""
        runner_source = (Path(__file__).resolve().parents[1] / "tools" / "qa" / "run_g6_t012_prestart_checks.py").read_text(encoding="utf-8")
        # Ensure that any command list invoking coordinator.py includes --dry-run-preflight
        import ast
        tree = ast.parse(runner_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.List):
                str_elts = [elt.value for elt in node.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)]
                if any("coordinator.py" in s for s in str_elts):
                    self.assertIn(
                        "--dry-run-preflight",
                        str_elts,
                        f"Found unsafe coordinator subprocess invocation without --dry-run-preflight: {str_elts}"
                    )


if __name__ == "__main__":
    unittest.main()
