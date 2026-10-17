# T007_FULL_SOURCE_INTEGRITY_REPORT — T007-02A & T007-02B Source Inventory & Real Candidate SHA-256 Baseline

**Document ID:** `T007-FULL-SOURCE-INTEGRITY-20261017`  
**Task:** `T-007` (`T007-02A` & `T007-02B`)  
**Parent Gate:** `G4` (`PLANNED / NOT_COMPLETED`)  
**Date:** `2026-10-17`

---

## 1. Executive Summary

This report documents:
1. **Reconciliation of `AUDITED_SOURCE_INVENTORY`** in `src/flight_pipeline/ingestion/source_validator.py` with the canonical G1 baseline metadata (`docs/05-evidence/inputs/schema_2016.json`..`schema_2024.json` and `docs/05-evidence/inputs/data_inventory.md`) and physical raw CSV files on disk (`data/raw/tabular/2016..2024/flight_with_weather_{year}.csv`).
2. **Fail-Closed Path & Boundary Hardening (`T007-02A`):** Symlink/reparse-point rejection across every ancestor component (`lstat` + Win32 `FILE_ATTRIBUTE_REPARSE_POINT`), strict `inventory == {2016..2024}` completeness, strict year-match validation in `approved_baseline_hashes`, and immutable manifest construction (`MappingProxyType` / frozen dataclasses / defensive tuples).
3. **Real Local Candidate SHA-256 Computation (`T007-02B`):** Read-only 1 MB streaming SHA-256 verification across all 9 physical raw CSV files (`15,196,366,173` bytes total, completed in `14.27` seconds at `1,015.65 MiB/s`), stored in `docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json` with status `LOCAL_HASH_COMPUTED_UNAPPROVED` and upstream provenance `IDENTITY_UNVERIFIED` (`OR-08`).

---

## 2. Canonical 9-Year Raw CSV Inventory & Candidate SHA-256 Hashes

All 9 files were verified read-only (zero modifications to byte size or `mtime_ns` before vs. after hashing):

| Year | Relative Path | Audited & Actual Bytes | Audited Rows (`G1`) | Coverage Notes | Local Candidate SHA-256 (`LOCAL_HASH_COMPUTED_UNAPPROVED`) |
|---|---|---|---|---|---|
| `2016` | `data/raw/tabular/2016/flight_with_weather_2016.csv` | `1,538,427,452` | `5,548,445` | Full year (`366` days) | `4ed92ed732721a38ae28325135fad63436347613674ad96c1b273eb9d44cef34` |
| `2017` | `data/raw/tabular/2017/flight_with_weather_2017.csv` | `1,549,837,485` | `5,596,603` | Full year (`365` days) | `67b8dbd6678576b1a2229ef2dbeec065e0f64d31d688ab8a2ca59c88d2a656f9` |
| `2018` | `data/raw/tabular/2018/flight_with_weather_2018.csv` | `1,941,406,432` | `7,071,817` | Full year (`365` days) | `0398bab8f1b79a5f3bea628b707e18c3af628f37a1daa52de6849fb8bdfc71a3` |
| `2019` | `data/raw/tabular/2019/flight_with_weather_2019.csv` | `1,990,370,667` | `7,268,232` | Full year (`365` days) | `eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a` |
| `2020` | `data/raw/tabular/2020/flight_with_weather_2020.csv` | `1,197,858,795` | `4,447,687` | Full year (`366` days; COVID contraction) | `787981046c9fe0f4884ac207a3d28ea6a7fae98e89535cb9f8a37debb5c7fa5d` |
| `2021` | `data/raw/tabular/2021/flight_with_weather_2021.csv` | `1,600,032,487` | `5,878,239` | Full year (`365` days) | `5b7cc4801a6ff5cf432137632209ebd7aecd3d4a0f83e8920e3525116e88defc` |
| `2022` | `data/raw/tabular/2022/flight_with_weather_2022.csv` | `1,782,648,882` | `6,524,259` | Full year (`365` days) | `45eb45e801d6eeeb16167306fc69a8449177191cfff29bfb5d22285827f53140` |
| `2023` | `data/raw/tabular/2023/flight_with_weather_2023.csv` | `1,847,433,387` | `6,713,590` | Full year (`365` days) | `9c9e20f55d3dd10a127bcdd28680df6547a01a82ad71999b794aff3e1075d7bd` |
| `2024` | `data/raw/tabular/2024/flight_with_weather_2024.csv` | `1,748,350,586` | `6,348,823` | Partial year (`335/366` days; March missing — `OR-05`) | `f938ade95a031088467ab5e75abea2021e541eaf4a4288e564066e100541d5f7` |
| **Total** | **9 files (`2016..2024`)** | **`15,196,366,173`** | **`54,674,003`** | **`OR-05` & `OR-08` tracked** | **`docs/05-evidence/T007_LOCAL_RAW_SHA256_CANDIDATE.json`** |

---

## 3. Reconciliation Note: `schema_YYYY.json` vs Early Design Draft

During Phase A verification, we audited `docs/05-evidence/inputs/schema_2016.json`..`schema_2024.json` and `docs/05-evidence/inputs/data_inventory.md` against the physical files in `data/raw/tabular/`:
- Every single physical file on disk (`2016..2024`) matches `docs/05-evidence/inputs/schema_2016.json`..`schema_2024.json` and `docs/05-evidence/inputs/data_inventory.md` to the exact byte (`15,196,366,173` total bytes).
- An early design draft had transposed byte sizes from an older workspace table; `AUDITED_SOURCE_INVENTORY` in `src/flight_pipeline/ingestion/source_validator.py` was reconciled to match `docs/05-evidence/inputs/schema_2016.json`..`schema_2024.json` and covered by unit test `test_inv_04_inventory_matches_g1_canonical_schema_manifests` in `tests/test_t007_source_validator.py`.

---

## 4. Three-State Hash Governance (`OR-08` & `G3-COND-A`)

`SourceValidator` strictly distinguishes three local hash states and never conflates local SHA-256 with upstream BTS/NOAA authenticity:

1. `LOCAL_HASH_NOT_COMPUTED`: Metadata-only mode (`compute_sha256=False`); checks path security, regular-file status, and exact byte size (`expected_byte_size == actual_byte_size`), while marking `verified=False`.
2. `LOCAL_HASH_COMPUTED_UNAPPROVED`: Streaming SHA-256 computed (`compute_sha256=True`) without a human-signed baseline hash for that year; records `computed_sha256` as candidate baseline (`verified=False`).
3. `LOCAL_HASH_VERIFIED`: Streaming SHA-256 computed and matches the approved baseline hash in `approved_baseline_hashes` (`verified=True`). Even when `LOCAL_HASH_VERIFIED` is achieved, `upstream_identity_status` remains `"IDENTITY_UNVERIFIED"` per `OR-08`.
