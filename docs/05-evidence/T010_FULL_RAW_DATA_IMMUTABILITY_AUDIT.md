# T010_FULL_RAW_DATA_IMMUTABILITY_AUDIT.md — Phase 7 Post-Execution Raw Data Integrity Audit

**Gate:** G5  
**Task:** T-010 — Bounded Real-Data Smoke & Resource Benchmark  
**Author:** Repository Governance & Evidence Integrity Auditor  
**Execution Timestamp:** 2026-10-18T11:07:20+00:00 (2026-10-18T18:07:20+07:00)  
**Target File:** `data/raw/tabular/2016/flight_with_weather_2016.csv`  
**Status:** PASS (CONTROLLED)  

---

## 1. Governance Mandate

A core policy of the project repository (enforced in `AGENTS.md`) is:
> **Không sửa/ghi đè data/raw/, nguồn JSON/MD audit, bản gốc ở docs/05-evidence/inputs/.**

This audit proves that despite reading `data/raw/tabular/2016/flight_with_weather_2016.csv` across multiple stages (preflight hash calculation, micro-smoke, January month-smoke, RFC-4180 logical record scan, and full-year Spark execution), the raw source file was accessed in **strictly read-only mode** and was NOT mutated, truncated, or modified in any way.

---

## 2. Pre-Execution vs Post-Execution Physical Audit

The physical properties and cryptographic hash of `data/raw/tabular/2016/flight_with_weather_2016.csv` were captured immediately before Phase 1 and re-verified immediately after Phase 6:

| Audit Parameter | Pre-Execution Baseline | Post-Execution Audit | Delta / Mutation | Compliance |
| :--- | :--- | :--- | :--- | :--- |
| **Physical File Path** | `data/raw/tabular/2016/flight_with_weather_2016.csv` | `data/raw/tabular/2016/flight_with_weather_2016.csv` | Identical path | **PASS** |
| **File Byte Size** | `1,538,427,452` bytes | `1,538,427,452` bytes | `0` bytes | **PASS (Exact)** |
| **Modification Time (mtime)** | `1787484809.8685696` | `1787484809.8685696` | `0.000` seconds | **PASS (Untouched)** |
| **Streaming SHA-256 Hash** | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` | Identical hex hash | **PASS (100% Cryptographic Match)** |
| **Access Mode** | Read-Only | Read-Only | No write handles opened | **PASS** |

---

## 3. Directory Cleanliness Audit

An audit of the raw data directory `data/raw/tabular/2016/` confirmed:
- Zero temporary or sidecar files created (`*.tmp`, `*.bak`, `*.swp`, `*.crc`).
- Exactly 1 file remains in the directory: `flight_with_weather_2016.csv`.
- No write permissions were exercised or requested.

---

## 4. Immutability Verdict

The 2016 raw dataset is **100% untouched, unmutated, and preserved in its original audited state**. Physical bytes, timestamps, and streaming SHA-256 digests match the pre-execution baseline with zero delta.
