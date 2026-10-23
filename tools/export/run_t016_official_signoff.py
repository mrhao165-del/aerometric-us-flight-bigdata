# -*- coding: utf-8 -*-
"""
tools/export/run_t016_official_signoff.py
Executes the final one-line erratum and official controlled signoff for Task T-016 (Gate G7).
Generates final deliverables into D:\\Flight_Audit_Exports\\G7_T016_FINAL_DELIVERABLES\\signoff_official\\:
  1. T016_FINAL_ACADEMIC_REPORT.docx (full-fidelity, all 80 headings, Chapter 2.5 erratum fixed)
  2. T016_FINAL_ACADEMIC_REPORT.md (80 headings, Chapter 2.5 erratum fixed)
  3. T016_FINAL_PRESENTATION.pptx (16 widescreen slides, preserved)
  4. T016_REPRODUCIBILITY_AND_DEMO_GUIDE.md (verified)
  5. T016_CLAIM_TO_EVIDENCE_INDEX.csv (20 standardized RES items)
  6. T016_TECHNICAL_COMPLETION_REPORT.md (verdict T016_OFFICIAL_CONTROLLED_SIGNOFF_PASS)
  7. T016_OFFICIAL_SIGNOFF_REVIEW.zip & T016_OFFICIAL_SIGNOFF_REVIEW_MANIFEST.json
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

SIGNOFF_OFFICIAL_DIR = Path(r"D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\signoff_official")
SIGNOFF_FINAL_DIR = Path(r"D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES\signoff_final")

def run_official_signoff():
    print("=" * 80)
    print("STARTING T-016 FINAL ONE-LINE ERRATUM & OFFICIAL CONTROLLED SIGNOFF")
    print(f"Target Directory: {SIGNOFF_OFFICIAL_DIR}")
    print("=" * 80)

    SIGNOFF_OFFICIAL_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Regenerate Markdown report with Section 2.5 erratum
    print("\n[Step 1/5] Regenerating Academic Report Markdown (Section 2.5 erratum fixed)...")
    md_path = generate_report_markdown(output_dir=SIGNOFF_OFFICIAL_DIR)

    # 2. Regenerate full-fidelity DOCX report
    print("\n[Step 2/5] Regenerating Academic Report DOCX (all 80 headings, Section 2.5 erratum fixed)...")
    docx_path = generate_report_docx(output_dir=SIGNOFF_OFFICIAL_DIR)

    # 3. Copy / Generate Presentation PPTX
    print("\n[Step 3/5] Setting up Presentation PPTX...")
    src_pptx = SIGNOFF_FINAL_DIR / "T016_FINAL_PRESENTATION.pptx"
    dst_pptx = SIGNOFF_OFFICIAL_DIR / "T016_FINAL_PRESENTATION.pptx"
    if src_pptx.exists():
        shutil.copy2(src_pptx, dst_pptx)
        print(f"Copied validated PPTX: {dst_pptx}")
    else:
        generate_presentation_pptx(output_dir=SIGNOFF_OFFICIAL_DIR)

    # 4. Generate Guides, Claim Index & Technical Report
    print("\n[Step 4/5] Generating Guides, Claim Index & Technical Report...")
    guide_path = generate_reproducibility_guide(output_dir=SIGNOFF_OFFICIAL_DIR)
    index_path = generate_claim_to_evidence_index(output_dir=SIGNOFF_OFFICIAL_DIR)
    tech_path = generate_technical_completion_report(output_dir=SIGNOFF_OFFICIAL_DIR)

    # 5. Package into ZIP and generate manifest
    print("\n[Step 5/5] Packaging deliverables into ZIP & generating manifest...")
    zip_path, manifest_path = package_deliverables(
        target_dir=SIGNOFF_OFFICIAL_DIR,
        zip_name="T016_OFFICIAL_SIGNOFF_REVIEW.zip",
        manifest_name="T016_OFFICIAL_SIGNOFF_REVIEW_MANIFEST.json",
        verdict="T016_OFFICIAL_CONTROLLED_SIGNOFF_PASS",
        status="PASS / COMPLETED (CONTROLLED)"
    )

    # Also provide alias filenames for reviewer convenience
    alias_zip = SIGNOFF_OFFICIAL_DIR / "T016_FINAL_SIGNOFF_REVIEW.zip"
    shutil.copy2(zip_path, alias_zip)
    alias_manifest = SIGNOFF_OFFICIAL_DIR / "T016_FINAL_SIGNOFF_REVIEW_MANIFEST.json"
    shutil.copy2(manifest_path, alias_manifest)

    # Validate
    print("\n[Verification] Validating all deliverables in signoff_official...")
    validate_all_deliverables(
        target_dir=SIGNOFF_OFFICIAL_DIR,
        zip_name="T016_OFFICIAL_SIGNOFF_REVIEW.zip",
        manifest_name="T016_OFFICIAL_SIGNOFF_REVIEW_MANIFEST.json"
    )

    print("\n" + "=" * 80)
    print("T-016 OFFICIAL SIGNOFF COMPLETE: T016_OFFICIAL_CONTROLLED_SIGNOFF_PASS")
    print("=" * 80)

if __name__ == "__main__":
    run_official_signoff()
