# -*- coding: utf-8 -*-
"""
tools/export/run_t016_final_signoff_closeout.py
Executes the final micro-correction and human signoff closeout for Task T-016 (Gate G7).
Generates final deliverables into D:\\Flight_Audit_Exports\\G7_T016_FINAL_DELIVERABLES\\signoff_final\\:
  1. T016_FINAL_ACADEMIC_REPORT.docx (full-fidelity, all 80 headings, 7 data tables, 2 callout boxes, 15 figures)
  2. T016_FINAL_ACADEMIC_REPORT.md (80 headings, ~82k characters, PySpark scalable selection, non-causal observations)
  3. T016_FINAL_PRESENTATION.pptx (16 widescreen slides, Slide 2/5/7 micro-corrections)
  4. T016_REPRODUCIBILITY_AND_DEMO_GUIDE.md (fixed NameError, verified versions)
  5. T016_CLAIM_TO_EVIDENCE_INDEX.csv (20 standardized RES items)
  6. T016_TECHNICAL_COMPLETION_REPORT.md (verdict T016_FINAL_READY_FOR_PROJECT_LEAD_SIGNOFF)
  7. T016_FINAL_SIGNOFF_REVIEW.zip & T016_FINAL_SIGNOFF_REVIEW_MANIFEST.json
"""

import sys
import os
import shutil
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

SIGNOFF_FINAL_DIR = Path(r"D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\signoff_final")

def run_signoff_final_closeout():
    print("=" * 80)
    print("STARTING T-016 FINAL MICRO-CORRECTION & HUMAN SIGNOFF CLOSEOUT")
    print(f"Target Directory: {SIGNOFF_FINAL_DIR}")
    print("=" * 80)

    SIGNOFF_FINAL_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate final Markdown report
    print("\n[Step 1/5] Generating final Academic Report Markdown...")
    md_path = generate_report_markdown(output_dir=SIGNOFF_FINAL_DIR)

    # 2. Generate full-fidelity DOCX report
    print("\n[Step 2/5] Generating full-fidelity Academic Report DOCX (all 80 headings)...")
    docx_path = generate_report_docx(output_dir=SIGNOFF_FINAL_DIR)

    # 3. Generate final Presentation PPTX
    print("\n[Step 3/5] Generating final Presentation PPTX (16 slides, Slide 2/5/7 fixed)...")
    pptx_path = generate_presentation_pptx(output_dir=SIGNOFF_FINAL_DIR)

    # 4. Generate Guides and Index
    print("\n[Step 4/5] Generating Reproducibility Guide, Claim Index & Technical Report...")
    guide_path = generate_reproducibility_guide(output_dir=SIGNOFF_FINAL_DIR)
    index_path = generate_claim_to_evidence_index(output_dir=SIGNOFF_FINAL_DIR)
    tech_path = generate_technical_completion_report(output_dir=SIGNOFF_FINAL_DIR)

    # 5. Package into ZIP and generate manifest
    print("\n[Step 5/5] Packaging deliverables into ZIP & generating manifest...")
    zip_path, manifest_path = package_deliverables(
        target_dir=SIGNOFF_FINAL_DIR,
        zip_name="T016_FINAL_SIGNOFF_REVIEW.zip",
        manifest_name="T016_FINAL_SIGNOFF_REVIEW_MANIFEST.json",
        verdict="T016_FINAL_READY_FOR_PROJECT_LEAD_SIGNOFF"
    )

    # Validate
    print("\n[Verification] Validating all deliverables...")
    validate_all_deliverables(
        target_dir=SIGNOFF_FINAL_DIR,
        zip_name="T016_FINAL_SIGNOFF_REVIEW.zip",
        manifest_name="T016_FINAL_SIGNOFF_REVIEW_MANIFEST.json"
    )

    print("\n" + "=" * 80)
    print("T-016 FINAL SIGNOFF CLOSEOUT COMPLETE: T016_FINAL_READY_FOR_PROJECT_LEAD_SIGNOFF")
    print("=" * 80)

if __name__ == "__main__":
    run_signoff_final_closeout()
