# TS018_FINAL_HARDENING_FINDINGS_AND_FIXES.md
# Báo Cáo Kỹ Thuật Khắc Phục Toàn Diện 5 Điểm Yếu Công Cụ TS-018 (H01–H05)

**Dự án:** US Flight Performance Analysis 2016–2024  
**Nhiệm vụ:** TS-018 — Final Verifier Hardening  
**Tác giả:** Principal Big Data QA Engineer, Security & Numerical Precision Specialist  
**Ngày hoàn thành:** 2026-10-20  
**Tình trạng:** Đã hoàn thành mã nguồn, kiểm thử âm tính và tích hợp vào công cụ chính thức.

---

## 1. TỔNG QUAN 5 ĐIỂM YẾU VÀ GIẢI PHÁP TRIỂN KHAI

| Mã | Phát hiện kỹ thuật (Finding) | Mức độ rủi ro | Giải pháp đã triển khai (Implemented Hardening) | Trạng thái |
| :---: | :--- | :---: | :--- | :---: |
| **H01** | `REQUIRE_STRICT_EXACT` đang mặc định `False`, có thể chấp nhận sai số dung sai khi nghiệm thu. | HIGH | Chuyển mặc định sang `REQUIRE_STRICT_EXACT = True`. Nếu xuất hiện bất kỳ sai số dung sai nào ($\le 10^{-4}$), chương trình ngắt lập tức với `exit=1`. | **RESOLVED** |
| **H02** | `parse_nullable_float()` âm thầm chuyển `"NaN"` và chuỗi hỏng thành `None`, biến token lỗi thành null hợp lệ. | CRITICAL | Xây dựng lớp `ParsedCell` và hàm `parse_numeric_cell()` phân tách độc quyền: `VALID_FLOAT`, `VALID_NULL`, `NONFINITE_OR_INVALID_TOKEN`. Hai nguồn cùng chứa `"NaN"` bị phát hiện và chặn đứng. | **RESOLVED** |
| **H03** | Khái niệm bitwise exact chưa tường minh; chưa tách biệt `+0.0` vs `-0.0` khỏi bitwise match. | MEDIUM/HIGH | Tách riêng trạng thái `NUMERIC_EQUAL_SIGNED_ZERO_DIFF` với `EXACT_BITWISE_MATCH`. Chỉ khi biểu diễn nhị phân IEEE-754 64-bit trùng khớp hoàn toàn mới được tính là bitwise exact. | **RESOLVED** |
| **H04** | Một số negative test chỉ kiểm tra mã thoát khác 0, có nguy cơ chấp nhận lỗi runtime ngoài ý muốn là test pass. | HIGH | Toàn bộ 13 negative test (NEG-W01..W13) bắt buộc khẳng định chuỗi thông báo lỗi đặc thù (chẩn đoán lỗi mục tiêu). Mọi lỗi ngoại lệ (traceback, KeyError) đều bị coi là test thất bại. | **RESOLVED** |
| **H05** | Chưa ghim mã băm bắt buộc của tệp witness; chưa đếm số lần xuất hiện của khóa trong nguồn để tránh ghi đè dictionary. | HIGH | Ghim cứng mã băm `EXPECTED_WITNESS_SHA256` (`942c4769...`) và `294.436` bytes. Bổ sung bộ đếm `Counter` phát hiện trùng lặp khóa trên witness, Raw CSV và BTS CSV. | **RESOLVED** |

---

## 2. CHI TIẾT TRIỂN KHAI TỪNG ĐIỂM YẾU

### 2.1. H01 — Cơ chế Strict Exact bắt buộc cho nghiệm thu TS-018
- **Tệp nguồn:** [tools/qa/verify_ts018_two_source_sample_witness.py](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/verify_ts018_two_source_sample_witness.py) (dòng 36).
- **Mã nguồn cập nhật:**
  ```python
  REQUIRE_STRICT_EXACT = True
  ```
- **Hành vi kiểm soát:** Trong Phase 2, Phase 3 và Phase 4, nếu phát hiện bất kỳ so sánh nào rơi vào nhóm `TOLERANCE_ONLY_MATCH` ($0 < |a - b| \le 10^{-4}$), chương trình in thông báo lỗi chi tiết và thoát với mã lỗi:
  ```python
  if REQUIRE_STRICT_EXACT and total_tol_only > 0:
      raise SystemExit(f"[FAIL] Strict exact mode violation: {total_tol_only} tolerance-only matches detected!")
  ```
- **Kiểm chứng âm tính (NEG-W07):** Khi tiêm sai lệch $+0.00005$ vào `ARR_DELAY`, hệ thống lập tức bắt lỗi fail-closed với mã thoát 1.

---

### 2.2. H02 — Phân biệt NULL hợp lệ với các Token số học không hợp lệ
- **Vấn đề cũ:** Hàm cũ dùng `val.lower() in ("null", "none", "nan", "na")` và `except ValueError: return None`. Điều này khiến chuỗi `"NaN"`, `"Infinity"`, hoặc văn bản rác bị nuốt thành `None`, dẫn đến việc hai tệp cùng chứa `"NaN"` sẽ được phân loại sai thành `NULL_NULL_AGREEMENT`.
- **Cấu trúc mới:**
  ```python
  class ParsedCell:
      def __init__(self, kind: str, value: Optional[float] = None, raw_token: str = ""):
          self.kind = kind  # "VALID_FLOAT", "VALID_NULL", "NONFINITE_OR_INVALID_TOKEN"
          self.value = value
          self.raw_token = raw_token

  def parse_numeric_cell(raw_val: str) -> ParsedCell:
      val = raw_val.strip()
      if val == "" or val.lower() in ("null", "none"):
          return ParsedCell("VALID_NULL", None, raw_val)
      if val.lower() in ("nan", "na", "inf", "-inf", "infinity", "-infinity"):
          return ParsedCell("NONFINITE_OR_INVALID_TOKEN", None, raw_val)
      try:
          f = float(val)
          if math.isnan(f) or math.isinf(f):
              return ParsedCell("NONFINITE_OR_INVALID_TOKEN", None, raw_val)
          return ParsedCell("VALID_FLOAT", f, raw_val)
      except ValueError:
          return ParsedCell("NONFINITE_OR_INVALID_TOKEN", None, raw_val)
  ```
- **Phân loại so sánh:**
  - `cell_a.kind == "VALID_NULL"` và `cell_b.kind == "VALID_NULL"` $\rightarrow$ `NULL_NULL_AGREEMENT`.
  - Có ít nhất một cell là `NONFINITE_OR_INVALID_TOKEN` $\rightarrow$ `NONFINITE_OR_INVALID_TOKEN` (bị loại trừ và báo lỗi fail-closed).
  - Một bên là `VALID_NULL`, một bên là `VALID_FLOAT` $\rightarrow$ `MISMATCH`.

---

### 2.3. H03 — Định nghĩa tường minh Bitwise Exact và Signed Zero Semantics
- **Nguyên tắc toán học IEEE-754:**
  - Hai số thực có cùng giá trị số học `val_a == val_b` (ví dụ `0.0 == -0.0` là `True`), nhưng cấu trúc bit nhị phân khác nhau: `+0.0` là `0x0000000000000000`, trong khi `-0.0` là `0x8000000000000000`.
  - Do đó, `+0.0` vs `-0.0` là **bằng nhau về mặt số học nhưng KHÔNG PHẢI là bitwise exact**.
- **Cơ chế phân loại:**
  ```python
  bits_a = struct.pack(">d", val_a)
  bits_b = struct.pack(">d", val_b)

  if bits_a == bits_b:
      return ("EXACT_BITWISE_MATCH", 0.0)
  elif val_a == val_b:
      return ("NUMERIC_EQUAL_SIGNED_ZERO_DIFF", 0.0)
  elif diff <= 1e-4:
      return ("TOLERANCE_ONLY_MATCH", diff)
  else:
      return ("MISMATCH", diff)
  ```
- **Kết quả trên tập dữ liệu thật:** Số lượng cặp phát sinh `NUMERIC_EQUAL_SIGNED_ZERO_DIFF` là **0**. Toàn bộ 10.500 so sánh đều đạt `EXACT_BITWISE_MATCH` với chuỗi bit trùng khớp tuyệt đối.

---

### 2.4. H04 — Nâng cấp độ tin cậy của bộ Negative Tests
- Đã rà soát và bổ sung toàn diện bộ kiểm thử trong [tools/qa/test_ts018_negative_witness_verification.py](file:///D:/Study/Code/Apache/Flight_Analyzt/US_FLIGHT_PERFORMANCE_DOCS_V1/tools/qa/test_ts018_negative_witness_verification.py) lên **13 kịch bản độc lập**:
  - `NEG-W01`: Bắt lỗi lệch giá trị âm lớn (`-999.0` vs `-6.0`).
  - `NEG-W02`: Bắt lỗi khóa chuyến bay không tồn tại (`2019-01-01|ZZ|9999...`).
  - `NEG-W03`: Bắt lỗi băm tệp witness bị sửa đổi bằng cơ chế `VERIFY_WITNESS_PINNED_HASH = True`.
  - `NEG-W04`: Bắt lỗi đảo dấu độ trễ (`-6.0` thành `+6.0`).
  - `NEG-W05`: Bắt lỗi trùng lặp khóa trong witness trước khi phân tích.
  - `NEG-W06`: Bắt lỗi ép giá trị khác 0 thành `0.0`.
  - `NEG-W07`: Bắt lỗi sai số dung sai $+0.00005$ dưới chế độ `REQUIRE_STRICT_EXACT`.
  - `NEG-W08`: Bắt lỗi bất đồng null vs số thực.
  - `NEG-W09`: Bắt lỗi giá trị không hữu hạn (`"NaN"`).
  - `NEG-W10`: Bắt lỗi tráo đổi ngày bay (`2019-01-10` thành `2019-01-20`).
  - `NEG-W11`: Kiểm chứng chống false-pass khi cả hai bên cùng chứa `"NaN"`.
  - `NEG-W12`: Kiểm chứng phân tách `+0.0` vs `-0.0` khỏi nhóm bitwise exact.
  - `NEG-W13`: Kiểm chứng parser từ chối các chuỗi không phân tích được từ việc biến thành null.
- Mọi test đều khẳng định thông điệp chẩn đoán mục tiêu, không chấp nhận lỗi cú pháp hay ngoại lệ runtime là pass.

---

### 2.5. H05 — Ghim mã băm Witness và phát hiện trùng lặp khóa
- **Ghim mã băm Witness:**
  ```python
  EXPECTED_WITNESS_SHA256 = "942c476994c414378a541d5c84fcbdad35c6aeace1c98891044a085d55c3a9a1"
  EXPECTED_WITNESS_BYTES = 294436
  ```
  Nếu tệp witness bị thay đổi dù chỉ 1 byte, quá trình nghiệm thu sẽ bị chặn đứng ngay tại bước 1.
- **Phát hiện trùng lặp khóa (Duplicate Detection):**
  - Trong witness: Đếm số lần xuất hiện của khóa, chặn đứng nếu có duplicate (`count > 1`).
  - Trong Raw CSV: Dùng `raw_key_occurrences = Counter()` đếm số lần mỗi khóa witness xuất hiện trong tháng 1/2019. Kết quả: **0 duplicate key collisions**.
  - Trong BTS CSV: Dùng `bts_key_occurrences = Counter()` đếm số lần mỗi khóa witness xuất hiện trong BTS CSV. Kết quả: **0 duplicate key collisions**.
  - **Ý nghĩa:** Loại bỏ hoàn toàn nguy cơ một khóa bị trùng lặp nhiều dòng trong nguồn mà bị ghi đè ngầm bởi dictionary của Python.
