# -*- coding: utf-8 -*-
"""
tools/export/run_t016_full_execution.py
End-to-end execution runner for T-016:
1. Generates Markdown report
2. Generates DOCX report
3. Generates PPTX presentation
4. Generates Reproducibility & Demo Guide, Claim-to-Evidence Index, and Technical Completion Report
5. Packages deliverables into ZIP and generates external manifest
6. Runs focused validation pass
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.export.build_report_md import generate_report_markdown
from tools.export.build_report_docx import generate_report_docx
from tools.export.build_presentation_pptx import generate_presentation_pptx
from tools.export.build_guides_and_index import (
    generate_reproducibility_guide,
    generate_claim_to_evidence_index,
    generate_technical_completion_report
)
from tools.export.package_and_validate import package_deliverables, validate_all_deliverables

def run_all():
    print("=== STARTING T-016 FULL EXECUTION PIPELINE ===")
    generate_report_markdown()
    generate_report_docx()
    generate_presentation_pptx()
    generate_reproducibility_guide()
    generate_claim_to_evidence_index()
    generate_technical_completion_report()
    package_deliverables()
    validate_all_deliverables()
    print("=== T-016 FULL EXECUTION PIPELINE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_all()
