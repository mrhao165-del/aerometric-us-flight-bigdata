# T007 EXIT DELTA - SOURCE RECORD ACCOUNTING & GROUND-TRUTH RECONCILIATION

**Document ID:** `DOC-T007-EXIT-DELTA-03-RECORD-ACCOUNTING`  
**Task ID:** `T-007` (Raw CSV Ingestion Pipeline)  
**Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Design Authority:** Lead PySpark Data Engineer & Storage Safety Auditor  
**Binding Standards:** `DATA_CONTRACT.md` (DC-11), `TEST_PLAN.md` (TS-003), `DECISIONS.md` (FP-DEC-002)  

---

## 1. PHYSICAL TEXT LINES VERSUS LOGICAL CSV RECORDS

A critical finding in CSV processing systems is the distinction between a **Physical Text Line** and a **Logical CSV Record**:
- **Physical Text Line:** A contiguous sequence of bytes terminated by a newline character (`\n` or `\r\n`).
- **Logical CSV Record:** A semantic tuple of fields parsed according to RFC 4180 rules, where fields enclosing quotes may contain embedded newlines (`\n`).

### 1.1. Why `physical_lines - 1` Cannot Be Assumed as Absolute Ground Truth
In naive ingestion pipelines, engineers often compute ground truth as:
$$N_{\text{ground\_truth}} \stackrel{?}{=} N_{\text{physical\_lines}} - 1$$
**This equality FAILS under any of the following conditions:**
1. **Embedded Newlines in Quoted Text:** If any string field (e.g. carrier names or comments) contains an embedded `\n`, one logical CSV record spans multiple physical text lines.
2. **Trailing Blank Lines:** Text files frequently end with an extra empty newline (`\n\n`) or trailing whitespace, inflating physical line count by $+1$.
3. **Multi-File Header Aggregation:** When reading 9 yearly files, each file has its own header line. Sum of physical lines minus 1 yields $+8$ spurious records!
4. **Unclosed Quotes:** A line with an unclosed quote consumes subsequent physical lines until the quote terminates or EOF.

### 1.2. BTS Historical Ingestion Audit Analysis
The historical BTS audit (`docs/05-evidence/inputs/SOURCE_MANIFEST.json`) recorded:
$$\sum_{Y=2016}^{2024} N_{\text{audited\_raw}}(Y) = 54,674,003 \text{ rows}$$
- Audit records show that standard BTS flight performance CSV files do not contain embedded newlines in standard flight columns.
- However, **T-007 DOES NOT assume this blindly.** The pipeline enforces an independent verification gate during ingestion.

---

## 2. DUAL-ACCOUNTING AUDIT ARCHITECTURE

To eliminate silent record loss and verify that every physical byte is accounted for, T-007 establishes a **Dual-Accounting Verification Pattern**:

```
+─────────────────────────────────────────────────────────────────────────────+
| TRACK 1: Physical File Accounting (Fast Streaming Byte/Line Counter)        |
| - Counts physical text lines (terminator regex `\r?\n`)                     |
| - Counts header lines (exactly 1 per source CSV file)                       |
| - Identifies trailing blank lines                                           |
| - Computes SHA-256 and byte size of raw input files                         |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼ (Cross-Audit Comparison)
+─────────────────────────────────────────────────────────────────────────────+
| TRACK 2: Logical Parser Accounting (PySpark Univocity Parser)                |
| - Evaluates logical records parsed by Spark                                 |
| - N_raw = N_accepted + N_quarantined + N_rejected                           |
| - Cross-checks: N_raw == N_physical_lines - N_headers - N_trailing_blank   |
+─────────────────────────────────────────────────────────────────────────────+
```

### 2.1. Handling Specific File Edge Cases

| File Scenario | Physical Behavior | Logical Ingestion Rule | Accounting Disposition |
| :--- | :--- | :--- | :--- |
| **Empty File (0 bytes)** | 0 lines, 0 bytes | Spark reads 0 rows | $N_{\text{raw}} = 0$, pipeline records empty input warning |
| **Header Only File** | 1 line, valid header | Spark parses 0 data rows | $N_{\text{raw}} = 0, N_{\text{accepted}} = 0$ |
| **Trailing Blank Line** | Extra `\n` at EOF | Univocity ignores empty line | Line counter decrements trailing blank, matching $N_{\text{raw}}$ |
| **Quoted Newline** | 2 physical lines | `multiLine="true"` parses 1 logical row | Track 1 & Track 2 discrepancy triggers `EMBEDDED_NEWLINE_DETECTED` |
| **Short Row (< 34 tokens)** | 1 physical line | Captured in `_corrupt_record` | $N_{\text{rejected}} += 1, N_{\text{raw}} += 1$ |
| **Extra Tokens (> 34 tokens)**| 1 physical line | Captured in `_corrupt_record` | $N_{\text{rejected}} += 1, N_{\text{raw}} += 1$ |
| **Unclosed Quote** | Swallows to EOF | Captured in `_corrupt_record` | $N_{\text{rejected}} += 1$, triggers corrupt block alert |

---

## 3. FAIL-CLOSED DISCREPANCY ENFORCEMENT

If any accounting discrepancy is detected:
1. **Discrepancy Condition A:**
   $$\sum (N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}) \neq N_{\text{raw}}$$
   $\implies$ **FAIL-CLOSED:** Staging Parquet is marked invalid. Publication is aborted with status `"ACCOUNTING_UNVERIFIED"`.
2. **Discrepancy Condition B (Current-Run vs Audited Historical):**
   $$N_{\text{observed\_raw}} \neq N_{\text{audited\_raw}} (54,674,003)$$
   $\implies$ Pipeline does not silently overwrite historical manifests; it records `HISTORICAL_COUNT_MISMATCH` with an audit report requiring Project Lead signoff before promotion.
3. **Discrepancy Condition C (Physical Line vs Logical Record Discrepancy):**
   If physical lines minus headers do not equal logical records, and embedded newlines were not previously verified for that source year:
   $\implies$ Ingestion pauses and generates an explicit `LINE_STRUCTURE_AUDIT_REQUIRED` forensic report.

---

## 4. LOCAL RESOURCE & MEMORY PROFILE DESIGN

- **Streaming Line Counter:** Implemented using Python's streaming chunk read (64 KB buffers) to count line terminators and calculate SHA-256 without loading files into memory.
- **Spark Distributed Parsing:** Utilizes Spark's standard distributed chunk partitioning across local cores without collecting raw rows to the driver JVM.
- **No Premature Benchmark Claims:** Resource consumption (peak RAM, spill-to-disk) will be empirically benchmarked during smoke runs (Subtask `T007-06`) and recorded in execution receipts; no theoretical throughput claims are fabricated at the design phase.
