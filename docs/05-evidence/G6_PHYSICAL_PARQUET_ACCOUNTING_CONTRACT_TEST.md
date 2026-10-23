# G6 Physical Parquet Row Accounting Contract & PyArrow Verification

**Document ID:** `DOC-G6-PARQUET-ROW-001`  
**Classification:** PHYSICAL STORAGE AUDIT & THRIFT METADATA SPECIFICATION  
**Task Reference:** Finding M03 / Gate G6 Operational Safety Hardening  
**Component Audited:** `tools/qa/verify_multiyear_snapshot.py`  
**Governing Principles:** DATA_CONTRACT.md (DC-11, DC-12), KPI_SPEC.md  
**Date:** 2026-10-20  
**Evaluator:** Principal Big Data Architect & Senior PySpark Reliability Engineer  
**Status:** IMPLEMENTED, TESTED & ENFORCED  

---

## 1. Finding M03 Analysis: The Testing Flaw and Its Vulnerability

In the initial draft of `tests/test_multiyear_snapshot_policy.py`, the positive test fixture created a minimal dummy Parquet file containing exactly 2 records:
```python
table = pa.Table.from_arrays([pa.array([100, 200])], names=["flight_record_id"])
```
However, both the manifest and the snapshot registry declared accepted row counts matching the full annual canonical figures (e.g. 5,617,658 for 2016, 7,422,037 for 2019). The validator returned `VALID_SNAPSHOT_REGISTRY` without complaint.

### Why This Was a Critical Vulnerability
1. The test failed to prove the core data contract invariant:
   $$\text{physical\_accepted\_rows} == \text{manifest\_accepted\_rows} == \text{registry\_accepted\_rows}$$
2. If a production pipeline suffered a write truncation or lost partition files mid-run, leaving only a fraction of accepted rows on disk, the previous validator would have accepted the run as long as the manifest and registry text files contained the expected numbers!

---

## 2. Hardened Architecture: Zero-RAM PyArrow Thrift Metadata Summation

To resolve Finding M03 without loading massive datasets into memory, the validator inspects the binary Thrift metadata footers across all Parquet part files:

```python
total_physical_parquet_rows = 0
for pf in parquet_files:
    meta = pq.read_metadata(str(pf))
    total_physical_parquet_rows += meta.num_rows

# Strict Physical Row Count Conservation Invariant (Finding M03)
if verify_physical_row_counts:
    if total_physical_parquet_rows != acc_c:
        return SnapshotValidationResult(
            valid=False,
            status="PARQUET_PHYSICAL_ROW_COUNT_MISMATCH",
            error_message=(
                f"Year {year} physical Parquet row count {total_physical_parquet_rows:,} "
                f"!= declared accepted_row_count {acc_c:,}"
            ),
        )
```

### Advantages of Thrift Metadata Summation
1. **Zero RAM Materialization:** Does not deserialize columnar vectors into memory. PyArrow merely reads the trailing 4-byte footer length and deserializes the Thrift `FileMetaData` block.
2. **Speed & Scalability:** Inspecting metadata for thousands of Parquet part files takes milliseconds per run.
3. **Exact Row Count Precision:** `meta.num_rows` is encoded directly in the Parquet footer from the sum of all Row Group descriptors written by the ParquetWriter.

---

## 3. Mathematical Formulation of DC-11/12 Conservation

Under Data Contract rules **DC-11** (Three-way partition of input records) and **DC-12** (No unclassified records):

$$\forall y \in [2016 \dots 2024]: \quad \text{raw}_y = \text{accepted}_y + \text{quarantined}_y + \text{rejected}_y$$
$$\text{where } \text{raw}_y, \text{accepted}_y, \text{quarantined}_y, \text{rejected}_y \in \mathbb{N}_0$$

And under the physical storage contract:
$$\forall y: \quad \text{accepted}_y = \sum_{pf \in \text{run}_y} \text{meta}_{pf}.\text{num\_rows}$$

### Dynamic Accepted Rows Aggregation
The total raw volume across the 9 survey years is fixed to the canonical audited source count:
$$\sum_{y=2016}^{2024} \text{raw}_y = 54,674,003$$

The total accepted volume is **dynamically aggregated**:
$$\text{total\_accepted} = \sum_{y=2016}^{2024} \text{accepted}_y \le 54,674,003$$
The system does NOT enforce $\text{total\_accepted} == 54,674,003$, because any real pipeline with data quality filtering will produce $\text{quarantined} > 0$ or $\text{rejected} > 0$.

---

## 4. Test Fixture Realignment & Empirical Evidence

In `tests/test_multiyear_snapshot_policy.py`, the synthetic test suite was re-architected to maintain exact row count conservation:
- **Baseline Test Fixtures:** Generate 2 physical Parquet rows per year.
- **Accounting Invariant:**
  - $\text{accepted} = 2$ (strictly matching physical rows).
  - $\text{quarantined} = \text{raw} - 2$.
  - $\text{rejected} = 0$.
  - $\text{raw} = \text{accepted} + \text{quarantined} + \text{rejected} = 2 + (\text{raw} - 2) + 0 = \text{raw}$.
- Total physical rows across all 9 years $= 9 \times 2 = 18$ rows.
- Total raw rows across all 9 years $= 54,674,003$.

### Empirical Test Evidence
1. **`test_pos_01_complete_canonical_9year_snapshot_passes`**
   - Validates that a 9-year snapshot with 18 physical Parquet rows, 18 accepted rows in manifest, and 18 accepted rows in registry passes validation.
   - Total Raw: 54,674,003; Total Accepted: 18; Total Quarantined: 54,673,985.
   - **Result:** `PASS` (`VALID_SNAPSHOT_REGISTRY`).
2. **`test_pos_02_valid_snapshot_with_nonzero_quarantine_rejects_passes`**
   - Validates non-zero quarantine and reject partition ($\text{acc}=2, \text{quar}=\text{raw}-10, \text{rej}=8$).
   - **Result:** `PASS` (`VALID_SNAPSHOT_REGISTRY`).
3. **`test_neg_11_parquet_physical_row_count_mismatch_fails_closed`**
   - Generates 2 physical rows on disk, but registry and manifest declare $\text{accepted}=5$.
   - **Result:** `FAIL_CLOSED` (`PARQUET_PHYSICAL_ROW_COUNT_MISMATCH`).

---

## 5. Conclusion

Finding M03 has been fully resolved. The snapshot validator now enforces mathematical and physical identity between on-disk Parquet data and certified manifest records. No run can pass validation if physical row counts diverge from declared accepted figures.
