# TS018_FINAL_STRICT_NUMERIC_REPLAY.md
# Báo Cáo Chạy Lại Kiểm Chứng Hai Nguồn Nghiêm Ngặt Tuyệt Đối (Strict Bitwise Replay)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 — Final Verifier Hardening & Strict Exact Replay  
**Tác giả:** Senior PySpark QA Engineer, Independent Forensic Evidence Auditor  
**Thời điểm thực thi:** 2026-10-20  
**Lệnh thực thi:** `python tools/qa/verify_ts018_two_source_sample_witness.py`  
**Chế độ chạy:** `REQUIRE_STRICT_EXACT = True` & `VERIFY_WITNESS_PINNED_HASH = True`

---

## 1. MỤC TIÊU VÀ TIÊU CHUẨN THẨM ĐỊNH
Báo cáo này công bố kết quả thực thi kiểm chứng thực tế độc lập của công cụ đối soát hai nguồn đã được tăng cường phòng vệ (hardened verifier). Mọi giá trị số đều được trích xuất trực tiếp từ các tệp vật lý nhị phân và đối chiếu ở cấp độ cấu trúc bit dấu phẩy động IEEE-754 64-bit.

---

## 2. KẾT QUẢ ĐỐI SOÁT CHI TIẾT TỔNG THỂ

```text
================================================================================
INDEPENDENT TWO-SOURCE SAMPLE WITNESS VERIFIER (TS-018 - HARDENED)
================================================================================
[WITNESS] Path:   D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1\docs\05-evidence\TS018_201901_MATCHED_SAMPLE_WITNESS.csv
[WITNESS] Bytes:  294436
[WITNESS] SHA256: 942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1
[OK] Sealed witness pinned SHA-256 and byte size verified.
[OK] Candidate BTS ZIP checksum & size verified: 342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6 (29975383 bytes)
[OK] Raw 2019 Dataset CSV checksum & size verified: eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a (1990370667 bytes)

[PHASE 1] Ingesting sample witness records from CSV...
[WITNESS STATS] Total unique witness keys loaded: 1500

[PHASE 2] Replaying against physical Raw Dataset CSV (flight_with_weather_2019.csv)...
[DATASET REPLAY] Witness keys matched in Raw CSV: 1500 / 1500
[DATASET REPLAY] Duplicate key collisions in Raw CSV: 0
[OK] All 1,500 witness rows match raw project CSV across all 7 fields (10,500/10,500 exact).

[PHASE 3] Replaying against physical BTS Reference CSV inside ZIP...
[BTS REPLAY] Witness keys matched in BTS CSV:     1500 / 1500
[BTS REPLAY] Duplicate key collisions in BTS CSV: 0
[OK] All 1,500 witness rows match BTS CSV across all 7 fields (10,500/10,500 exact).

[PHASE 4] Direct Cross-Source Parity Verification (Raw CSV vs BTS CSV)...

[PARITY FIELD-BY-FIELD BREAKDOWN]
Field                  | Bitwise Exact | Signed Zero | Tol Only  | Null-Null | Mismatch  | Max Diff  
---------------------------------------------------------------------------------------------------------
ARR_DELAY              | 1500          | 0           | 0         | 0         | 0         | 0.000000  
DEP_DELAY              | 1500          | 0           | 0         | 0         | 0         | 0.000000  
TAXI_OUT               | 1500          | 0           | 0         | 0         | 0         | 0.000000  
TAXI_IN                | 1500          | 0           | 0         | 0         | 0         | 0.000000  
AIR_TIME               | 1500          | 0           | 0         | 0         | 0         | 0.000000  
ACTUAL_ELAPSED_TIME    | 1500          | 0           | 0         | 0         | 0         | 0.000000  
CRS_ELAPSED_TIME       | 1500          | 0           | 0         | 0         | 0         | 0.000000  
---------------------------------------------------------------------------------------------------------
TOTAL                  | 10500         | 0           | 0         | 0         | 0         |

[CROSS-SOURCE PARITY SUMMARY]
  Total Comparisons:                10,500 (1,500 flights x 7 fields)
  EXACT_BITWISE_MATCH:              10500
  NUMERIC_EQUAL_SIGNED_ZERO_DIFF:   0
  TOLERANCE_ONLY_MATCH:             0
  NULL_NULL_AGREEMENT:              0
  MISMATCH:                         0
  NONFINITE_OR_INVALID_TOKEN:       0

================================================================================
VERIFICATION RESULT: 100% REPRODUCIBLE STRICT EXACT TWO-SOURCE PARITY PASS
================================================================================
  Witness File:        TS018_201901_MATCHED_SAMPLE_WITNESS.csv (SHA-256: 942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1)
  Physical Raw Source: flight_with_weather_2019.csv (SHA-256: eec50211a1a63f37b840977be5ab2e99a008a8d5234c2a12df8eb50862f93b4a)
  Physical BTS Source: T_ONTIME_REPORTING_20261019_112232.zip (SHA-256: 342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6)
  Total Checked Rows:  1,500 unique keys (0 duplicates)
  Total Fields:        10,500 (7 CORE fields x 1,500 flights)
  Bitwise Exact Rate:  100.00% (10500 / 10,500 exact)
  Signed Zero Diff:    0
  Tolerance-Only:      0
  Null-Null:           0
================================================================================
```

Mã thoát tiến trình: **`0`** (`PASS`).

---

## 3. CÁC ĐẶC TRƯNG CHẤT LƯỢNG ĐÃ ĐƯỢC XÁC LẬP
1. **Tính duy nhất của khóa định danh (Key Uniqueness):**
   - 1.500 khóa witness là hoàn toàn duy nhất (0 khóa trùng lặp).
   - Khi quét toàn bộ 583.985 chuyến bay tháng 1/2019 trong CSV dự án thô: 1.500 khóa xuất hiện chính xác 1 lần, **0 lần trùng lặp (duplicate collisions = 0)**.
   - Khi quét toàn bộ 583.985 chuyến bay trong tệp tham chiếu BTS: 1.500 khóa xuất hiện chính xác 1 lần, **0 lần trùng lặp (duplicate collisions = 0)**.
2. **Độ chính xác nhị phân tuyệt đối (Bitwise Exactness):**
   - Không có trường hợp nào chênh lệch signed zero (`+0.0` vs `-0.0`).
   - Không có trường hợp nào cần dựa vào dung sai (`TOLERANCE_ONLY_MATCH = 0`).
   - Sai lệch tối đa giữa hai nguồn vật lý trên toàn bộ 7 trường là: **`0.000000`**.
3. **Phân biệt tính hợp lệ của Null:**
   - Trong tập 1.500 chuyến bay đang khai thác (operating cohort), không có bất kỳ trường nào bị thiếu hụt dữ liệu (0 nulls).
   - Cơ chế parser mới bảo đảm các chuỗi `"NaN"` hay token lỗi không bao giờ có thể bị biến đổi thành null hợp lệ.

---

## 4. TÁI XÁC THỰC 3 VÍ DỤ MINH HỌA VẬT LÝ
1. **Ví dụ 1 (Đến sớm):** `2019-01-10` | `NK 314` | `IAH` $\rightarrow$ `TPA`
   - RAW: `[-6.0, -4.0, 13.0, 8.0, 98.0, 119.0, 121.0]`
   - BTS: `[-6.0, -4.0, 13.0, 8.0, 98.0, 119.0, 121.0]`
   - Bitwise hex: Đồng nhất 100% trên cả 7 trường.
2. **Ví dụ 2 (Đúng giờ):** `2019-01-31` | `UA 753` | `SFO` $\rightarrow$ `EWR`
   - RAW: `[0.0, 0.0, 24.0, 10.0, 295.0, 329.0, 329.0]`
   - BTS: `[0.0, 0.0, 24.0, 10.0, 295.0, 329.0, 329.0]`
   - Bitwise hex: Đồng nhất 100% trên cả 7 trường.
3. **Ví dụ 3 (Trễ cao):** `2019-01-21` | `AA 692` | `PHX` $\rightarrow$ `HNL`
   - RAW: `[1186.0, 1191.0, 28.0, 17.0, 364.0, 409.0, 414.0]`
   - BTS: `[1186.0, 1191.0, 28.0, 17.0, 364.0, 409.0, 414.0]`
   - Bitwise hex: Đồng nhất 100% trên cả 7 trường.

---

## 5. HẠN CHẾ VÀ ĐỊNH DANH QUẢN TRỊ
- **Nhãn bằng chứng:** `2019_RAW_SOURCE_VS_BTS` (Đối soát đơn vị đo lường trực tiếp giữa CSV thô 2019 và BTS TranStats ZIP theo Option B).
- **Hạn chế mẫu:** Giữ nguyên nhãn hạn chế `CONDITIONAL_REMAINDER_SKEW` cho tập mẫu bù phân tầng; đây là kết quả của thuật toán cắt ngưỡng có điều kiện tất định trên tập phần dư, không phải mẫu ngẫu nhiên độc lập phân phối đều của toàn quốc gia.
