# T009-FINAL-SEAL: Governance Errata & Technical Boundary Addendum

**Project:** US Flight Performance Analysis 2016–2024 using Apache Spark / PySpark  
**Document ID:** `T009-SEAL-ERRATA-01`  
**Task ID:** `T-009` (Controlled PySpark Environment & Toolchain Bootstrap)  
**Gate:** `G4` (Status: `PLANNED / NOT_COMPLETED`)  
**Auditor:** Independent QA Auditor & Repository Governance Engineer  
**Baseline Git Commit:** `ec361f16a8bc045291af95fe5694a95bc08fa46f` on branch `master`  
**Execution Mode:** `READ-ONLY REVIEW + ADDITIVE ERRATA ONLY`  

---

## 1. FP-DEC-017: Weather Integration Status (`CONDITIONAL_NO_GO`)
- **Status:** `CONDITIONAL_NO_GO`.
- **Governance Clarification:** In accordance with G3 design decisions and `AGENTS.md`, weather dataset integration remains strictly optional and is classified as `CONDITIONAL_NO_GO` for the CORE analytical pipeline.
- **Architectural Boundary:** The 8 CORE KPIs and data processing pipeline proceed independently without external weather feeds. No causal inferences regarding weather conditions may be asserted, and CORE pipeline gate reviews (G4, G5, G6) are not blocked by the absence of weather data.

---

## 2. OR-05: Known Data Defect: March 2024 Incomplete Reporting (`OPEN_QUALITY_DEFECT`)
- **Status:** `OPEN_QUALITY_DEFECT`.
- **Governance Clarification:** The raw audit dataset contains a verified, missing reporting defect for March 2024 (`2024-03`), where carrier reporting data is missing or incomplete in the audited source rather than simply reflecting a temporary reduction in flight volume.
- **Handling Mandate:** This anomaly is an immutable characteristic of the historical data snapshot. Downstream ingestion (`T-007`) and quality engines (`T-008`) must NOT attempt to impute, synthesize, or silently omit this month. It must be ingested as-is, accounted for in row balancing, and highlighted in downstream analytical commentary.

---

## 3. OR-08: Local Snapshot Integrity vs Upstream Provenance (`IDENTITY_UNVERIFIED`)
- **Status:** `IDENTITY_UNVERIFIED`.
- **Governance Clarification:** The SHA-256 hashes and file sizes recorded in `SOURCE_MANIFEST.json` and verified in `check_working_tree_consistency.py` prove with cryptographic certainty that the local raw CSV files (`2016.csv` through `2024.csv`) are bit-for-bit identical to the audited workstation snapshot established at project inception.
- **Boundary Limitation:** Local hash matches **do NOT** prove provenance or authenticity against the upstream US Bureau of Transportation Statistics (BTS) origin database. Upstream identity remains unverified (`IDENTITY_UNVERIFIED`); local processing operates strictly on the local frozen snapshot.

---

## 4. G2-EXC-001: Measure Units Reservation & Mandatory Hard Stop TS-018 at Gate G5
- **Status:** `PROVISIONAL_EXCEPTION_ACTIVE`.
- **Governance Clarification:** Exception `G2-EXC-001` permits provisional operational units for the 7 CORE measures (`ARR_DELAY`, `DEP_DELAY`, `TAXI_IN`, `TAXI_OUT`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) to enable PySpark framework bootstrap and synthetic unit testing in Task T-009.
- **Mandatory Obligation:** This provisional status does **NOT** waive the requirement for authoritative verification. Test `TS-018` represents an unskippable mandatory hard stop at Gate G5. Gate G6 production deployment is strictly blocked until `TS-018` confirms unit definitions against the BTS TranStats data dictionary.

---

## 5. Verification Granularity Errata: 685 Assertions vs Standalone Test Functions
- **Governance Clarification:** Previous summary reports cited "685 checks passed." To prevent ambiguity, this addendum formally clarifies that this figure represents **685 individual automated assertion checkpoints** verified across 7 distinct testing frameworks and validators, rather than 685 independent test functions (`def test_*`).
- **Exact Granular Composition:**
  1. **Unit Test Suite (`tests/`):** 27 standalone `TestCase` methods executed by `unittest discover` (27 PASS).
  2. **Spark Environment Smoke Test:** 1 standalone initialization and catalog access test (1 PASS).
  3. **T-006 Data Contract Consistency Suite:** 17 invariant checks and 16 isolated mutation tests (33 PASS).
  4. **Working-Tree Registry Regression Suite:** 2 positive baseline, 11 negative security/traversal, and 3 mutation tests (16 PASS).
  5. **Git Exclusion Verification Suite:** 2 positive root `.git/` ignore tests and 5 negative security rejection tests (7 PASS).
  6. **Validator Policy Extension Suite:** 1 base fixture, 3 positive extension, and 4 negative security tests (8 PASS).
  7. **Working-Tree Consistency Audit:** 111 baseline invariant assertions + 482 registered deliverable assertions ($2 \times 241$) (593 PASS).
  - **Total Assertion Checkpoints:** $27 + 1 + 33 + 16 + 7 + 8 + 593 = 685\text{ assertions PASS}$.

---

## 6. Runtime Warnings: Host PySpark & Py4J Diagnostics
- **Observed Diagnostics:**
  - `WARN Shell: Did not find winutils.exe: java.io.FileNotFoundException` (Hadoop binaries omitted on local Windows runtime).
  - `WARN NativeCodeLoader: Unable to load native-hadoop library for your platform` (Pure-Java fallback utilized).
  - `WARN SparkConf: Note that spark.local.dir will be overridden by the value set by the cluster manager` (Local temp directory configured).
  - `ResourceWarning: unclosed <socket.socket ...>` (Standard Python 3.10 garbage collection notification during Py4J gateway socket closure).
- **Governance Clarification:** While these diagnostics are standard development messages on Windows host environments that do not cause exit code failure in current unit suites, they are **NOT** claimed to be universally harmless under full-scale production clustering. Production deployment under G6 must explicitly configure cluster native Hadoop libraries.

---

## 7. Storage Engine Verification Scope: Parquet Metadata vs Full Row Integrity
- **Scope Clarification:** The validation performed by `SafePublisher.is_valid_parquet_file()` in `src/flight_pipeline/storage/publication.py` validates:
  1. Minimum file length ($\ge 12$ bytes) and header/trailer `PAR1` magic byte presence.
  2. Thrift `FileMetaData` footer deserialization via `pyarrow.parquet.read_metadata()`, confirming schema definitions, row group counts, and column descriptors without reading cell data into RAM.
- **Boundary Limitation:** This metadata verification guarantees that the Parquet file container is syntactically sound, uncorrupted at the container level, and readable by standard readers. It does **NOT** decode every row group or evaluate per-cell domain predicates (which would require gigabytes of RAM during publication). Exhaustive row-level data quality validation is the explicit domain of Task `T-008`.

---

## 8. Operational Assumption: Single-Writer Requirement for Task T-007
- **Scope Clarification:** `SafePublisher` implements atomic pointer updates (`os.replace`) and version immutability (`FAILED_VERSION_EXISTS`), but does **NOT** implement distributed cross-process locking (e.g. ZooKeeper, distributed file locks).
- **Mandatory Pipeline Constraint:** The execution orchestrator developed in Task `T-007` must enforce a strict **single-writer sequential execution model**. Concurrent execution threads attempting simultaneous publications to the curated store are strictly prohibited by operational policy.

---

## 9. Fault Injection TS-013: Unit Simulation Boundary
- **Scope Clarification:** The non-destructive rollback verified in `tests/test_publication_safety.py` under `fault_injection_step5` proves that the logic in `SafePublisher` aborts safely and preserves state under unit test simulation.
- **Boundary Limitation:** Unit simulation does **NOT** constitute full-scale `TS-013` compliance across multi-node failures or power-loss crash scenarios. Full-scale integration verification of TS-013 is scheduled for end-to-end pipeline gates.
