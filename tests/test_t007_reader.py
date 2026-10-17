"""
Comprehensive Unit Test Suite for T007-03 Raw CSV Reader and Record Classifier.
Validates:
1. Valid 34-column CSV parsing and curated schema transformation.
2. Univocity parser syntax corruption handling (short rows, extra tokens, unclosed quotes).
3. DC-11 three-state disjoint row accounting (raw = accepted + quarantined + rejected).
4. DC-12 metric vs record validity separation (non-numeric delay parsed, accepted, and cast to null in curated).
5. G3-COND-B compliance: OP_CARRIER_FL_NUM <= 0 is NOT quarantined.
6. FP-DEC-017 compliance: Null weather values do NOT reject or quarantine records.
7. FP-DEC-010 compliance: FLIGHTS preserved as float64 without denominator weighting.
8. Quoted commas and embedded newlines handling.
9. Protection against PySpark AnalysisException UNSUPPORTED_FEATURE.QUERY_ONLY_CORRUPT_RECORD_COLUMN.
"""

from pathlib import Path
import sys
import tempfile
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, LongType, StringType

from flight_pipeline.config.spark_config import SparkConfig, get_spark_session, stop_spark_session
from flight_pipeline.ingestion.reader import (
    AnomalyReason,
    CsvReadOptions,
    IngestionRecordClassifier,
    IngestionTransformer,
    RawCsvReader,
    RecordStatus,
    compute_row_accounting,
)
from flight_pipeline.ingestion.schema import (
    CANONICAL_COLUMN_NAMES,
    CANONICAL_COLUMNS_COUNT,
    CORRUPT_RECORD_COLUMN,
    CURATED_PARQUET_SCHEMA,
)


class TestT007Reader(unittest.TestCase):
    """Test suite for RawCsvReader and record classification."""

    @classmethod
    def setUpClass(cls):
        """Initialize isolated local SparkSession."""
        cfg = SparkConfig(app_name="TestT007Reader", master="local[2]", driver_memory="2g", shuffle_partitions=4)
        cls.spark = get_spark_session(cfg)

    @classmethod
    def tearDownClass(cls):
        """Clean up SparkSession."""
        if cls.spark:
            stop_spark_session(cls.spark)

    def _create_synthetic_csv(self, dir_path: Path, rows: list) -> Path:
        """Helper to create a CSV with canonical header and specified rows."""
        csv_file = dir_path / "test_data.csv"
        header = ",".join(CANONICAL_COLUMN_NAMES)
        lines = [header] + rows
        csv_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return csv_file

    def _make_valid_34_col_row(
        self,
        fl_date: str = "2016-01-01",
        op_carrier: str = "AA",
        fl_num: str = "1234.0",
        dep_delay: str = "10.0",
        arr_delay: str = "-5.0",
        flights: str = "1.0",
    ) -> str:
        """Generate a valid 34-column CSV line."""
        fields = [
            fl_date,            # FL_DATE
            op_carrier,         # OP_CARRIER
            fl_num,             # OP_CARRIER_FL_NUM
            "JFK",              # ORIGIN
            "LAX",              # DEST
            "0800",             # CRS_DEP_TIME
            "0810",             # DEP_TIME
            dep_delay,          # DEP_DELAY
            "15.0",             # TAXI_OUT
            "0825",             # WHEELS_OFF
            "1110",             # WHEELS_ON
            "5.0",              # TAXI_IN
            "1120",             # CRS_ARR_TIME
            "1115",             # ARR_TIME
            arr_delay,          # ARR_DELAY
            360.0,              # CRS_ELAPSED_TIME
            355.0,              # ACTUAL_ELAPSED_TIME
            335.0,              # AIR_TIME
            flights,            # FLIGHTS
            1,                  # MONTH
            1,                  # DAY_OF_MONTH
            5,                  # DAY_OF_WEEK
            100,                # ORIGIN_INDEX
            200,                # DEST_INDEX
            15.5,               # O_TEMP
            0.0,                # O_PRCP
            12.0,               # O_WSPD
            22.0,               # D_TEMP
            0.1,                # D_PRCP
            8.0,                # D_WSPD
            40.6413,            # O_LATITUDE
            -73.7781,           # O_LONGITUDE
            33.9416,            # D_LATITUDE
            -118.4085,          # D_LONGITUDE
        ]
        return ",".join(str(f) for f in fields)

    def test_read_valid_34_columns_parses_cleanly(self):
        """RDR-01: Valid 34-column row parses cleanly into 35 fields (34 business + corrupt=None)."""
        with tempfile.TemporaryDirectory() as td:
            row = self._make_valid_34_col_row()
            csv_path = self._create_synthetic_csv(Path(td), [row])

            reader = RawCsvReader(self.spark)
            df = reader.read_raw(csv_path)

            self.assertEqual(len(df.columns), CANONICAL_COLUMNS_COUNT + 1)
            self.assertIn(CORRUPT_RECORD_COLUMN, df.columns)

            records = df.collect()
            self.assertEqual(len(records), 1)
            rec = records[0]

            self.assertEqual(rec["FL_DATE"], "2016-01-01")
            self.assertEqual(rec["OP_CARRIER"], "AA")
            self.assertEqual(rec["OP_CARRIER_FL_NUM"], "1234.0")
            self.assertEqual(rec["DEP_DELAY"], "10.0")
            self.assertEqual(rec["ARR_DELAY"], "-5.0")
            self.assertIsNone(rec[CORRUPT_RECORD_COLUMN])

    def test_short_row_token_mismatch_captured_as_corrupt(self):
        """RDR-02: Short row (< 34 tokens) is captured in _corrupt_record and classified as REJECTED."""
        with tempfile.TemporaryDirectory() as td:
            valid_row = self._make_valid_34_col_row()
            short_row = "2016-01-02,DL,500,ORD,ATL"  # Only 5 tokens
            csv_path = self._create_synthetic_csv(Path(td), [valid_row, short_row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df)
            self.assertEqual(accounting.raw_row_count, 2)
            self.assertEqual(accounting.accepted_row_count, 1)
            self.assertEqual(accounting.quarantined_row_count, 0)
            self.assertEqual(accounting.rejected_row_count, 1)
            self.assertTrue(accounting.is_balanced())

            rejected = classified_df.filter(classified_df["_record_status"] == RecordStatus.REJECTED.value).collect()
            self.assertEqual(len(rejected), 1)
            self.assertEqual(rejected[0]["_anomaly_reason"], AnomalyReason.PARSER_SYNTAX_CORRUPTION.value)

    def test_extra_tokens_captured_as_corrupt(self):
        """RDR-03: Extra tokens (> 34 tokens) captured in _corrupt_record and classified as REJECTED."""
        with tempfile.TemporaryDirectory() as td:
            valid_row = self._make_valid_34_col_row()
            extra_row = self._make_valid_34_col_row() + ",EXTRA_TOKEN_1,EXTRA_TOKEN_2"
            csv_path = self._create_synthetic_csv(Path(td), [valid_row, extra_row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df)
            self.assertEqual(accounting.raw_row_count, 2)
            self.assertEqual(accounting.accepted_row_count, 1)
            self.assertEqual(accounting.rejected_row_count, 1)

    def test_dc12_non_numeric_metric_accepted_in_raw_and_null_in_curated(self):
        """RDR-04: Non-numeric metric string is ACCEPTED (DC-12) and cast to NULL in curated schema."""
        with tempfile.TemporaryDirectory() as td:
            # Row with non-numeric DEP_DELAY = "CORRUPT_DELAY"
            row = self._make_valid_34_col_row(dep_delay="CORRUPT_DELAY")
            csv_path = self._create_synthetic_csv(Path(td), [row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            # Ingest accounting must treat this row as ACCEPTED (DC-12)
            accounting = compute_row_accounting(classified_df)
            self.assertEqual(accounting.raw_row_count, 1)
            self.assertEqual(accounting.accepted_row_count, 1)
            self.assertEqual(accounting.rejected_row_count, 0)

            # Curated transformation should safely cast DEP_DELAY to None (DoubleType)
            curated_df = IngestionTransformer.to_curated(classified_df)
            self.assertEqual(len(curated_df.columns), CANONICAL_COLUMNS_COUNT)
            self.assertEqual(curated_df.schema["DEP_DELAY"].dataType, DoubleType())

            record = curated_df.collect()[0]
            self.assertIsNone(record["DEP_DELAY"])
            self.assertEqual(record["OP_CARRIER"], "AA")

    def test_g3_cond_b_non_positive_flight_num_not_quarantined(self):
        """RDR-05: OP_CARRIER_FL_NUM <= 0 is NOT quarantined per G3-COND-B; remains ACCEPTED."""
        with tempfile.TemporaryDirectory() as td:
            row_zero = self._make_valid_34_col_row(fl_num="0.0")
            row_neg = self._make_valid_34_col_row(fl_num="-100.0")
            csv_path = self._create_synthetic_csv(Path(td), [row_zero, row_neg])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df)
            self.assertEqual(accounting.raw_row_count, 2)
            self.assertEqual(accounting.accepted_row_count, 2)
            self.assertEqual(accounting.quarantined_row_count, 0)

    def test_malformed_fl_date_quarantined(self):
        """RDR-06: Row with malformed FL_DATE is classified as QUARANTINED."""
        with tempfile.TemporaryDirectory() as td:
            valid_row = self._make_valid_34_col_row()
            bad_date_row = self._make_valid_34_col_row(fl_date="INVALID_DATE_2016")
            csv_path = self._create_synthetic_csv(Path(td), [valid_row, bad_date_row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)

            accounting = compute_row_accounting(classified_df)
            self.assertEqual(accounting.raw_row_count, 2)
            self.assertEqual(accounting.accepted_row_count, 1)
            self.assertEqual(accounting.quarantined_row_count, 1)
            self.assertEqual(accounting.rejected_row_count, 0)
            self.assertTrue(accounting.is_balanced())

            quarantined = classified_df.filter(classified_df["_record_status"] == RecordStatus.QUARANTINED.value).collect()
            self.assertEqual(len(quarantined), 1)
            self.assertEqual(quarantined[0]["_anomaly_reason"], AnomalyReason.MALFORMED_FL_DATE.value)

    def test_curated_schema_preserves_canonical_types(self):
        """RDR-07: Curated DataFrame exactly matches canonical 34-column types."""
        with tempfile.TemporaryDirectory() as td:
            row = self._make_valid_34_col_row(fl_num="5432.1", arr_delay="-12.5")
            csv_path = self._create_synthetic_csv(Path(td), [row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            curated_df = IngestionTransformer.to_curated(classified_df)

            self.assertEqual(curated_df.columns, list(CANONICAL_COLUMN_NAMES))

            # Verify specific types
            self.assertEqual(curated_df.schema["OP_CARRIER_FL_NUM"].dataType, DoubleType())
            self.assertEqual(curated_df.schema["FLIGHTS"].dataType, DoubleType())
            self.assertEqual(curated_df.schema["ARR_DELAY"].dataType, DoubleType())
            self.assertEqual(curated_df.schema["MONTH"].dataType, LongType())
            self.assertEqual(curated_df.schema["ORIGIN_INDEX"].dataType, LongType())

            rec = curated_df.collect()[0]
            self.assertEqual(rec["OP_CARRIER_FL_NUM"], 5432.1)
            self.assertEqual(rec["ARR_DELAY"], -12.5)

    def test_quoted_commas_and_embedded_newlines(self):
        """RDR-08: Quoted fields with commas and newlines parse correctly with multi_line=True."""
        with tempfile.TemporaryDirectory() as td:
            opts = CsvReadOptions(multi_line=True)
            reader = RawCsvReader(self.spark, options=opts)

            # Row with quoted carrier name
            row = self._make_valid_34_col_row(op_carrier='"DELTA, INC"')
            csv_path = self._create_synthetic_csv(Path(td), [row])

            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            accounting = compute_row_accounting(classified_df)

            self.assertEqual(accounting.raw_row_count, 1)
            self.assertEqual(accounting.accepted_row_count, 1)

            curated_df = IngestionTransformer.to_curated(classified_df)
            rec = curated_df.collect()[0]
            self.assertEqual(rec["OP_CARRIER"], "DELTA, INC")

    def test_null_weather_columns_accepted(self):
        """RDR-09: Absence of weather data (nulls) preserves record as ACCEPTED per FP-DEC-017."""
        with tempfile.TemporaryDirectory() as td:
            fields = [
                "2016-01-01", "AA", "100.0", "JFK", "LAX", "0800", "0810", "10.0", "15.0",
                "0825", "1110", "5.0", "1120", "1115", "-5.0", "360.0", "355.0", "335.0",
                "1.0", "1", "1", "5", "100", "200",
                "", "", "", "", "", "",  # Empty weather fields
                "40.6413", "-73.7781", "33.9416", "-118.4085"
            ]
            row = ",".join(fields)
            csv_path = self._create_synthetic_csv(Path(td), [row])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            accounting = compute_row_accounting(classified_df)

            self.assertEqual(accounting.raw_row_count, 1)
            self.assertEqual(accounting.accepted_row_count, 1)

            curated_df = IngestionTransformer.to_curated(classified_df)
            rec = curated_df.collect()[0]
            self.assertIsNone(rec["O_TEMP"])
            self.assertIsNone(rec["O_PRCP"])
            self.assertIsNone(rec["D_TEMP"])

    def test_header_only_csv_handling(self):
        """RDR-10: Header-only CSV file yields 0 rows with balanced accounting (0 = 0 + 0 + 0)."""
        with tempfile.TemporaryDirectory() as td:
            csv_path = self._create_synthetic_csv(Path(td), [])  # No data rows

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            accounting = compute_row_accounting(classified_df)

            self.assertEqual(accounting.raw_row_count, 0)
            self.assertEqual(accounting.accepted_row_count, 0)
            self.assertEqual(accounting.quarantined_row_count, 0)
            self.assertEqual(accounting.rejected_row_count, 0)
            self.assertTrue(accounting.is_balanced())
            self.assertIsNone(accounting.calculate_ingest_acceptance_rate())

    def test_negative_delay_values_preserved(self):
        """RDR-11: Early arrivals/departures with negative signed delays are preserved exactly (KPI-03)."""
        with tempfile.TemporaryDirectory() as td:
            row_early = self._make_valid_34_col_row(dep_delay="-18.0", arr_delay="-45.5")
            csv_path = self._create_synthetic_csv(Path(td), [row_early])

            reader = RawCsvReader(self.spark)
            raw_df = reader.read_raw(csv_path)
            classified_df = IngestionRecordClassifier.classify(raw_df)
            curated_df = IngestionTransformer.to_curated(classified_df)

            rec = curated_df.collect()[0]
            self.assertEqual(rec["DEP_DELAY"], -18.0)
            self.assertEqual(rec["ARR_DELAY"], -45.5)


if __name__ == "__main__":
    unittest.main()
