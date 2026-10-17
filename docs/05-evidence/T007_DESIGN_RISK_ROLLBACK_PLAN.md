# T007 DESIGN RISK AND ROLLBACK PLAN — OPERATIONAL RISKS & NON-DESTRUCTIVE RECOVERY

**Document ID:** `DOC-T007-DESIGN-08-RISK-ROLLBACK`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN ONLY`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Senior Risk & Reliability Engineer & Big Data Architect  
**Governance Baselines:** `docs/03-quality/ROLLBACK_PLAN.md`, `docs/03-quality/RISK_REGISTER.md`  

---

## 1. OPERATIONAL RISK ALIGNMENT & MITIGATION MATRIX

The ingestion design addresses all registered operational risks (`OR-01` through `OR-08`) with concrete technical mitigations:

| Risk ID | Risk Summary | Severity | Technical Failure Mode | Architectural Mitigation Strategy |
|---|---|---|---|---|
| **OR-01** | **Driver Memory Exhaustion (OOM)** | HIGH | Processing 54.7M rows in a single DataFrame causes JVM heap exhaustion or OS thrashing. | Sequential year-by-year batching (`2016` to `2024`); driver memory capped at 4GB; shuffle partitions set to 16; off-heap disk spill to local SSD. |
| **OR-02** | **Windows NTFS File Lock Contention** | MEDIUM | Concurrent processes collide when writing staging files or updating pointer. | Single-writer atomic lock (`.publisher.lock`) with Windows PID liveness check and stale lock timeout (2 hours). |
| **OR-03** | **Schema Drift Across Years** | HIGH | Undetected column reordering or missing columns corrupt Parquet partitions. | Preflight header validation comparing CSV headers to exact 34 canonical fields. Fail-fast with `SchemaMismatchError`. |
| **OR-04** | **Silent Row Loss During Parsing** | CRITICAL | Malformed lines silently dropped by parser, corrupting downstream counts. | Mandatory DC-11 assertion: $N_{\text{raw}} == N_{\text{acc}} + N_{\text{quar}} + N_{\text{rej}}$. Mismatch triggers `ACCOUNTING_UNVERIFIED` and halts publication. |
| **OR-05** | **Year 2024 Missing March Defect** | HIGH | Month 3 completely missing from raw extract (335/366 days). | Pipeline computes calendar coverage; records `OR-05` open quality defect in `RunManifest`; does not fabricate data. |
| **OR-06** | **Partial / Corrupted Publication** | CRITICAL | Incomplete Parquet dataset exposed to downstream readers via pointer. | `SafePublisher` 7-step sequence: staging isolated; `PAR1` magic bytes validated; pointer updated atomically via `os.replace`. |
| **OR-07** | **Unreproducible Local Environment** | MEDIUM | Different Python/Spark runtime versions alter float casting or date parsing. | Runtime check in `spark_config.py`; Python 3.10 and PySpark 4.0.1 pinned; configuration recorded in manifest. |
| **OR-08** | **Raw Identity Unverified (BTS Provenance)** | HIGH | Local CSV files lack cryptographic cryptographic origin verification from BTS. | Documented as non-blocking accepted limitation `IDENTITY_UNVERIFIED`. Local SHA-256 tracked for reproducibility. |

---

## 2. MULTI-LEVEL NON-DESTRUCTIVE ROLLBACK PROCEDURES

The rollback framework guarantees that any failure at any stage can be reversed with zero corruption to raw data or historical runs:

```
[Level 1: Staging Failure]  --> Purge staging/{run_id}/, release lock. Pointer unchanged.
[Level 2: Publish Failure]  --> Quarantine curated/runs/{run_id}/. Pointer remains at previous run.
[Level 3: Source Code Bug]  --> Git revert commit, rollback to baseline 859ae3874080.
```

### 2.1. Level 1 Rollback: Failure During CSV Parsing or Staging Write
- **Trigger:** Out of memory, parser exception, disk full, or DC-11 row accounting mismatch during batch execution.
- **State:** Parquet files exist in `data/staging/{run_id}/`. Pointer `data/curated/latest_run_id.txt` has **NOT** been modified.
- **Rollback Steps:**
  1. Catch exception in pipeline supervisor.
  2. Rename `data/staging/{run_id}/` to `data/staging/{run_id}_FAILED_{timestamp}/` for forensic debugging (or purge if disk space constrained).
  3. Release `.publisher.lock`.
  4. Curated data remains 100% untouched. Downstream consumers experience zero downtime.

### 2.2. Level 2 Rollback: Failure During Curated Publication or Validation
- **Trigger:** `PAR1` magic byte check fails, or directory move encounters NTFS permission lock.
- **State:** Staging completed, but publication sequence aborted before pointer switch.
- **Rollback Steps:**
  1. Abort `SafePublisher` transaction.
  2. If partial directory exists at `data/curated/runs/{run_id}/`, quarantine it to `data/curated/failed_runs/{run_id}/`.
  3. Revert pointer: ensure `data/curated/latest_run_id.txt` points to previous valid run (or remove temporary `.tmp` pointer file).
  4. Release `.publisher.lock`.

### 2.3. Level 3 Rollback: Post-Implementation Code Defect / Regression
- **Trigger:** Discovery of logical flaw or regression after code commit.
- **Target Git Baseline:** Commit `859ae38740806ce8f92a244bfe4ee12287c4c9bd` (`feat(t009): record official human signoff and reconcile G4 task governance state`).
- **Rollback Steps:**
  1. `git revert <commit-sha> -m "revert(t007): rollback ingestion pipeline due to defect"`.
  2. Verify clean working tree with `git status --porcelain`.
  3. Rerun baseline consistency check (`python tools/check_working_tree_consistency.py`).

---

## 3. FAIL-SAFE STOP CONDITIONS

The execution engine must halt immediately under any of the following conditions:
1. **Lock Contention:** `.publisher.lock` exists and holder process PID is confirmed active.
2. **Schema Inconsistency:** Any annual CSV has fewer or more than 34 columns, or header names do not match canonical set.
3. **Source Hash Discrepancy:** A local raw CSV file fails local SHA-256 verification against `SOURCE_MANIFEST.json`.
4. **DC-11 Accounting Violation:** For any year, $N_{\text{raw}} \neq N_{\text{acc}} + N_{\text{quar}} + N_{\text{rej}}$.
5. **Disk Space Exhaustion:** Available disk space on staging drive falls below 10 GB.

---

## 4. RISK & ROLLBACK DESIGN VERDICT

The multi-level non-destructive rollback plan ensures comprehensive operational safety on local Windows NTFS.

**RISK & ROLLBACK DESIGN VERDICT: APPROVED FOR T-007 IMPLEMENTATION.**
