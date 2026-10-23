# Gate G6 Task T-012 — Resource and Capacity Preflight
## Empirical Hardware Benchmarks, Workstation Budgets, and Storage Capacity Projections

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-012 / Gate G6  
**Parent Gate State:** `G6 — NOT_STARTED / BLOCKED`  
**Host Environment:** Windows local workstation, NTFS filesystem, Python 3.11, PySpark 3.5.0  
**Status:** **AUTHORITATIVE RESOURCE PREFLIGHT**  

---

## 1. Storage Capacity & Disk Headroom Audit

A live physical disk audit of drive `D:` was executed:
- **Drive Total Capacity:** `300.00 GB`
- **Drive Used Space:** `240.53 GB`
- **Drive Free Space Available:** `59.47 GB`

### Multi-Year Staging Storage Projections:
Based on empirical measurements from the T-010 2016 real-data benchmark (`T010_FULL_RESOURCE_BENCHMARK_TS014.md`):
- **Raw Input Size (All 9 Years):** `14.15 GB` (`15,196,366,173` bytes across 9 CSVs).
- **Measured Snappy Compression Ratio:** $4.48\times$ (1.54 GB raw CSV compressed to 343 MB Parquet in 2016).
- **Projected Total 9-Year Staging Parquet Output:**
  $$\text{Parquet Output} \approx \frac{14.15\text{ GB}}{4.48} \approx \mathbf{3.16\text{ GB}}$$
- **Peak Intermediate Shuffle & Scratch Space (`tmp_spark/`):** $\sim \mathbf{10.0\text{ GB}}$ (at any single time, cleaned after each year).
- **Total Required Storage Buffer:** $\approx 15.0\text{ GB}$.
- **Storage Safety Margin:**
  $$\text{Safety Ratio} = \frac{59.47\text{ GB Available}}{15.0\text{ GB Required}} = \mathbf{3.96\times \text{ Headroom}}$$
- **Verdict:** **STORAGE CAPACITY HIGHLY SUFFICIENT**.

---

## 2. Memory & JVM Heap Budget

The local PySpark execution configuration is pinned in `src/flight_pipeline/config/spark_config.py` and strictly obeys the workstation memory profile:

| Configuration Parameter | Allocated Value | Rationale & Safety Guard |
|---|---|---|
| `spark.driver.memory` | `4g` | Dedicated JVM heap for Driver. Measured T-010 peak: 3.2 GB. |
| `spark.driver.memoryOverhead` | `1g` | Buffer for JVM off-heap memory, string interning, and Py4J bindings. |
| `spark.sql.shuffle.partitions` | `16` | Divides shuffle stages into 16 chunks (~20 MB per chunk), eliminating heap spikes. |
| `spark.local.dir` | `D:/Study/Code/Apache/Flight_Analyzt/tmp_spark/` | Offloads spillover and shuffle files away from Windows system drive `C:`. |
| `spark.sql.execution.arrow.pyspark.enabled` | `true` | Zero-copy Arrow serialization between PySpark and JVM. |
| **Total Peak RAM Budget** | $\mathbf{\le 6.0\text{ GB}}$ | Safely within workstation physical RAM without triggering swap thrashing. |

---

## 3. CPU Core Allocation & Throughput Projections

- **Thread Pool Master:** `local[4]` (4 concurrent worker threads).
- **Measured Ingestion Throughput (T-010 Benchmark):**
  $$\text{Throughput} = \frac{5,617,658\text{ rows}}{249.8\text{ seconds}} \approx \mathbf{22,488\text{ rows / second}}$$
- **Estimated Full 9-Year Population:** $\approx \mathbf{54,700,000\text{ rows}}$.

### Execution Window Projection:
$$\text{Estimated Processing Time} = \frac{54,700,000\text{ rows}}{22,488\text{ rows/sec}} \approx 2,432\text{ seconds} \approx \mathbf{40.5\text{ minutes}}$$
- Adding 1 minute per annual batch for checksum validation, lock acquisition/release, and atomic publication ($9 \times 1\text{ min} = 9\text{ min}$):
- **Total Estimated End-to-End Execution Window:** $\approx \mathbf{49.5\text{ minutes}}$ ($\le 60\text{ minutes}$).

---

## 4. Sequential Execution & Garbage Collection Policy

To maintain zero memory creep across the 9 sequential batches:
1. **Explicit Session Re-use or Context Refresh:** Between annual batches, the driver will call `spark.catalog.clearCache()` to release cached DataFrames.
2. **Scratch Cleanup:** The intermediate directory `tmp_spark/` will be purged of orphaned shuffle blocks after each year.
3. **Lock Release Verification:** `SingleWriterLock.release()` will be called and verified before initiating the subsequent year's preflight.
