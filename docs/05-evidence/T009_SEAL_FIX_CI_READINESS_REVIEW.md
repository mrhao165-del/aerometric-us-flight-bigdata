# T009-SEAL-FIX CI Readiness & Clean-Checkout Verification Report

## 1. Problem Identification (FIX-S04)
The repository CI definition `.github/workflows/ci.yml` previously invoked `python tools/check_working_tree_consistency.py` immediately following checkout.
However, `check_working_tree_consistency.py` enforced `len(raw_data_files) == 9`. Because the 15GB raw tabular dataset (`data/raw/tabular/*.csv`) is properly excluded from Git tracking via `.gitignore`, any clean Git clone (such as a GitHub Actions runner) naturally contains 0 raw CSV files. This caused CI builds on clean checkouts to fail unconditionally.

---

## 2. Architectural Design: Separation of Audit Scopes
To preserve the non-negotiable policy that large raw data must never be committed to Git, while ensuring CI performs rigorous, meaningful verification:

1. **Local Mode (Default, `ci_mode=False`):**
   - Executed on development workstations with the raw data repository.
   - Enforces `len(raw_data_files) == 9`.
   - Validates that the developer or audit environment has all 9 annual CSV files present.

2. **CI Clean-Checkout Mode (`--ci-mode` / `--repo-only`, `ci_mode=True`):**
   - Executed by CI workflows on fresh clones.
   - Enforces `len(raw_data_files) == 0`, actively verifying that no raw CSV files were leaked or committed to Git.
   - **Maintains 100% of all other checks:**
     - Core documentary structure and file presence (18 ABC + 8 supplementary docs).
     - Relative link resolution across all Markdown files.
     - Stale token exclusion.
     - Core glossary and formula consistency.
     - Canonical 34 raw columns order and data types.
     - 8 CORE KPI definitions and formulas.
     - Pinned `PACKAGE_MANIFEST.json` and `SOURCE_MANIFEST.json` byte and hash validation.
     - Full registry verification: format, size, and SHA-256 validation for all 241+ registered deliverables.
     - Unrecognized stray file detection.

---

## 3. Local Clean-Checkout Simulation Results
Because a live GitHub Actions runner is not attached to this offline workstation, the CI workflow status on GitHub is recorded as `NOT_EXECUTED`.
A strict local clean-checkout simulation was executed in an isolated temporary sandbox containing only Git-tracked files (zero raw CSVs):
- **Command:** `python tools/check_working_tree_consistency.py --ci-mode`
- **Simulation Outcome:** `593 PASS, 0 FAIL` (matches expected assertion count).
- **Log Evidence:** `docs/05-evidence/T009_SEAL_FIX_LOG_CI_CLEAN_CHECKOUT.txt`.
