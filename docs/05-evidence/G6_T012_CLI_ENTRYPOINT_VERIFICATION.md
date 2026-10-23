# G6_T012_CLI_ENTRYPOINT_VERIFICATION.md
## Audit, Implementation and Verification of Ingestion CLI Runner (Finding E03)

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-21  
**Gate Status:** G5 = IN_PROGRESS (TECHNICALLY READY) | G6 = NOT_STARTED / BLOCKED  
**Auditor:** Principal Big Data Architect & PySpark Release Engineer  
**Component:** `src/flight_pipeline/ingestion/coordinator.py`  
**Finding Classification:** E03 (CLI Command Incompatibility / Missing Production CLI Entrypoint)

---

## 1. Finding E03 Context & Defect Analysis

The operational runbook `G6_T012_FIRST_YEAR_EXECUTION_READINESS.md` specified the following execution command:
```powershell
python -m flight_pipeline.ingestion.coordinator --years 2016 --run-id run_2016_v1 --base-data-dir data
```

### Forensic Review of Module `coordinator.py` Prior to Remediation
1. **Existing Interfaces:**
   - **Python API:** `IngestionCoordinator.execute_run(years=..., run_id=...)` was fully implemented and utilized by automated test suites.
   - **Diagnostic Smoke Runners:** Dedicated scripts existed in `tools/qa/run_t010_real_data_smoke.py` and `tools/qa/run_ts018_bts_adapter.py`.
   - **Module CLI Entrypoint:** `coordinator.py` **lacked** a top-level `if __name__ == "__main__":` block and `main(argv=None)` argument parser. Executing `python -m flight_pipeline.ingestion.coordinator` terminated silently with return code 0 without executing any logic or validating parameters.
2. **Operational Risk:** Operators following the runbook would believe the command had completed successfully or failed mysteriously, leading to operational confusion and unverified runs.

---

## 2. Production CLI Design & Implementation

To resolve Finding E03 without compromising governance controls, a formal CLI entrypoint was implemented directly in `src/flight_pipeline/ingestion/coordinator.py`.

### Argument Parser Specification

```python
parser = argparse.ArgumentParser(
    prog="python -m flight_pipeline.ingestion.coordinator",
    description="US Flight Performance Production Ingestion Coordinator Runner (T-012).",
)
parser.add_argument(
    "--years",
    nargs="+",
    type=int,
    required=True,
    help="One or more survey years to ingest (e.g. --years 2016)",
)
parser.add_argument(
    "--run-id",
    type=str,
    required=True,
    help="Unique execution run identifier (e.g. --run-id run_2016_v1)",
)
parser.add_argument(
    "--base-data-dir",
    type=Path,
    default=Path("data"),
    help="Base data directory (default: data)",
)
parser.add_argument(
    "--task-id",
    type=str,
    default="T-012",
    help="Governance task identifier (default: T-012)",
)
parser.add_argument(
    "--dry-run-preflight",
    action="store_true",
    help="Execute preflight validation only without starting Spark or writing Parquet",
)
parser.add_argument(
    "--allow-candidate-hashes",
    action="store_true",
    help="Allow local unapproved candidate hashes during dry-run preflight",
)
```

### Operational Modes & Safety Guards

1. **Dry-Run Preflight Mode (`--dry-run-preflight`):**
   - Validates `run_id` syntax and safe directory confinement via `validate_run_id()`.
   - Verifies all requested survey years against `AUDITED_SOURCE_INVENTORY`.
   - Inspects physical source file presence, byte size, and row count matching.
   - Verifies write lock status in `<base_data_dir>/locks/`.
   - Emits structured preflight audit report to stdout.
   - Exits cleanly with return code `0` **without** initializing PySpark or writing any files to disk.
2. **Live Execution Mode (Enforces Governance Hold D5):**
   - When invoked without `--dry-run-preflight`, the CLI performs all preflight checks.
   - It intercepts live execution and enforces the autonomous governance hold:
     ```
     [GOVERNANCE HOLD] Live ingestion execution is BLOCKED.
     Decision D5 (Gate G6 Annual Ingestion Authorization) has NOT been approved by Project Lead.
     Per AGENTS.md, autonomous AI agents cannot authorize production data execution.
     Preflight check passed; awaiting explicit human authorization (D5).
     ```
   - Exits with return code `1`.
   - **Protection:** Guarantees that neither AI agents nor automated scripts can accidentally trigger multi-million-row production writes without human approval.

---

## 3. Physical Verification & Test Results

The CLI runner was verified through both manual execution and automated unit testing in `tests/test_multiyear_snapshot_policy.py`:

```
TestFindingE03CoordinatorCLI:
- test_coordinator_cli_help:                PASS (SystemExit 0, clean help banner)
- test_coordinator_cli_dry_run_preflight:   PASS (Return code 0, complete report)
- test_coordinator_cli_live_run_blocked_by_d5: PASS (Return code 1, governance hold enforced)
```

### Raw Invocation Command on Windows NTFS (Antigravity Environment)

```powershell
python -m flight_pipeline.ingestion.coordinator --years 2016 --run-id run_2016_v1 --base-data-dir data --dry-run-preflight
```

**Stdout Output:**
```
================================================================================
INGESTION COORDINATOR PREFLIGHT REPORT (T-012)
================================================================================
Run ID:              run_2016_v1
Target Directory:    D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data\curated\runs\run_2016_v1
Survey Years:        [2016]
Base Data Dir:       D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data
Lock Directory:      D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\data\locks
Lock Status:         CLEAN
Dry-Run Mode:        True
--------------------------------------------------------------------------------
Source Files Inventory:
  Year 2016: data\raw\tabular\2016\flight_with_weather_2016.csv [OK]
    Audited Rows:  5,537,987
    Audited Bytes: 1,538,427,452 | Actual Bytes: 1,538,427,452
================================================================================
[PREFLIGHT PASS] Dry-run preflight inspection completed successfully. No data written.
```

---

## 4. Audit Verdict

- **CLI Compatibility:** Finding E03 is fully resolved. The CLI interface exists, parses all options correctly, and conforms to the operational runbook.
- **Fail-Closed Governance:** Live writes are structurally guarded by Decision D5 check.
- **Status:** **E03_RESOLVED_AND_VERIFIED**.
