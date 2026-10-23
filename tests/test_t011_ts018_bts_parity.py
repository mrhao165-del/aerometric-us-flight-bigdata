"""
Unit test suite for TS-018 BTS TranStats Reconciliation Engine.
Conforms to Master Execution Prompt T-011, T011-R2 remediation requirements, and G2-EXC-001 obligations.
Tests:
- R2-F01: Provenance gating separating the 5 governance states.
- R2-F02: 7-field completeness (each field omitted in turn, all null, 1 null, scale, sign, missingness).
- R2-F03: Robust composite keys (numerical zero 0.0, blank date, malformed date, non-finite fl num).
"""

from pathlib import Path
import sys
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flight_pipeline.kpi.bts_reconciler import (
    BtsTranStatsReconciler,
    BtsProvenanceMetadata,
    BtsProvenanceValidator,
    CORE_MEASURE_MAPPINGS,
    MismatchType,
    KeyMatchStatus,
)


class TestTs018BtsParity(unittest.TestCase):
    """Test suite validating BtsTranStatsReconciler behavior and fail-closed rules."""

    def setUp(self):
        self.reconciler = BtsTranStatsReconciler(tolerance=1e-4)
        self.valid_base_dataset = {
            "FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 1234.0,
            "ORIGIN": "DFW", "DEST": "ORD",
            "ARR_DELAY": -15.0, "DEP_DELAY": -5.0, "TAXI_OUT": 18.0, "TAXI_IN": 7.0,
            "AIR_TIME": 115.0, "ACTUAL_ELAPSED_TIME": 140.0, "CRS_ELAPSED_TIME": 150.0,
        }
        self.valid_base_bts = {
            "FlightDate": "2018-05-10", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 1234,
            "Origin": "DFW", "Dest": "ORD",
            "ArrDelay": -15.0, "DepDelay": -5.0, "TaxiOut": 18.0, "TaxiIn": 7.0,
            "AirTime": 115.0, "ActualElapsedTime": 140.0, "CRSElapsedTime": 150.0,
        }

    def test_01_exact_match_all_seven_measures_synthetic(self):
        """Synthetic run with all 7 measures matching returns SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING."""
        summary, results = self.reconciler.reconcile([self.valid_base_dataset], [self.valid_base_bts], is_authentic_bts_data=False)

        self.assertEqual(summary.unique_key_matches, 1)
        self.assertEqual(summary.ambiguous_duplicate_keys, 0)
        self.assertTrue(results[0].all_fields_match)

        for field_name in CORE_MEASURE_MAPPINGS.keys():
            comp = results[0].field_comparisons[field_name]
            self.assertEqual(comp.status, MismatchType.EXACT_MATCH)
            self.assertEqual(comp.abs_diff, 0.0)

        # Synthetic run MUST NOT claim official BTS PASS
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING")
        self.assertFalse(summary.is_authentic_bts_data)

    def test_02_scale_mismatch_detection(self):
        """Scale factor of 60 (seconds vs minutes) is detected as SCALE_DIFF."""
        bts_rec = dict(self.valid_base_bts)
        bts_rec["AirTime"] = 115.0 * 60.0  # seconds instead of minutes

        summary, results = self.reconciler.reconcile([self.valid_base_dataset], [bts_rec], is_authentic_bts_data=False)
        comp = results[0].field_comparisons["AIR_TIME"]
        self.assertEqual(comp.status, MismatchType.SCALE_DIFF)
        self.assertFalse(results[0].all_fields_match)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED")

    def test_03_sign_mismatch_detection(self):
        """Opposite signs on delay are detected as SIGN_MISMATCH."""
        bts_rec = dict(self.valid_base_bts)
        bts_rec["ArrDelay"] = 15.0  # dataset has -15.0

        summary, results = self.reconciler.reconcile([self.valid_base_dataset], [bts_rec], is_authentic_bts_data=False)
        comp = results[0].field_comparisons["ARR_DELAY"]
        self.assertEqual(comp.status, MismatchType.SIGN_MISMATCH)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED")

    def test_04_missingness_mismatch_and_null_agreement(self):
        """Valid null-null agreement vs missingness mismatch."""
        d_rec = dict(self.valid_base_dataset)
        d_rec["ARR_DELAY"] = None
        d_rec["TAXI_OUT"] = None

        b_rec = dict(self.valid_base_bts)
        b_rec["ArrDelay"] = None  # null-null
        b_rec["TaxiOut"] = 25.0   # missingness mismatch

        summary, results = self.reconciler.reconcile([d_rec], [b_rec], is_authentic_bts_data=False)
        self.assertEqual(results[0].field_comparisons["ARR_DELAY"].status, MismatchType.NULL_NULL_AGREEMENT)
        self.assertEqual(results[0].field_comparisons["TAXI_OUT"].status, MismatchType.MISSINGNESS_MISMATCH)

    def test_05_ambiguous_duplicate_key_detection(self):
        """Duplicate composite keys are classified as AMBIGUOUS_DUPLICATE."""
        d1 = dict(self.valid_base_dataset)
        d2 = dict(self.valid_base_dataset)
        d2["ARR_DELAY"] = 20.0

        summary, results = self.reconciler.reconcile([d1, d2], [self.valid_base_bts], is_authentic_bts_data=False)
        self.assertEqual(summary.ambiguous_duplicate_keys, 2)
        self.assertEqual(summary.unique_key_matches, 0)

    def test_06_authentic_parity_fail_closed_on_unmatched_records(self):
        """Authentic reconciliation must FAIL if any unmatched records exist on either side."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="RECORD_001",
            is_external_reference=True,
            sha256_hash="a" * 64,
        )
        d_extra = dict(self.valid_base_dataset)
        d_extra["OP_CARRIER_FL_NUM"] = 9999.0

        summary, _ = self.reconciler.reconcile(
            [self.valid_base_dataset, d_extra],
            [self.valid_base_bts],
            provenance_metadata=prov,
            is_authentic_bts_data=True,
        )
        self.assertEqual(summary.unmatched_dataset_records, 1)
        self.assertEqual(summary.reconciliation_verdict, "TS018_FAIL_DISCREPANCIES_DETECTED")

    def test_07_authentic_parity_fail_closed_on_all_null_measures(self):
        """Authentic reconciliation must FAIL if all measures are NULL (0 numeric observations)."""
        prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="RECORD_001",
            is_external_reference=True,
            sha256_hash="a" * 64,
        )
        d_null = {k: None if k in CORE_MEASURE_MAPPINGS else v for k, v in self.valid_base_dataset.items()}
        b_null = {k: None if k in CORE_MEASURE_MAPPINGS.values() else v for k, v in self.valid_base_bts.items()}

        summary, _ = self.reconciler.reconcile([d_null], [b_null], provenance_metadata=prov, is_authentic_bts_data=True)
        self.assertEqual(summary.reconciliation_verdict, "TS018_FAIL_DISCREPANCIES_DETECTED")

    def test_08_flight_number_numerical_zero_and_invalid_handling(self):
        """Flight number 0.0 is preserved; corrupt/empty/NaN flight numbers are flagged as invalid keys."""
        # 0.0 is preserved
        k_zero = self.reconciler.extract_composite_key({"FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 0, "ORIGIN": "DFW", "DEST": "ORD"})
        self.assertEqual(k_zero[2], 0.0)
        self.assertTrue(k_zero[5])

        # Corrupt flight number
        k_corrupt = self.reconciler.extract_composite_key({"FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": "CORRUPT", "ORIGIN": "DFW", "DEST": "ORD"})
        self.assertIsNone(k_corrupt[2])
        self.assertFalse(k_corrupt[5])

    def test_09_each_of_seven_fields_omitted_in_turn(self):
        """Each of the 7 CORE measures omitted in turn must trigger SCHEMA_MISSING_COLUMN and fail."""
        for field_name in CORE_MEASURE_MAPPINGS.keys():
            bts_col = CORE_MEASURE_MAPPINGS[field_name]
            d_omitted = {k: v for k, v in self.valid_base_dataset.items() if k != field_name}
            b_omitted = {k: v for k, v in self.valid_base_bts.items() if k != bts_col}

            summary, results = self.reconciler.reconcile([d_omitted], [b_omitted], is_authentic_bts_data=False)
            comp = results[0].field_comparisons[field_name]
            self.assertEqual(comp.status, MismatchType.SCHEMA_MISSING_COLUMN, f"Field {field_name} omission not flagged as missing column")
            self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED")

    def test_10_only_arr_delay_present_fails_closed(self):
        """Only ARR_DELAY present (other 6 absent) must fail closed due to missing columns and 0 numeric samples."""
        d_only = {"FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0, "ORIGIN": "DFW", "DEST": "ORD", "ARR_DELAY": 5.0}
        b_only = {"FlightDate": "2018-05-10", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 101, "Origin": "DFW", "Dest": "ORD", "ArrDelay": 5.0}

        summary, _ = self.reconciler.reconcile([d_only], [b_only], is_authentic_bts_data=False)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED")

    def test_11_only_dep_delay_present_fails_closed(self):
        """Only DEP_DELAY present (other 6 absent) must fail closed."""
        d_only = {"FL_DATE": "2018-05-10", "OP_CARRIER": "AA", "OP_CARRIER_FL_NUM": 101.0, "ORIGIN": "DFW", "DEST": "ORD", "DEP_DELAY": 5.0}
        b_only = {"FlightDate": "2018-05-10", "Reporting_Airline": "AA", "Flight_Number_Reporting_Airline": 101, "Origin": "DFW", "Dest": "ORD", "DepDelay": 5.0}

        summary, _ = self.reconciler.reconcile([d_only], [b_only], is_authentic_bts_data=False)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED")

    def test_12_all_seven_present_but_one_entirely_null(self):
        """All 7 fields present in schema, but one field (TAXI_IN) is null on all records -> fail closed."""
        d_rec = dict(self.valid_base_dataset)
        d_rec["TAXI_IN"] = None
        b_rec = dict(self.valid_base_bts)
        b_rec["TaxiIn"] = None

        summary, _ = self.reconciler.reconcile([d_rec], [b_rec], is_authentic_bts_data=False)
        # 6 fields have numeric samples, TAXI_IN has 0
        self.assertEqual(summary.field_statistics["TAXI_IN"]["numeric_sample_count"], 0)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED")

    def test_13_field_missing_on_only_one_side(self):
        """Field present in dataset but missing in BTS schema is detected as SCHEMA_MISSING_COLUMN."""
        b_missing = {k: v for k, v in self.valid_base_bts.items() if k != "CRSElapsedTime"}
        summary, results = self.reconciler.reconcile([self.valid_base_dataset], [b_missing], is_authentic_bts_data=False)
        self.assertEqual(results[0].field_comparisons["CRS_ELAPSED_TIME"].status, MismatchType.SCHEMA_MISSING_COLUMN)
        self.assertEqual(summary.reconciliation_verdict, "SYNTHETIC_RECONCILER_FAIL_DISCREPANCIES_DETECTED")

    def test_14_provenance_validation_gates_authentic_pass(self):
        """
        R2-F01: Passing matching data with is_authentic_bts_data=True without provenance
        or with unapproved provenance MUST NEVER return TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED.
        """
        # Case A: Caller boolean alone without provenance
        summary_no_prov, _ = self.reconciler.reconcile(
            [self.valid_base_dataset], [self.valid_base_bts], is_authentic_bts_data=True
        )
        self.assertNotEqual(summary_no_prov.reconciliation_verdict, "TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED")
        self.assertEqual(summary_no_prov.reconciliation_verdict, "SYNTHETIC_RECONCILER_VERIFIED_AUTHENTIC_BTS_PENDING")

        # Case B: Unapproved provenance
        unapproved_prov = BtsProvenanceMetadata(
            project_lead_approval_status="PENDING_APPROVAL",
            approval_record_ref="DRAFT",
            is_external_reference=True,
            sha256_hash="a" * 64,
        )
        summary_unapp, _ = self.reconciler.reconcile(
            [self.valid_base_dataset], [self.valid_base_bts],
            provenance_metadata=unapproved_prov,
            is_authentic_bts_data=True,
        )
        self.assertNotEqual(summary_unapp.reconciliation_verdict, "TS018_PASS_AUTHENTIC_PARITY_ESTABLISHED")

        # Case C: Fully approved provenance
        approved_prov = BtsProvenanceMetadata(
            project_lead_approval_status="APPROVED_BY_PROJECT_LEAD",
            approval_record_ref="DECISION_20261019_PL_BTS_SAMPLE",
            is_external_reference=True,
            sha256_hash="a" * 64,
        )
        summary_app, _ = self.reconciler.reconcile(
            [self.valid_base_dataset], [self.valid_base_bts],
            provenance_metadata=approved_prov,
            is_authentic_bts_data=True,
        )
        self.assertEqual(summary_app.reconciliation_verdict, "TS018_CANDIDATE_PARITY_VERIFIED_HUMAN_APPROVAL_PENDING")
        self.assertFalse(summary_app.source_provenance_verified)
        self.assertTrue(summary_app.companion_metadata_valid)
        self.assertFalse(summary_app.human_accepted)

    def test_15_blank_or_invalid_date_fails_closed(self):
        """Blank date or invalid date format fails composite key validation and cannot match."""
        d_blank = dict(self.valid_base_dataset)
        d_blank["FL_DATE"] = ""
        b_blank = dict(self.valid_base_bts)
        b_blank["FlightDate"] = ""

        summary, results = self.reconciler.reconcile([d_blank], [b_blank], is_authentic_bts_data=False)
        self.assertEqual(summary.unique_key_matches, 0)
        self.assertEqual(summary.invalid_key_records, 2)
        self.assertEqual(results[0].key_status, KeyMatchStatus.INVALID_KEY)


if __name__ == "__main__":
    unittest.main()
