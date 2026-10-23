# -*- coding: utf-8 -*-
"""
tools/export/generate_t016_deliverables.py

Comprehensive deliverable generator for Task T-016:
- T016_FINAL_ACADEMIC_REPORT.md
- T016_FINAL_ACADEMIC_REPORT.docx
- T016_FINAL_PRESENTATION.pptx
- T016_REPRODUCIBILITY_AND_DEMO_GUIDE.md
- T016_CLAIM_TO_EVIDENCE_INDEX.csv
- T016_TECHNICAL_COMPLETION_REPORT.md
- T016_FINAL_REVIEW.zip
- T016_FINAL_REVIEW_MANIFEST.json

All deliverables stored in: D:\\Flight_Audit_Exports\\G7_T016_FINAL_DELIVERABLES\\
"""

import os
import sys
import json
import csv
import zipfile
import hashlib
import zlib
from pathlib import Path
import pandas as pd

# Word and PowerPoint generation libraries
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

import pptx
from pptx.util import Inches as PInches, Pt as PPt
from pptx.dml.color import RGBColor as PRGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_DIR = Path(r"D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES")
BASE_DIR = Path(r"D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1")
ANALYTICS_DIR = BASE_DIR / "data" / "analytics" / "runs" / "t014_analysis_2016_2024_v4"
CHARTS_DIR = ANALYTICS_DIR / "charts"
TABLES_DIR = ANALYTICS_DIR / "tables"

def ensure_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    with open(ANALYTICS_DIR / "RESULTS_REGISTER.json", "r", encoding="utf-8") as f:
        res_data = json.load(f)
    results = res_data.get("results", [])

    with open(ANALYTICS_DIR / "CHART_INVENTORY.json", "r", encoding="utf-8") as f:
        chart_data = json.load(f)
    figures = chart_data.get("figures", [])

    tables = {}
    for table_name in [
        "rq01_annual_volume.csv", "rq01_monthly_volume.csv",
        "rq02_annual_delays.csv", "rq02_monthly_delays.csv",
        "rq03_top_carriers.csv", "rq03_directed_routes.csv",
        "rq04_pandemic_comparison.csv", "rq05_airport_taxi.csv",
        "rq05_annual_journey_times.csv"
    ]:
        table_path = TABLES_DIR / table_name
        if table_path.exists():
            tables[table_name] = pd.read_csv(table_path)

    return results, figures, tables

print("Helper definitions loaded.")
