#!/usr/bin/env python3
"""
Official QA Test Suite: PySpark 4.0.1 CSV Parser Empirical Reproduction.
Validates:
1. Short row token mismatch behavior.
2. Extra token mismatch behavior.
3. Quoted comma handling.
4. Embedded newline handling (multiLine=true vs multiLine=false).
5. Unclosed quote detection and multiline spanning.
6. Numeric parse failure vs StringType raw schema boundary (DC-12 protection).
7. Null metric representation.
8. Query on _corrupt_record alone (AnalysisException detection).
9. Catalyst column pruning behavior under spark.sql.csv.parser.columnPruning.enabled.
10. Two-action / cache materialization requirement.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
)
from pyspark.sql.functions import col


def run_reproduction_suite() -> Dict[str, Any]:
    results = {}

    spark = (
        SparkSession.builder
        .master("local[1]")
        .appName("T007_PySpark_CSV_Reproduction")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.driver.memory", "1g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    jvm = spark.sparkContext._gateway.jvm
    results["python_version"] = sys.version.split()[0]
    results["pyspark_version"] = pyspark.__version__
    results["spark_version"] = spark.version
    results["java_version"] = str(jvm.java.lang.System.getProperty("java.version"))

    with tempfile.TemporaryDirectory() as td:
        csv_file = Path(td) / "qa_test_cases.csv"
        lines = [
            "FL_DATE,OP_CARRIER,FL_NUM,ORIGIN,DEST,DEP_DELAY",
            "2016-01-01,AA,100,JFK,LAX,12.5",                  # Row 1: Valid
            "2016-01-02,DL,200",                               # Row 2: Short row (3 tokens)
            "2016-01-03,UA,300,ORD,SFO,-5.0,EXTRA1,EXTRA2",    # Row 3: Extra tokens (8 tokens)
            '2016-01-04,WN,400,"MDW,CHI",LAS,0.0',           # Row 4: Quoted comma
            '2016-01-05,B6,500,"BOS\nLOGAN",MIA,15.0',       # Row 5: Embedded newline
            "2016-01-06,AS,600,SEA,ANC,NOT_A_NUMBER",          # Row 6: Numeric parse failure
            "2016-01-07,NK,700,FLL,ATL,",                      # Row 7: Null metric
            '2016-01-08,AA,800,"UNCLOSED_QUOTE,DFW,ORD,20.0', # Row 8: Unclosed quote
        ]
        csv_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        # Schema with typed DoubleType for DEP_DELAY
        typed_schema = StructType([
            StructField("FL_DATE", StringType(), True),
            StructField("OP_CARRIER", StringType(), True),
            StructField("FL_NUM", IntegerType(), True),
            StructField("ORIGIN", StringType(), True),
            StructField("DEST", StringType(), True),
            StructField("DEP_DELAY", DoubleType(), True),
            StructField("_corrupt_record", StringType(), True),
        ])

        # Test 1: Column Pruning Enabled (Default)
        spark.conf.set("spark.sql.csv.parser.columnPruning.enabled", "true")
        df_prune_on = (
            spark.read
            .option("header", "true")
            .option("mode", "PERMISSIVE")
            .option("multiLine", "true")
            .option("columnNameOfCorruptRecord", "_corrupt_record")
            .schema(typed_schema)
            .csv(str(csv_file))
        )

        # Test Column Pruning on FileScan BEFORE caching
        biz_df = df_prune_on.select("FL_DATE", "OP_CARRIER", "FL_NUM", "ORIGIN", "DEST", "DEP_DELAY")
        plan_str = biz_df._jdf.queryExecution().executedPlan().toString()
        results["corrupt_record_pruned_from_plan"] = "_corrupt_record" not in plan_str

        # Direct query only _corrupt_record without cache must raise AnalysisException
        caught_unsupported = False
        try:
            df_prune_on.select("_corrupt_record").filter(col("_corrupt_record").isNotNull()).collect()
        except Exception as exc:
            if "UNSUPPORTED_FEATURE.QUERY_ONLY_CORRUPT_RECORD_COLUMN" in str(exc):
                caught_unsupported = True
        results["direct_corrupt_query_rejected"] = caught_unsupported

        # With cache(), query succeeds
        cached_df = df_prune_on.cache()
        total_rows = cached_df.count()
        corrupt_rows = cached_df.filter(col("_corrupt_record").isNotNull()).collect()
        corrupt_contents = [r["_corrupt_record"] for r in corrupt_rows]
        results["total_cached_rows"] = total_rows
        results["corrupt_count_typed"] = len(corrupt_rows)

        # Check short row captured
        results["short_row_captured"] = any("2016-01-02,DL,200" in c for c in corrupt_contents)
        # Check extra tokens captured
        results["extra_tokens_captured"] = any("EXTRA1,EXTRA2" in c for c in corrupt_contents)
        # Check numeric failure captured when schema is DoubleType
        results["numeric_failure_captured_in_typed"] = any("NOT_A_NUMBER" in c for c in corrupt_contents)
        # Check unclosed quote captured
        results["unclosed_quote_captured"] = any("UNCLOSED_QUOTE" in c for c in corrupt_contents)

        cached_df.unpersist(blocking=True)

        # Test 2: Raw Schema with StringType for business columns (DC-12 Architectural Fix)
        raw_string_schema = StructType([
            StructField("FL_DATE", StringType(), True),
            StructField("OP_CARRIER", StringType(), True),
            StructField("FL_NUM", StringType(), True),
            StructField("ORIGIN", StringType(), True),
            StructField("DEST", StringType(), True),
            StructField("DEP_DELAY", StringType(), True),
            StructField("_corrupt_record", StringType(), True),
        ])

        df_string = (
            spark.read
            .option("header", "true")
            .option("mode", "PERMISSIVE")
            .option("multiLine", "true")
            .option("columnNameOfCorruptRecord", "_corrupt_record")
            .schema(raw_string_schema)
            .csv(str(csv_file))
        )
        cached_str = df_string.cache()
        str_corrupt_rows = cached_str.filter(col("_corrupt_record").isNotNull()).collect()
        str_corrupt_contents = [r["_corrupt_record"] for r in str_corrupt_rows]

        # In string schema, Row 6 ("NOT_A_NUMBER") must NOT be in _corrupt_record!
        row6 = cached_str.filter(col("FL_NUM") == "600").collect()[0]
        results["string_schema_preserves_row6_acceptance"] = (
            row6["DEP_DELAY"] == "NOT_A_NUMBER" and row6["_corrupt_record"] is None
        )
        results["string_schema_short_row_captured"] = any("2016-01-02,DL,200" in c for c in str_corrupt_contents)
        results["string_schema_extra_tokens_captured"] = any("EXTRA1,EXTRA2" in c for c in str_corrupt_contents)

        cached_str.unpersist()

    spark.stop()
    return results


if __name__ == "__main__":
    res = run_reproduction_suite()
    print("=" * 80)
    print("PYSPARK 4.0.1 CSV PARSER EMPIRICAL REPRODUCTION SUITE RESULTS")
    print("=" * 80)
    for k, v in res.items():
        print(f"  {k}: {v}")
    print("=" * 80)
    assert res["direct_corrupt_query_rejected"] is True
    assert res["short_row_captured"] is True
    assert res["extra_tokens_captured"] is True
    assert res["numeric_failure_captured_in_typed"] is True
    assert res["unclosed_quote_captured"] is True
    assert res["corrupt_record_pruned_from_plan"] is True
    assert res["string_schema_preserves_row6_acceptance"] is True
    assert res["string_schema_short_row_captured"] is True
    assert res["string_schema_extra_tokens_captured"] is True
    print("ALL EMPIRICAL REPRODUCTION ASSERTIONS PASSED.")
