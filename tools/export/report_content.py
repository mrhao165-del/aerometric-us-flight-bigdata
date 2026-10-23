# -*- coding: utf-8 -*-
"""
tools/export/report_content.py
Structured content, metadata, and tables for T-016 deliverables.
"""

PROJECT_METADATA = {
    "project_name": "Phân tích hiệu suất khai thác chuyến bay nội địa Hoa Kỳ 2016–2024",
    "framework": "Apache Spark / PySpark & Big Data Columnar Storage",
    "curated_records": 54674003,
    "curated_files": 117,
    "curated_bytes": 3308617408,
    "years": "2016–2024 (9 năm quan sát; năm 2024 quan sát 11 tháng theo OR-05)",
    "kpi_run_id": "kpi_run_2016_2024_v1",
    "kpi_records": 684180,
    "kpi_cohorts": 57015,
    "kpi_streams": 12,
    "analysis_run_id": "t014_analysis_2016_2024_v4",
    "analytics_tables_count": 12,
    "analytics_figures_count": 16,
    "results_count": 20,
    "gate": "G7",
    "task": "T-016",
    "status": "READY_FOR_HUMAN_SIGNOFF",
    "authors": "[OPEN — Nhóm Nghiên cứu Sinh viên / Đơn vị Đào tạo / Giảng viên Hướng dẫn]",
    "submission_date": "Tháng 10 / 2026"
}

BIBLIOGRAPHY = [
    {
        "id": "1",
        "citation": "Apache Software Foundation. (2024). Apache Spark Documentation: PySpark Programming Guide and Spark SQL Reference. https://spark.apache.org/docs/latest/"
    },
    {
        "id": "2",
        "citation": "Zaharia, M., Xin, R. S., Wendell, P., Das, T., Armbrust, M., Dave, A., Meng, X., Rosen, J., Venkataraman, S., Franklin, M. J., Ghodsi, A., Gonzalez, J., Shenker, S., & Stoica, I. (2016). Apache Spark: A unified engine for big data processing. Communications of the ACM, 59(11), 56–65."
    },
    {
        "id": "3",
        "citation": "Greenwald, M., & Khanna, S. (2001). Space-efficient online computation of quantile summaries. In Proceedings of the 2001 ACM SIGMOD international conference on Management of data (pp. 58–66)."
    },
    {
        "id": "4",
        "citation": "Bureau of Transportation Statistics (BTS), U.S. Department of Transportation. (2024). Airline On-Time Performance Data (Form 41 Traffic, Part 234). Research and Innovative Technology Administration. https://www.transtats.bts.gov/"
    },
    {
        "id": "5",
        "citation": "Federal Aviation Administration (FAA). (2023). Operations Network (OPSNET) and Aviation System Performance Metrics (ASPM) Documentation. U.S. Department of Transportation."
    },
    {
        "id": "6",
        "citation": "Ball, M., Barnhart, C., Dresner, M., Hansen, M., Neels, K., Odoni, A., Peterson, R., Sherry, L., Trani, A., & Zou, B. (2010). Total delay impact study: A comprehensive assessment of the costs and impacts of flight delay in the United States. National Center of Excellence for Aviation Operations Research (NEXTOR)."
    },
    {
        "id": "7",
        "citation": "Apache Parquet Project. (2024). Apache Parquet Format and Encoding Specifications. https://parquet.apache.org/docs/"
    },
    {
        "id": "8",
        "citation": "McKinney, W. (2010). Data Structures for Statistical Computing in Python. In Proceedings of the 9th Python in Science Conference (pp. 51–56)."
    }
]
