# -*- coding: utf-8 -*-
"""
tools/export/run_t016_targeted_correction.py
Executes the bounded targeted final correction for Task T-016 (Gate G7).
Generates corrected deliverables into D:\\Flight_Audit_Exports\\G7_T016_FINAL_DELIVERABLES\\corrected\\:
  1. T016_FINAL_ACADEMIC_REPORT.docx (full-fidelity, all 80 headings, 16 tables, 15 figures)
  2. T016_FINAL_ACADEMIC_REPORT.md (80 headings, ~82k characters, B1-B5 corrected)
  3. T016_FINAL_PRESENTATION.pptx (16 widescreen slides with notes, B1-B5 corrected)
  4. T016_REPRODUCIBILITY_AND_DEMO_GUIDE.md (fixed NameError, verified versions)
  5. T016_CLAIM_TO_EVIDENCE_INDEX.csv (updated RES-007, RES-018, RES-019)
  6. T016_TECHNICAL_COMPLETION_REPORT.md (verdict T016_CORRECTED_READY_FOR_HUMAN_SIGNOFF)
  7. T016_CORRECTED_REVIEW.zip & T016_CORRECTED_REVIEW_MANIFEST.json
"""

import sys
import os
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

CORRECTED_DIR = Path(r"D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\corrected")

def run_targeted_correction():
    print("=" * 80)
    print("STARTING T-016 TARGETED FINAL CORRECTION (BOUNDED PASS)")
    print(f"Target Directory: {CORRECTED_DIR}")
    print("=" * 80)

    CORRECTED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate corrected Markdown report
    print("\n[Step 1/5] Generating corrected Academic Report Markdown...")
    md_path = generate_report_markdown(output_dir=CORRECTED_DIR)

    # 2. Generate full-fidelity DOCX report
    print("\n[Step 2/5] Generating full-fidelity Academic Report DOCX (all 80 headings)...")
    docx_path = generate_report_docx(output_dir=CORRECTED_DIR)

    # 3. Generate corrected Presentation PPTX
    print("\n[Step 3/5] Generating corrected Presentation PPTX (16 slides)...")
    pptx_path = generate_presentation_pptx(output_dir=CORRECTED_DIR)

    # 4. Generate Guides and Index
    print("\n[Step 4/5] Generating Reproducibility Guide, Claim Index & Technical Report...")
    guide_path = generate_reproducibility_guide(output_dir=CORRECTED_DIR)
    index_path = generate_claim_to_evidence_index(output_dir=CORRECTED_DIR)
    tech_path = generate_technical_completion_report(output_dir=CORRECTED_DIR)

    # 5. Package into ZIP and generate manifest
    print("\n[Step 5/5] Packaging deliverables into ZIP & generating manifest...")
    zip_path, manifest_path = package_deliverables(target_dir=CORRECTED_DIR)

    # Validate
    print("\n[Verification] Validating all deliverables...")
    validate_all_deliverables(target_dir=CORRECTED_DIR)

    print("\n" + "=" * 80)
    print("T-016 TARGETED CORRECTION COMPLETE: T016_CORRECTED_READY_FOR_HUMAN_SIGNOFF")
    print("=" * 80)

if __name__ == "__main__":
    run_targeted_correction()
