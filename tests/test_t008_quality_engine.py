"""
Comprehensive Unit & Integration Test Suite for T-008 Data Quality Engine.
Conforms to DATA_CONTRACT.md (DC-11, DC-12), ARCHITECTURE.md, T006_FINAL_CORRECTIONS_ADDENDUM.md,
and Gate G3 / G4 governance decisions (G3-COND-A, FP-DEC-007, FP-DEC-010, FP-DEC-017, OR-05).

Test Groups:
1. QUALITY: Core identity anchors, calendar dates, numeric domains, negative delays, weather optionality, duplicates.
2. ACCOUNTING: DC-11 3-state disjointness, independent raw balance, metric bounds, zero-denominator.
3. COVERAGE: Calendar date coverage, normal vs leap year, OR-05 2024 missing March detection, partial status.
4. POLICY: G3-COND-A provisional compliance, unapproved policy rejection, provisional impact profiling.
5. INTEGRATION: End-to-end pipeline with RawCsvReader, QualityEngine, IngestionTransformer, and forensics.
"""

from calendar import isleap
from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, LongType, StringType

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
from flight_pipeline.ingestion.reader import (
    ANOMALY_FLAGS_COLUMN,
    REASON_COLUMN,
    STATUS_COLUMN,
    AnomalyReason,
    CsvReadOptions,
    IngestionRecordClassifier,
    IngestionTransformer,
    RawCsvReader,
    RecordStatus,
)
from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMN_NAMES,
    CANONICAL_COLUMNS_COUNT,
    CORRUPT_RECORD_COLUMN,
    get_curated_parquet_schema,
)
from flight_pipeline.quality.accounting import (
    AccountingBalanceError,
    QualityAccountingEngine,
)
from flight_pipeline.quality.catalog import (
    QualityRuleCatalog,
    RuleConsequence,
    RuleScope,
    RuleSeverity,
)
from flight_pipeline.quality.coverage import (
    CoverageReport,
    DateCoverageAnalyzer,
)
from flight_pipeline.quality.engine import (
    QualityEngine,
    QualityValidationResult,
)
from flight_pipeline.quality.policy import (
    PolicyViolationError,
    ProvisionalPolicyProfile,
    ProvisionalPolicyProfiler,
    QualityPolicyConfig,
)
from flight_pipeline.quality.predicates import (
    is_finite_numeric,
    is_valid_actual_elapsed_time,
    is_valid_air_time,
    is_valid_arr_delay,
    is_valid_crs_elapsed_time,
    is_valid_dep_delay,
    is_valid_taxi_in,
    is_valid_taxi_out,
)
from flight_pipeline.utils.run_manifest import MetricAccounting, RowAccounting


class TestT008QualityEngine(unittest.TestCase):
    """Unified test suite for T-008 Data Quality, Disjoint Row Accounting, and Quarantine Engine."""

    @classmethod
    def setUpClass(cls):
        """Initialize isolated local SparkSession."""
        cfg = SparkConfig(
            app_name="TestT008QualityEngine",
            master="local[2]",
            driver_memory="2g",
            shuffle_partitions=4,
        )
        cls.spark = get_spark_session(cfg)

    @classmethod
    def tearDownClass(cls):
        """Clean up SparkSession."""
        if cls.spark:
            stop_spark_session(cls.spark)

    def _make_valid_row(
        self,
        fl_date: str = "2016-01-01",
        op_carrier: str = "AA",
        fl_num: str = "1234.0",
        origin: str = "JFK",
        dest: str = "LAX",
        dep_delay: str = "10.0",
        arr_delay: str = "-5.0",
        taxi_out: str = "15.0",
        taxi_in: str = "5.0",
        air_time: str = "335.0",
        actual_elapsed: str = "355.0",
        crs_elapsed: str = "360.0",
        flights: str = "1.0",
        month: str = "1",
        day_of_month: str = "1",
        o_temp: str = "15.5",
        o_prcp: str = "0.0",
        o_wspd: str = "12.0",
        d_temp: str = "22.0",
        d_prcp: str = "0.1",
        d_wspd: str = "8.0",
    ) -> str:
        """Generate a canonical 34-column CSV line."""
        fields = [
            fl_date,
            op_carrier,
            fl_num,
            origin,
            dest,
            "0800",
            "0810",
            dep_delay,
            taxi_out,
            "0825",
            "1110",
            taxi_in,
            "1120",
            "1115",
            arr_delay,
            crs_elapsed,
            actual_elapsed,
            air_time,
            flights,
            month,
            day_of_month,
            "5",
            "100",
            "200",
            o_temp,
            o_prcp,
            o_wspd,
            d_temp,
            d_prcp,
            d_wspd,
            "40.6413",
            "-73.7781",
            "33.9416",
            "-118.4085",
        ]
        return ",".join(str(f) for f in fields)

    def _create_synthetic_csv(self, dir_path: Path, rows: list, filename: str = "quality_data.csv") -> Path:
        """Helper to create a CSV with canonical header and specified rows."""
        csv_file = dir_path / filename
        header = ",".join(CANONICAL_COLUMN_NAMES)
        lines = [header] + rows
        csv_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return csv_file

    # =========================================================================
    # GROUP 1: QUALITY (Core identity, calendar dates, domains, nulls, weather)
    # =========================================================================

    def test_qual_01_valid_record_identity_accepted(self):
        """Valid record meeting all core entity anchors is classified as ACCEPTED."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row = self._make_valid_row()
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            res = classified.select(STATUS_COLUMN, REASON_COLUMN).collect()[0]
            self.assertEqual(res[STATUS_COLUMN], RecordStatus.ACCEPTED.value)
            self.assertEqual(res[REASON_COLUMN], AnomalyReason.NONE.value)

    def test_qual_02_missing_core_carrier_quarantined(self):
        """Missing or blank OP_CARRIER is quarantined with MISSING_CARRIER_CORE_ANCHOR."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_null = self._make_valid_row(op_carrier="")
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_null])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            res = classified.select(STATUS_COLUMN, REASON_COLUMN).collect()[0]
            self.assertEqual(res[STATUS_COLUMN], RecordStatus.QUARANTINED.value)
            self.assertEqual(res[REASON_COLUMN], AnomalyReason.MISSING_CARRIER_CORE_ANCHOR.value)

    def test_qual_03_missing_core_airport_quarantined(self):
        """Missing ORIGIN or DEST is quarantined with MISSING_AIRPORT_CORE_ANCHOR."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_no_dest = self._make_valid_row(dest="")
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_no_dest])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            res = classified.select(STATUS_COLUMN, REASON_COLUMN).collect()[0]
            self.assertEqual(res[STATUS_COLUMN], RecordStatus.QUARANTINED.value)
            self.assertEqual(res[REASON_COLUMN], AnomalyReason.MISSING_AIRPORT_CORE_ANCHOR.value)

    def test_qual_04_invalid_flight_number_quarantined(self):
        """Non-numeric or NaN/Inf flight number is quarantined with INVALID_FLIGHT_NUM_CORE_ANCHOR."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_bad = self._make_valid_row(fl_num="NOT_A_NUM")
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_bad])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            res = classified.select(STATUS_COLUMN, REASON_COLUMN).collect()[0]
            self.assertEqual(res[STATUS_COLUMN], RecordStatus.QUARANTINED.value)
            self.assertEqual(res[REASON_COLUMN], AnomalyReason.INVALID_FLIGHT_NUM_CORE_ANCHOR.value)

    def test_qual_05_provisional_flight_num_non_positive_accepted_and_flagged(self):
        """G3-COND-A: OP_CARRIER_FL_NUM <= 0 is ACCEPTED with provisional anomaly flag."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_zero = self._make_valid_row(fl_num="0.0")
            row_neg = self._make_valid_row(fl_num="-15.0")
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_zero, row_neg])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            results = classified.select(STATUS_COLUMN, ANOMALY_FLAGS_COLUMN).collect()
            for r in results:
                self.assertEqual(r[STATUS_COLUMN], RecordStatus.ACCEPTED.value)
                self.assertIn("PROVISIONAL_FLIGHT_NUM_NON_POSITIVE_G3_COND_A", r[ANOMALY_FLAGS_COLUMN])

    def test_qual_06_calendar_date_validation_leap_year(self):
        """Real calendar date validation: 2016-02-29 is valid; 2016-02-30 and 2019-02-29 are quarantined."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_valid_leap = self._make_valid_row(fl_date="2016-02-29")
            row_impossible_feb = self._make_valid_row(fl_date="2016-02-30")
            row_non_leap_feb = self._make_valid_row(fl_date="2019-02-29")

            csv_path = self._create_synthetic_csv(
                Path(tmp_dir),
                [row_valid_leap, row_impossible_feb, row_non_leap_feb],
            )
            reader = RawCsvReader(self.spark)
            # Read without source_year restriction so year mismatch doesn't shadow calendar test
            df = reader.read_raw(csv_path)
            classified = IngestionRecordClassifier.classify(df)

            rows = classified.select("FL_DATE", STATUS_COLUMN, REASON_COLUMN).collect()
            res_map = {r["FL_DATE"]: (r[STATUS_COLUMN], r[REASON_COLUMN]) for r in rows}

            self.assertEqual(res_map["2016-02-29"][0], RecordStatus.ACCEPTED.value)
            self.assertEqual(res_map["2016-02-30"][0], RecordStatus.QUARANTINED.value)
            self.assertEqual(res_map["2016-02-30"][1], AnomalyReason.INVALID_FL_DATE_CORE_ANCHOR.value)
            self.assertEqual(res_map["2019-02-29"][0], RecordStatus.QUARANTINED.value)
            self.assertEqual(res_map["2019-02-29"][1], AnomalyReason.INVALID_FL_DATE_CORE_ANCHOR.value)

    def test_qual_07_source_year_mismatch_quarantined(self):
        """FL_DATE year mismatch against source file year is quarantined with SOURCE_YEAR_DATE_MISMATCH."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_mismatch = self._make_valid_row(fl_date="2017-06-15")
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_mismatch])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            res = classified.select(STATUS_COLUMN, REASON_COLUMN).collect()[0]
            self.assertEqual(res[STATUS_COLUMN], RecordStatus.QUARANTINED.value)
            self.assertEqual(res[REASON_COLUMN], AnomalyReason.SOURCE_YEAR_DATE_MISMATCH.value)

    def test_qual_08_metric_invalidity_preserves_accepted_record(self):
        """DC-12: Non-numeric raw delay strings do NOT quarantine whole flight; cast to NULL in curated."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_bad_delay = self._make_valid_row(dep_delay="UNKNOWN_DELAY")
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_bad_delay])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            res = classified.select(STATUS_COLUMN, ANOMALY_FLAGS_COLUMN).collect()[0]
            self.assertEqual(res[STATUS_COLUMN], RecordStatus.ACCEPTED.value)
            self.assertIn("METRIC_NON_NUMERIC_RAW_TOKEN_DC12", res[ANOMALY_FLAGS_COLUMN])

            # In curated transformation, it safely try_casts to NULL
            curated = IngestionTransformer.to_curated(classified)
            cur_res = curated.select("DEP_DELAY").collect()[0]
            self.assertIsNone(cur_res["DEP_DELAY"])

    def test_qual_09_signed_negative_delay_preserved(self):
        """Preserves signed negative delays (early arrivals/departures) per KPI-02..06."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_early = self._make_valid_row(dep_delay="-12.0", arr_delay="-25.0")
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_early])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            curated = IngestionTransformer.to_curated(df, filter_accepted=False)

            cur_res = curated.select("DEP_DELAY", "ARR_DELAY").collect()[0]
            self.assertEqual(cur_res["DEP_DELAY"], -12.0)
            self.assertEqual(cur_res["ARR_DELAY"], -25.0)

            # Check predicates
            pred_df = QualityEngine.attach_metric_validity_flags(curated)
            p_res = pred_df.select("is_valid_dep_delay", "is_valid_arr_delay").collect()[0]
            self.assertTrue(p_res["is_valid_dep_delay"])
            self.assertTrue(p_res["is_valid_arr_delay"])

    def test_qual_10_duration_metrics_domain_boundaries(self):
        """Duration metrics must satisfy domain boundaries (taxi >= 0, air_time > 0, elapsed > 0)."""
        test_cases = [
            # (taxi_out, taxi_in, air_time, actual_elapsed, crs_elapsed, exp_to, exp_ti, exp_at, exp_ae, exp_ce)
            ("0.0", "0.0", "1.0", "1.0", "1.0", True, True, True, True, True),
            ("-1.0", "5.0", "100.0", "110.0", "115.0", False, True, True, True, True),
            ("10.0", "-0.1", "100.0", "110.0", "115.0", True, False, True, True, True),
            ("10.0", "5.0", "0.0", "110.0", "115.0", True, True, False, True, True),
            ("10.0", "5.0", "100.0", "-5.0", "115.0", True, True, True, False, True),
            ("10.0", "5.0", "100.0", "110.0", "0.0", True, True, True, True, False),
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            rows = [
                self._make_valid_row(
                    taxi_out=tc[0],
                    taxi_in=tc[1],
                    air_time=tc[2],
                    actual_elapsed=tc[3],
                    crs_elapsed=tc[4],
                )
                for tc in test_cases
            ]
            csv_path = self._create_synthetic_csv(Path(tmp_dir), rows)
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            curated = IngestionTransformer.to_curated(df, filter_accepted=False)
            flagged = QualityEngine.attach_metric_validity_flags(curated)

            eval_rows = flagged.select(
                "is_valid_taxi_out",
                "is_valid_taxi_in",
                "is_valid_air_time",
                "is_valid_actual_elapsed_time",
                "is_valid_crs_elapsed_time",
            ).collect()

            for i, tc in enumerate(test_cases):
                r = eval_rows[i]
                self.assertEqual(r["is_valid_taxi_out"], tc[5], f"Case {i} taxi_out")
                self.assertEqual(r["is_valid_taxi_in"], tc[6], f"Case {i} taxi_in")
                self.assertEqual(r["is_valid_air_time"], tc[7], f"Case {i} air_time")
                self.assertEqual(r["is_valid_actual_elapsed_time"], tc[8], f"Case {i} actual_elapsed")
                self.assertEqual(r["is_valid_crs_elapsed_time"], tc[9], f"Case {i} crs_elapsed")

    def test_qual_11_weather_absence_allowed(self):
        """FP-DEC-017: Null or blank weather columns do NOT reject or quarantine flight."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_no_weather = self._make_valid_row(
                o_temp="", o_prcp="", o_wspd="", d_temp="", d_prcp="", d_wspd=""
            )
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_no_weather])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            res = classified.select(STATUS_COLUMN, REASON_COLUMN).collect()[0]
            self.assertEqual(res[STATUS_COLUMN], RecordStatus.ACCEPTED.value)
            self.assertEqual(res[REASON_COLUMN], AnomalyReason.NONE.value)

    def test_qual_12_duplicate_records_preserved(self):
        """FP-DEC-010 / OR-02: Exact duplicate records (YX 3624) are preserved and get unique lineage IDs."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_a = self._make_valid_row(op_carrier="YX", fl_num="3624.0")
            row_b = self._make_valid_row(op_carrier="YX", fl_num="3624.0")
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_a, row_b])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016, attach_lineage=True)

            rows = df.select("_record_lineage_id").collect()
            self.assertEqual(len(rows), 2)
            # Deterministic rank disambiguation ensures lineage IDs are unique
            self.assertNotEqual(rows[0]["_record_lineage_id"], rows[1]["_record_lineage_id"])

    def test_qual_13_ansi_mode_safe_metric_predicates_on_raw_strings(self):
        """DC-12: Full metric evaluation directly on raw StringType DataFrame under ANSI mode.
        Ensures no SparkNumberFormatException or runtime crash when raw metric columns contain
        malformed non-numeric tokens across all 7 CORE measures. Metric invalidity decrements
        count_metric_valid without quarantining the records."""
        orig_ansi = self.spark.conf.get("spark.sql.ansi.enabled", "false")
        try:
            self.spark.conf.set("spark.sql.ansi.enabled", "true")
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Row 1: Valid numeric strings across all 7 measures with negative delays
                row1 = self._make_valid_row(
                    fl_date="2016-01-01",
                    dep_delay="-15.0",
                    arr_delay="-20.0",
                    taxi_out="12.0",
                    taxi_in="6.0",
                    air_time="300.0",
                    actual_elapsed="318.0",
                    crs_elapsed="330.0",
                )
                # Row 2: Malformed string tokens across all 7 measures
                row2 = self._make_valid_row(
                    fl_date="2016-01-02",
                    dep_delay="UNKNOWN_DELAY",
                    arr_delay="NA",
                    taxi_out="BAD_NUM",
                    taxi_in="-5.0",          # negative taxi_in (violates domain >= 0)
                    air_time="0.0",          # zero air_time (violates domain > 0)
                    actual_elapsed="INVALID",
                    crs_elapsed="-10.0",     # negative crs_elapsed (violates domain > 0)
                )

                csv_path = self._create_synthetic_csv(Path(tmp_dir), [row1, row2])
                reader = RawCsvReader(self.spark)
                raw_df = reader.read_raw(csv_path, source_year=2016)

                engine = QualityEngine()
                augmented_df, result = engine.evaluate(
                    raw_df,
                    independent_raw_count=2,
                    source_year=2016,
                    analyze_coverage=True,
                    profile_provisional_policy=True,
                )

                # Both records remain ACCEPTED (metric errors do NOT quarantine records)
                self.assertEqual(result.accepted_count, 2)
                self.assertEqual(result.quarantined_count, 0)
                self.assertEqual(result.rejected_count, 0)
                self.assertTrue(result.row_accounting.is_balanced())

                # Check metric accounting for Row 1 vs Row 2
                # Row 1 is valid on all 7 measures; Row 2 is invalid on all 7 measures
                for m_name in [
                    "ARR_DELAY",
                    "DEP_DELAY",
                    "TAXI_OUT",
                    "TAXI_IN",
                    "AIR_TIME",
                    "ACTUAL_ELAPSED_TIME",
                    "CRS_ELAPSED_TIME",
                ]:
                    m_acct = result.metric_accounting[m_name]
                    self.assertEqual(m_acct.count_records, 2)
                    self.assertEqual(
                        m_acct.count_metric_valid,
                        1,
                        f"Metric {m_name} valid count mismatch under ANSI mode",
                    )
                    self.assertAlmostEqual(m_acct.calculate_metric_valid_rate(), 0.5)

                # Verify augmented_df boolean columns
                flag_rows = (
                    augmented_df.select(
                        "FL_DATE",
                        "is_valid_arr_delay",
                        "is_valid_dep_delay",
                        "is_valid_taxi_out",
                        "is_valid_taxi_in",
                        "is_valid_air_time",
                        "is_valid_actual_elapsed_time",
                        "is_valid_crs_elapsed_time",
                    )
                    .orderBy("FL_DATE")
                    .collect()
                )

                # Row 1: all True
                self.assertTrue(flag_rows[0]["is_valid_arr_delay"])
                self.assertTrue(flag_rows[0]["is_valid_dep_delay"])
                self.assertTrue(flag_rows[0]["is_valid_taxi_out"])
                self.assertTrue(flag_rows[0]["is_valid_taxi_in"])
                self.assertTrue(flag_rows[0]["is_valid_air_time"])
                self.assertTrue(flag_rows[0]["is_valid_actual_elapsed_time"])
                self.assertTrue(flag_rows[0]["is_valid_crs_elapsed_time"])

                # Row 2: all False
                self.assertFalse(flag_rows[1]["is_valid_arr_delay"])
                self.assertFalse(flag_rows[1]["is_valid_dep_delay"])
                self.assertFalse(flag_rows[1]["is_valid_taxi_out"])
                self.assertFalse(flag_rows[1]["is_valid_taxi_in"])
                self.assertFalse(flag_rows[1]["is_valid_air_time"])
                self.assertFalse(flag_rows[1]["is_valid_actual_elapsed_time"])
                self.assertFalse(flag_rows[1]["is_valid_crs_elapsed_time"])
        finally:
            self.spark.conf.set("spark.sql.ansi.enabled", orig_ansi)

    # =========================================================================
    # GROUP 2: ACCOUNTING (DC-11, DC-12, zero denominator, independent raw count)
    # =========================================================================

    def test_acct_01_three_state_disjoint_balance_success(self):
        """DC-11: N_raw == N_accepted + N_quarantined + N_rejected verified successfully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_acc = self._make_valid_row()
            row_quar = self._make_valid_row(op_carrier="")  # quarantined
            row_rej = "SHORT,ROW,ONLY,FOUR,TOKENS"            # syntax rejected

            # Write raw file directly
            csv_file = Path(tmp_dir) / "mixed.csv"
            header = ",".join(CANONICAL_COLUMN_NAMES)
            csv_file.write_text(f"{header}\n{row_acc}\n{row_quar}\n{row_rej}\n", encoding="utf-8")

            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_file, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            # Independent count = 3 rows
            acct = QualityAccountingEngine.compute_and_verify_row_accounting(
                classified,
                independent_raw_count=3,
            )
            self.assertEqual(acct.raw_row_count, 3)
            self.assertEqual(acct.accepted_row_count, 1)
            self.assertEqual(acct.quarantined_row_count, 1)
            self.assertEqual(acct.rejected_row_count, 1)
            self.assertTrue(acct.is_balanced())
            self.assertAlmostEqual(acct.calculate_ingest_acceptance_rate(), 1 / 3)

    def test_acct_02_independent_raw_count_discrepancy_fails_closed(self):
        """DC-11: Discrepancy between independent count and classifier sum raises AccountingBalanceError."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_acc = self._make_valid_row()
            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_acc])
            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(df)

            # Claimed independent count = 2, but actual rows = 1
            with self.assertRaises(AccountingBalanceError):
                QualityAccountingEngine.compute_and_verify_row_accounting(
                    classified,
                    independent_raw_count=2,
                )

    def test_acct_03_negative_accounting_counts_rejected(self):
        """Negative counts in RowAccounting raise ValueError / AccountingBalanceError."""
        with self.assertRaises(ValueError):
            RowAccounting(raw_row_count=-1, accepted_row_count=0, quarantined_row_count=0, rejected_row_count=0)

        with self.assertRaises(ValueError):
            RowAccounting(raw_row_count=10, accepted_row_count=-5, quarantined_row_count=10, rejected_row_count=5)

    def test_acct_04_metric_valid_bound_enforced(self):
        """DC-12: count_metric_valid cannot exceed count_records."""
        with self.assertRaises(ValueError):
            MetricAccounting(metric_name="ARR_DELAY", count_records=10, count_metric_valid=15)

    def test_acct_05_zero_denominator_handled_cleanly(self):
        """ZERO_DENOMINATOR returns None without division by zero error for both row and metric accounting."""
        row_acct = RowAccounting(raw_row_count=0, accepted_row_count=0, quarantined_row_count=0, rejected_row_count=0)
        self.assertTrue(row_acct.is_balanced())
        self.assertIsNone(row_acct.calculate_ingest_acceptance_rate())

        metric_acct = MetricAccounting(metric_name="DEP_DELAY", count_records=0, count_metric_valid=0)
        self.assertIsNone(metric_acct.calculate_metric_valid_rate())
        self.assertEqual(metric_acct.excluded_count, 0)

    def test_acct_06_multi_source_reconciliation(self):
        """Multi-source accounting verifies per-source balances and total aggregate balance."""
        acct_2016 = RowAccounting(raw_row_count=100, accepted_row_count=90, quarantined_row_count=8, rejected_row_count=2)
        acct_2017 = RowAccounting(raw_row_count=200, accepted_row_count=180, quarantined_row_count=15, rejected_row_count=5)

        agg = QualityAccountingEngine.reconcile_multi_source_accounting(
            {"2016": acct_2016, "2017": acct_2017},
            expected_total_raw=300,
        )
        self.assertEqual(agg.raw_row_count, 300)
        self.assertEqual(agg.accepted_row_count, 270)
        self.assertEqual(agg.quarantined_row_count, 23)
        self.assertEqual(agg.rejected_row_count, 7)
        self.assertTrue(agg.is_balanced())

        # Mismatch in total expected raw count raises error
        with self.assertRaises(AccountingBalanceError):
            QualityAccountingEngine.reconcile_multi_source_accounting(
                {"2016": acct_2016, "2017": acct_2017},
                expected_total_raw=999,
            )

    # =========================================================================
    # GROUP 3: COVERAGE (DateCoverageAnalyzer, leap years, OR-05 missing March)
    # =========================================================================

    def test_cov_01_complete_normal_year(self):
        """Normal year with 365 observed dates is COMPLETE."""
        dates = [f"2017-{m:02d}-{d:02d}" for m in range(1, 13) for d in range(1, 29)]
        # Generate full 365 days for 2017
        expected_2017 = DateCoverageAnalyzer.get_expected_dates_for_year(2017)
        self.assertEqual(len(expected_2017), 365)

        df = self.spark.createDataFrame([(d,) for d in expected_2017], ["FL_DATE"])
        report = DateCoverageAnalyzer.analyze(df, target_year=2017)

        self.assertEqual(report.year, 2017)
        self.assertFalse(report.is_leap)
        self.assertEqual(report.expected_days, 365)
        self.assertEqual(report.observed_days, 365)
        self.assertEqual(report.missing_days_count, 0)
        self.assertEqual(report.source_coverage_status, "COMPLETE")
        self.assertAlmostEqual(report.coverage_ratio, 1.0)
        self.assertFalse(report.has_march_2024_defect)

    def test_cov_02_complete_leap_year(self):
        """Leap year with 366 observed dates (including Feb 29) is COMPLETE."""
        expected_2016 = DateCoverageAnalyzer.get_expected_dates_for_year(2016)
        self.assertEqual(len(expected_2016), 366)
        self.assertIn("2016-02-29", expected_2016)

        df = self.spark.createDataFrame([(d,) for d in expected_2016], ["FL_DATE"])
        report = DateCoverageAnalyzer.analyze(df, target_year=2016)

        self.assertEqual(report.year, 2016)
        self.assertTrue(report.is_leap)
        self.assertEqual(report.expected_days, 366)
        self.assertEqual(report.observed_days, 366)
        self.assertEqual(report.source_coverage_status, "COMPLETE")

    def test_cov_03_or05_missing_march_2024_defect_detected(self):
        """OR-05: Simulation of year 2024 with 335 observed days and missing 31 days of March."""
        expected_2024 = DateCoverageAnalyzer.get_expected_dates_for_year(2024)
        self.assertEqual(len(expected_2024), 366)

        # Exclude all 31 days of March 2024
        observed_2024 = [d for d in expected_2024 if not d.startswith("2024-03-")]
        self.assertEqual(len(observed_2024), 335)

        df = self.spark.createDataFrame([(d,) for d in observed_2024], ["FL_DATE"])
        report = DateCoverageAnalyzer.analyze(df, target_year=2024)

        self.assertEqual(report.year, 2024)
        self.assertTrue(report.is_leap)
        self.assertEqual(report.expected_days, 366)
        self.assertEqual(report.observed_days, 335)
        self.assertEqual(report.missing_days_count, 31)
        self.assertEqual(report.source_coverage_status, "PARTIAL")
        self.assertTrue(report.has_march_2024_defect)
        self.assertTrue(report.is_march_missing)
        self.assertTrue(report.is_exact_or05_pattern)
        self.assertAlmostEqual(report.coverage_ratio, 335 / 366)

    def test_cov_04_missing_feb_29_and_out_of_year_dates(self):
        """Detects missing Feb 29 in leap year and detects out-of-year dates."""
        expected_2020 = DateCoverageAnalyzer.get_expected_dates_for_year(2020)
        # Drop Feb 29 and add an out-of-year date
        dates = [d for d in expected_2020 if d != "2020-02-29"] + ["2019-12-31"]

        df = self.spark.createDataFrame([(d,) for d in dates], ["FL_DATE"])
        report = DateCoverageAnalyzer.analyze(df, target_year=2020)

        self.assertIn("2020-02-29", report.missing_dates)
        self.assertEqual(report.missing_days_count, 1)
        self.assertEqual(report.out_of_year_count, 1)
        self.assertIn("2019-12-31", report.out_of_year_dates)
        self.assertEqual(report.source_coverage_status, "PARTIAL")

    def test_cov_05_empty_2024_cohort_does_not_flag_or05_defect(self):
        """Empty 2024 cohort (0 observed days) must NOT be flagged as OR-05 March defect."""
        from pyspark.sql.types import StructType, StructField, StringType
        schema = StructType([StructField("FL_DATE", StringType(), True)])
        empty_df = self.spark.createDataFrame([], schema)
        report = DateCoverageAnalyzer.analyze(empty_df, target_year=2024)

        self.assertEqual(report.year, 2024)
        self.assertTrue(report.is_leap)
        self.assertEqual(report.expected_days, 366)
        self.assertEqual(report.observed_days, 0)
        self.assertEqual(report.missing_days_count, 366)
        self.assertEqual(report.source_coverage_status, "PARTIAL")
        self.assertEqual(report.coverage_ratio, 0.0)
        self.assertFalse(report.has_march_2024_defect)
        self.assertFalse(report.is_march_missing)
        self.assertFalse(report.is_exact_or05_pattern)

    def test_cov_06_march_plus_other_months_missing_not_exact_or05_pattern(self):
        """Missing March + April: is_march_missing is True, but is_exact_or05_pattern is False."""
        expected_2024 = DateCoverageAnalyzer.get_expected_dates_for_year(2024)
        # Exclude March (31 days) and April (30 days)
        observed_2024 = [
            d for d in expected_2024
            if not d.startswith("2024-03-") and not d.startswith("2024-04-")
        ]
        self.assertEqual(len(observed_2024), 305)

        df = self.spark.createDataFrame([(d,) for d in observed_2024], ["FL_DATE"])
        report = DateCoverageAnalyzer.analyze(df, target_year=2024)

        self.assertEqual(report.observed_days, 305)
        self.assertEqual(report.missing_days_count, 61)
        self.assertTrue(report.is_march_missing)
        self.assertTrue(report.has_march_2024_defect)
        self.assertFalse(report.is_exact_or05_pattern)
        self.assertEqual(report.source_coverage_status, "PARTIAL")

    def test_cov_07_non_march_days_missing_does_not_flag_or05(self):
        """Missing days outside March (e.g., January) does NOT flag OR-05."""
        expected_2024 = DateCoverageAnalyzer.get_expected_dates_for_year(2024)
        # Exclude 10 days in January; March is complete
        observed_2024 = [d for d in expected_2024 if not (d.startswith("2024-01-") and int(d[-2:]) <= 10)]
        self.assertEqual(len(observed_2024), 356)

        df = self.spark.createDataFrame([(d,) for d in observed_2024], ["FL_DATE"])
        report = DateCoverageAnalyzer.analyze(df, target_year=2024)

        self.assertEqual(report.observed_days, 356)
        self.assertEqual(report.missing_days_count, 10)
        self.assertFalse(report.is_march_missing)
        self.assertFalse(report.has_march_2024_defect)
        self.assertFalse(report.is_exact_or05_pattern)
        self.assertEqual(report.source_coverage_status, "PARTIAL")

    def test_cov_08_complete_2024_does_not_flag_or05(self):
        """Complete 366 days in 2024 does NOT flag OR-05."""
        expected_2024 = DateCoverageAnalyzer.get_expected_dates_for_year(2024)
        df = self.spark.createDataFrame([(d,) for d in expected_2024], ["FL_DATE"])
        report = DateCoverageAnalyzer.analyze(df, target_year=2024)

        self.assertEqual(report.observed_days, 366)
        self.assertEqual(report.missing_days_count, 0)
        self.assertEqual(report.source_coverage_status, "COMPLETE")
        self.assertFalse(report.is_march_missing)
        self.assertFalse(report.has_march_2024_defect)
        self.assertFalse(report.is_exact_or05_pattern)

    # =========================================================================
    # GROUP 4: POLICY (G3-COND-A, unapproved policy safety, impact profiling)
    # =========================================================================

    def test_pol_01_default_policy_conforms_to_g3_cond_a(self):
        """Default policy has quarantine_non_positive_flight_num=False per G3-COND-A."""
        cfg = QualityPolicyConfig()
        self.assertFalse(cfg.quarantine_non_positive_flight_num)
        self.assertTrue(cfg.allow_weather_nulls)
        self.assertTrue(cfg.strict_record_accounting)
        self.assertTrue(cfg.strict_metric_accounting)

    def test_pol_02_enabling_hard_quarantine_without_override_raises_error(self):
        """Enacting hard quarantine for flight numbers without allow_unapproved_policies=True raises PolicyViolationError."""
        with self.assertRaises(PolicyViolationError) as ctx:
            QualityPolicyConfig(quarantine_non_positive_flight_num=True)
        self.assertIn("GOVERNANCE_VIOLATION", str(ctx.exception))
        self.assertIn("G3-COND-A", str(ctx.exception))

    def test_pol_03_disallowing_weather_nulls_raises_error(self):
        """Disallowing weather nulls without override violates FP-DEC-017 and raises PolicyViolationError."""
        with self.assertRaises(PolicyViolationError) as ctx:
            QualityPolicyConfig(allow_weather_nulls=False)
        self.assertIn("FP-DEC-017", str(ctx.exception))

    def test_pol_04_provisional_policy_profiling_simulation(self):
        """ProvisionalPolicyProfiler profiles counts, rate, carrier distribution, and simulates policies."""
        test_records = [
            ("AA", "100.0"),  # positive
            ("AA", "0.0"),    # zero
            ("DL", "-5.0"),   # negative
            ("DL", "200.0"),  # positive
            ("UA", "300.0"),  # positive
        ]
        df = self.spark.createDataFrame(test_records, ["OP_CARRIER", "OP_CARRIER_FL_NUM"])
        profile = ProvisionalPolicyProfiler.profile_flight_number_anomalies(df)

        self.assertEqual(profile.total_records, 5)
        self.assertEqual(profile.non_positive_count, 2)
        self.assertEqual(profile.zero_count, 1)
        self.assertEqual(profile.negative_count, 1)
        self.assertAlmostEqual(profile.non_positive_rate, 2 / 5)
        self.assertEqual(profile.affected_carriers, {"AA": 1, "DL": 1})
        self.assertEqual(profile.simulated_accepted_under_canonical_policy, 5)
        self.assertEqual(profile.simulated_quarantined_under_hard_policy, 2)
        self.assertEqual(profile.governance_status, "PROVISIONAL_POLICY_PENDING_REAL_DATA_VALIDATION")

    def test_pol_05_offline_policy_simulation_quarantines_non_positive_flight_nums(self):
        """Simulation mode (allow_unapproved_policies=True): quarantine_non_positive_flight_num=True
        reclassifies non-positive flight numbers to QUARANTINED while maintaining exact DC-11 row balance."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_pos = self._make_valid_row(fl_date="2016-01-01", fl_num="100.0")
            row_zero = self._make_valid_row(fl_date="2016-01-02", fl_num="0.0")
            row_neg = self._make_valid_row(fl_date="2016-01-03", fl_num="-15.0")

            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_pos, row_zero, row_neg])
            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path, source_year=2016)

            sim_policy = QualityPolicyConfig(
                quarantine_non_positive_flight_num=True,
                allow_unapproved_policies=True,
            )
            engine = QualityEngine(policy=sim_policy)
            augmented_df, result = engine.evaluate(raw_df, independent_raw_count=3)

            # In simulation: 1 positive accepted, 2 non-positive quarantined
            self.assertEqual(result.accepted_count, 1)
            self.assertEqual(result.quarantined_count, 2)
            self.assertEqual(result.rejected_count, 0)
            self.assertTrue(result.row_accounting.is_balanced())

            # Check reasons of quarantined records
            quar_reasons = (
                augmented_df.filter(F.col(STATUS_COLUMN) == RecordStatus.QUARANTINED.value)
                .select(REASON_COLUMN)
                .distinct()
                .collect()
            )
            reasons_list = [r[REASON_COLUMN] for r in quar_reasons]
            self.assertIn("PROVISIONAL_FLIGHT_NUM_NON_POSITIVE", reasons_list)

    def test_pol_06_canonical_production_never_hard_quarantines_non_positive(self):
        """Production mode (default policy): OP_CARRIER_FL_NUM <= 0 remains ACCEPTED per G3-COND-A."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_pos = self._make_valid_row(fl_date="2016-01-01", fl_num="100.0")
            row_zero = self._make_valid_row(fl_date="2016-01-02", fl_num="0.0")

            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row_pos, row_zero])
            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path, source_year=2016)

            engine = QualityEngine()  # default canonical policy
            augmented_df, result = engine.evaluate(raw_df, independent_raw_count=2)

            # In production: both remain ACCEPTED
            self.assertEqual(result.accepted_count, 2)
            self.assertEqual(result.quarantined_count, 0)
            self.assertTrue(result.row_accounting.is_balanced())

    # =========================================================================
    # GROUP 5: INTEGRATION (End-to-End Pipeline, Forensic Outputs, Determinism)
    # =========================================================================

    def test_integ_01_end_to_end_quality_pipeline(self):
        """Full pipeline: RawCsvReader -> QualityEngine -> IngestionTransformer."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 1 accepted normal, 1 accepted non-positive fl_num (G3-COND-A), 1 quarantined missing origin
            row1 = self._make_valid_row(fl_date="2016-01-01", fl_num="100.0")
            row2 = self._make_valid_row(fl_date="2016-01-02", fl_num="0.0")
            row3 = self._make_valid_row(fl_date="2016-01-03", origin="")  # quarantined

            csv_path = self._create_synthetic_csv(Path(tmp_dir), [row1, row2, row3])
            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path, source_year=2016)

            engine = QualityEngine()
            augmented_df, result = engine.evaluate(
                raw_df,
                independent_raw_count=3,
                source_year=2016,
                analyze_coverage=True,
                profile_provisional_policy=True,
            )

            # 1. Verify accounting
            self.assertEqual(result.accepted_count, 2)
            self.assertEqual(result.quarantined_count, 1)
            self.assertEqual(result.rejected_count, 0)
            self.assertTrue(result.row_accounting.is_balanced())

            # 2. Verify metric validity flags attached
            self.assertIn("is_valid_arr_delay", augmented_df.columns)
            self.assertIn("is_valid_dep_delay", augmented_df.columns)

            # 3. Verify provisional profiling result
            self.assertIsNotNone(result.provisional_policy_profile)
            self.assertEqual(result.provisional_policy_profile.zero_count, 1)

            # 4. Transform to curated Parquet schema
            curated_df = IngestionTransformer.to_curated(augmented_df, filter_accepted=True)
            self.assertEqual(curated_df.count(), 2)

            curated_schema = get_curated_parquet_schema()
            curated_field_names = [f.name for f in curated_schema.fields]
            self.assertEqual(curated_df.columns, curated_field_names)

    def test_integ_02_forensic_output_preserves_anomaly_reasons(self):
        """Forensic output ensures quarantined records have precise reasons and flags."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            row_bad_date = self._make_valid_row(fl_date="2016-02-30")
            row_missing_carrier = self._make_valid_row(op_carrier="")
            row_bad_fl_num = self._make_valid_row(fl_num="NOT_NUMERIC")

            csv_path = self._create_synthetic_csv(
                Path(tmp_dir),
                [row_bad_date, row_missing_carrier, row_bad_fl_num],
            )
            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path, source_year=2016)
            classified = IngestionRecordClassifier.classify(raw_df)

            quarantined = classified.filter(F.col(STATUS_COLUMN) == RecordStatus.QUARANTINED.value)
            rows = quarantined.select(REASON_COLUMN, ANOMALY_FLAGS_COLUMN).collect()
            reasons = [r[REASON_COLUMN] for r in rows]

            self.assertIn(AnomalyReason.INVALID_FL_DATE_CORE_ANCHOR.value, reasons)
            self.assertIn(AnomalyReason.MISSING_CARRIER_CORE_ANCHOR.value, reasons)
            self.assertIn(AnomalyReason.INVALID_FLIGHT_NUM_CORE_ANCHOR.value, reasons)

    def test_integ_03_quality_rule_catalog_traceability(self):
        """All rules in QualityRuleCatalog have valid attributes, authorities, and scopes."""
        all_rules = QualityRuleCatalog.get_all_rules()
        self.assertGreaterEqual(len(all_rules), 15)

        for rule in all_rules:
            self.assertTrue(rule.rule_id.startswith("QR-"))
            self.assertIn(rule.scope, (RuleScope.RECORD, RuleScope.METRIC, RuleScope.DATASET))
            self.assertIn(rule.severity, (RuleSeverity.ERROR, RuleSeverity.WARNING, RuleSeverity.INFO))
            self.assertIn(
                rule.consequence,
                (RuleConsequence.REJECT, RuleConsequence.QUARANTINE, RuleConsequence.METRIC_INVALID, RuleConsequence.FLAG_ONLY),
            )
            self.assertTrue(len(rule.authority) > 0)
            self.assertTrue(len(rule.description) > 0)

        provisional_rules = QualityRuleCatalog.get_provisional_rules()
        self.assertEqual(len(provisional_rules), 1)
        self.assertEqual(provisional_rules[0].rule_id, "QR-REC-07")
        self.assertTrue(provisional_rules[0].is_provisional)


if __name__ == "__main__":
    unittest.main()
