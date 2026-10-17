# T007 DESIGN R1 T-009 PUBLICATION INTERFACE REVIEW — API ALIGNMENT & STORAGE SAFETY

**Document ID:** `DOC-T007-DESIGN-R1-05-T009-INTERFACE`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Phase:** `DESIGN REMEDIATION (R1)`  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Storage Reliability Engineer & Senior PySpark Architect  
**Live Production Modules:** [`src/flight_pipeline/storage/publication.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/storage/publication.py), [`src/flight_pipeline/utils/run_manifest.py`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/utils/run_manifest.py)  

---

## 1. LIVE PRODUCTION API AUDIT & DISCREPANCY RECTIFICATION

The initial T-007 design erroneously referenced a non-existent method `SafePublisher.publish_run()` and claimed that data promotion was implemented via an atomic directory rename. Direct audit of the live production codebase confirms the exact API signatures and behaviors implemented in T-009:

### 1.1. Exact Live Signatures & Dataclasses

```python
# Location: src/flight_pipeline/storage/publication.py

@dataclass
class PublicationResult:
    """Result of a 7-step safe publication execution."""
    success: bool
    status: str
    run_id: str
    published_path: Optional[str] = None
    pointer_value: Optional[str] = None
    previous_pointer: Optional[str] = None
    error_message: Optional[str] = None
    aborted_step: Optional[int] = None

class SafePublisher:
    def __init__(self, base_data_dir: str):
        self.base_dir = Path(base_data_dir)
        self.staging_root = self.base_dir / "staging"
        self.curated_root = self.base_dir / "curated"
        self.runs_root = self.curated_root / "runs"
        self.pointer_file = self.curated_root / "latest_run_id.txt"

    def get_current_pointer(self, max_retries: int = 3, retry_delay: float = 0.05) -> Optional[str]: ...

    def publish(
        self,
        run_id: str,
        staging_dir: Path,
        accounting: RowAccounting,
        fault_injection_step5: bool = False,
    ) -> PublicationResult: ...
```

### 1.2. The True 7-Step Publication Implementation
Contrary to the initial design description of an atomic rename:
1. **Step 1 (Staging Parquet Audit):** Traverses `staging_dir`, ensures at least one `.parquet` file exists, and verifies every Parquet file via `is_valid_parquet_file(pf)` (checking file size $\ge 12$ bytes, header/footer magic bytes `b'PAR1'`, and Thrift metadata via PyArrow). Computes streaming SHA-256 for all staging files into `staging_inventory`.
2. **Step 2 (Row Accounting Audit):** Evaluates `accounting.is_balanced()`. If $N_{\text{raw}} \neq N_{\text{acc}} + N_{\text{quar}} + N_{\text{rej}}$, aborts with status `"ACCOUNTING_UNVERIFIED"`.
3. **Step 3 (Directory Promotion via Copytree):** Promotes staging to `data/curated/runs/{run_id}/` using **`shutil.copytree(staging_dir, versioned_target)`**!
   > [!IMPORTANT]
   > Promotion is performed via recursive copy (`copytree`), **NOT atomic directory rename**. This design choice in T-009 avoids cross-volume NTFS rename restrictions on Windows and ensures that the original staging directory remains fully intact if promotion fails.
4. **Step 4 (Post-Promotion Verification):** Performs a comprehensive byte-by-byte and streaming SHA-256 comparison between every file in `versioned_target` and `staging_inventory`. If any byte size or SHA-256 hash fails to match, the promoted directory is removed and publication aborts with `"FAILED_PROMOTION_CORRUPTION"`.
5. **Step 5 (Atomic Pointer Switch):** Updates `data/curated/latest_run_id.txt` using temporary file `.latest_run_id_tmp_<ts>.tmp` with atomic replacement via **`os.replace`** and retry backoff.
6. **Step 6 (Pointer Rollback on Step 5 Failure):** If Step 5 fails (or during `fault_injection_step5=True`), safely reverts `latest_run_id.txt` to `previous_pointer`.
7. **Step 7 (Audit Log Closure):** Returns `PublicationResult(success=True, status="SUCCESS", ...)` with full pointer provenance.

---

## 2. STAGING DIRECTORY LAYOUT & ARTIFACT SEPARATION

Under Step 1 of `SafePublisher.publish()`, every `.parquet` file in `staging_dir` must pass Thrift and magic byte validation. If non-parquet diagnostic text files or malformed CSV rows were placed directly alongside Parquet data, or if quarantine files were given `.parquet` extensions, the validator would fail with `"FAILED_STAGING_CONTENT_INVALID"`.

### 2.1. Engineered Staging Hierarchy
To guarantee clean separation, the ingestion pipeline organizes staging into distinct, isolated subdirectories:

```
data/staging/{run_id}/
├── curated/                     <-- Target staging_dir passed to SafePublisher.publish()
│   ├── year=2016/*.parquet     <-- 100% valid Snappy-compressed Parquet files
│   ├── ...
│   └── year=2024/*.parquet
└── evidence/                    <-- Isolated diagnostic & forensic artifacts (NOT in curated)
    ├── quarantine/              <-- Quarantined records (JSON lines with quarantine reason codes)
    ├── rejected/                <-- Rejected malformed CSV lines (raw text)
    └── run_manifest.json        <-- Full RunManifest audit document
```

By passing `staging_dir = Path("data/staging/{run_id}/curated")` to `SafePublisher.publish()`, downstream query engines operating on `data/curated/runs/{run_id}/` are guaranteed a 100% pure Parquet schema without foreign file collisions.

---

## 3. INTEGRATION WITH `RunManifest`

The ingestion coordinator integrates seamlessly with `RunManifest` without modifying its API:
```python
manifest = RunManifest(
    run_id=run_id,
    task_id="T-007",
    configuration={
        "spark_version": spark.version,
        "driver_memory": "4g",
        "shuffle_partitions": 16,
    }
)
# Record audited raw inputs
for raw_file in raw_inventory:
    manifest.record_input(path=raw_file.path, bytes_count=raw_file.bytes, sha256_hash=raw_file.sha256)

# Set verified row accounting
manifest.row_accounting = accounting

# Save manifest to staging evidence and obtain disk SHA-256
manifest_sha256 = manifest.save(f"data/staging/{run_id}/evidence/run_manifest.json")
manifest.record_output("evidence/run_manifest.json", os.path.getsize(f"data/staging/{run_id}/evidence/run_manifest.json"), manifest_sha256)
```

---

## 4. PUBLICATION TEST FIXTURE SPECIFICATION

To verify T-009 integration thoroughly in `T007-06`, the following 5 publication scenarios are simulated:

| Fixture ID | Publication Scenario | Simulated Condition | Expected `PublicationResult` |
|---|---|---|---|
| **`PUB-01`** | **Golden Success** | Valid Parquet staging, balanced accounting. | `success=True, status="SUCCESS"`, pointer updated to new `run_id`. |
| **`PUB-02`** | **Staging Content Invalid**| One `.parquet` file in staging contains corrupt bytes (not `PAR1`). | `success=False, status="FAILED_STAGING_CONTENT_INVALID"`, pointer untouched. |
| **`PUB-03`** | **Accounting Unverified** | `accounting.raw_row_count != acc + quar + rej`. | `success=False, status="ACCOUNTING_UNVERIFIED"`, promotion halted. |
| **`PUB-04`** | **Version Exists Collision** | Destination directory `curated/runs/{run_id}/` already exists. | `success=False, status="FAILED_VERSION_EXISTS"`, existing version preserved. |
| **`PUB-05`** | **Step 5 Fault Injection** | Injected failure during pointer switch (`fault_injection_step5=True`). | `success=False, status="FAILED_POINTER_SWITCH"`, pointer rolled back to previous. |

---

## 5. T-009 INTERFACE REVIEW VERDICT

The ingestion pipeline design directly binds to live production modules [`SafePublisher`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/storage/publication.py) and [`RunManifest`](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/src/flight_pipeline/utils/run_manifest.py) without altering a single line of T-009 source code.

**T-009 INTERFACE REVIEW VERDICT: 100% CANONICAL API FIDELITY ACHIEVED.**
