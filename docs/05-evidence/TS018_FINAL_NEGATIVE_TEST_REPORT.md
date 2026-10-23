# TS-018 Final Negative Test Report
## Automated Fault Injection and Fail-Closed Verification of Sample Witness Verifier

**Project:** US Flight Performance Analysis 2016–2024  
**Date:** 2026-10-20 (Asia/Ho_Chi_Minh)  
**Parent Task:** Task T-011 / TS-018  
**Parent Gate:** Gate G5 (`IN_PROGRESS`)  
**Test Suite:** `tools/qa/test_ts018_negative_witness_verification.py`  
**Execution Environment:** Isolated `tempfile.TemporaryDirectory()` on Windows NTFS  
**Status:** **AUTHORITATIVE NEGATIVE QA REPORT**  

---

## 1. Executive Summary

To ensure that the TS-018 two-source verification script [`verify_ts018_two_source_sample_witness.py`](../../tools/qa/verify_ts018_two_source_sample_witness.py) cannot produce false-positive passes or silently ignore corrupted witness data, six distinct error-injection tests were executed against an isolated temporary copy of the witness dataset.

```text
================================================================================
NEGATIVE WITNESS FAULT INJECTION SUMMARY
================================================================================
Total Negative Test Cases:        6
Fault Injections Caught (PASS):   6 / 6 (100.0%)
Fault Injections Missed (FAIL):   0 / 6 (0.0%)
Production Mutation:              ZERO (Executed in temp directories)
Overall Suite Verdict:            ALL NEGATIVE TESTS PASSED (FAIL-CLOSED)
================================================================================
```

---

## 2. Injected Fault Scenarios & Verification Evidence

### NEG-W01: Injected Numerical Value Mismatch
- **Fault Description:** The value of `RAW_DATASET_ARR_DELAY` for the first record (`NK 314 IAH->TPA`) was modified from `-6.0` to `-999.0` in the witness CSV.
- **Expected Behavior:** Verifier compares witness value against the physical raw CSV, detects mismatch, and halts with non-zero exit code.
- **Observed Result:** `[PASS] NEG-W01: Injected value mismatch in witness (-999.0 vs real) is caught fail-closed -> exit=1`
- **Verifier Diagnostic:** `[FAIL] 1 value mismatches between raw CSV and witness!`

---

### NEG-W02: Injected Non-Existent Flight Composite Key
- **Fault Description:** A completely fabricated key (`2019-01-01 | ZZ | 9999 | XYZ -> ZZZ`) was injected into the witness in place of a valid flight.
- **Expected Behavior:** Verifier attempts to locate the key in the physical 2019 raw CSV, fails to match 1,500 distinct keys, and halts with non-zero exit code.
- **Observed Result:** `[PASS] NEG-W02: Non-existent flight key in witness is caught fail-closed -> exit=1`
- **Verifier Diagnostic:** `[FAIL] 1 witness keys missing from raw CSV! Sample: [('2019-01-01', 'ZZ', '9999', 'XYZ', 'ZZZ')]`

---

### NEG-W03: Witness File Byte Tampering / Corrupted Checksum
- **Fault Description:** An extra trailing corrupted line was appended to the witness CSV, altering its physical byte sequence and invalidating its cryptographic digest.
- **Expected Behavior:** Verifier identifies SHA-256 digest divergence or malformed structure and terminates with exit code 1.
- **Observed Result:** `[PASS] NEG-W03: Corrupted witness byte content is rejected fail-closed -> exit=1`

---

### NEG-W04: Slipped Sign on Signed Delay Measure
- **Fault Description:** An arrival delay of `-6.0` minutes was flipped to positive `+6.0` minutes in the witness CSV, simulating a sign-stripping bug (`abs()` or `max(0, delay)`).
- **Expected Behavior:** Verifier detects sign mismatch against raw project CSV and halts fail-closed.
- **Observed Result:** `[PASS] NEG-W04: Slipped sign on arrival delay (-6.0 -> +6.0) is caught fail-closed -> exit=1`
- **Verifier Diagnostic:** `[FAIL] 1 value mismatches between raw CSV and witness! Sample: [('2019-01-10', 'NK', '314', 'IAH', 'TPA', 'ARR_DELAY', -6.0, 6.0)]`

---

### NEG-W05: Duplicate Key Collision (Truncated Distinct Keys)
- **Fault Description:** The second row of the witness CSV was overwritten with an exact duplicate of the first row, reducing distinct composite keys from 1,500 to 1,499.
- **Expected Behavior:** Verifier counts distinct keys ingested, asserts `len(keys) == 1500`, and halts immediately with exit code 1.
- **Observed Result:** `[PASS] NEG-W05: Duplicate key collision in witness (resulting in <1500 distinct keys) is caught -> exit=1`
- **Verifier Diagnostic:** `[FAIL] Expected exactly 1500 witness records, got 1499`

---

### NEG-W06: Null / Zero Disagreement on Numeric Measure
- **Fault Description:** A non-zero taxi-out duration (`13.0` minutes) was replaced with `0.0` in the witness CSV, testing whether false zero substitutions are detected.
- **Expected Behavior:** Verifier detects discrepancy between `0.0` and `13.0` and terminates fail-closed.
- **Observed Result:** `[PASS] NEG-W06: Null / zero disagreement on numeric measure is caught fail-closed -> exit=1`
- **Verifier Diagnostic:** `[FAIL] 1 value mismatches between raw CSV and witness! Sample: [('2019-01-10', 'NK', '314', 'IAH', 'TPA', 'TAXI_OUT', 13.0, 0.0)]`

---

## 3. Data Safety and Isolation Guarantee

All six test scenarios executed within temporary directories provisioned via Python's `tempfile.TemporaryDirectory()`. The immutable production dataset at `data/raw/tabular/2019/flight_with_weather_2019.csv`, the reference ZIP at `data/reference/bts_transtats/original/T_ONTIME_REPORTING_20261019_112232.zip`, and the verified witness at `docs/05-evidence/TS018_201901_MATCHED_SAMPLE_WITNESS.csv` were **never modified, overwritten, or unlinked**.
