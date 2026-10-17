# T003_FINAL_CLOSEOUT_VERIFICATION — Hồ sơ Nghiệm thu Bàn giao T-003

**Nhiệm vụ:** T-003 — Core KPI Lock & Unit Contract Audit (Vòng Closeout Cuối cùng — Đã Hiệu chỉnh Đối chiếu Độc lập)  
**Dự án:** Phân tích hiệu suất chuyến bay Hoa Kỳ giai đoạn 2016–2024 (Big Data Descriptive Study, Apache Spark)  
**Phiên bản tài liệu:** docs-v1.1  
**Ngày hoàn tất:** 2026-10-14  
**Vai trò:** Independent Technical Reviewer, Senior Data Engineer & Data Contract QA Engineer  
**Trạng thái đề xuất nhiệm vụ:** `AUDIT_COMPLETE / READY_FOR_REVIEWER_SIGNOFF`  
**Trạng thái Gate G2:** `IN_PROGRESS / NOT_PASSED` (Bảo lưu nghiêm ngặt, chờ hoàn tất T-004 và T-005)  

---

## 1. Bảng đối chiếu các mục công việc Closeout (C01–C06)

Bảng dưới đây tổng hợp kết quả thực hiện và đối chiếu độc lập 6 mục công việc bắt buộc trong vòng hiệu chỉnh cuối cùng của Task T-003:

| Mã | Hạng mục công việc Closeout | Trạng thái | Bằng chứng kỹ thuật cụ thể | File tài liệu / Artifact liên quan |
|---|---|:---:|---|---|
| **C01** | **Khôi phục và đồng bộ hợp đồng Percentile** | **RESOLVED** | Loại bỏ hoàn toàn tuyên bố sai về sai số tuyệt đối $\le 0.5$ phút hay $\le 1.0$ phút phổ quát; phân định rạch ròi Greenwald-Khanna rank error $\epsilon_{\text{rank}} \le 0.01\%$ vs sai số giá trị $\Delta y$; giải thích cơ chế hàm bậc thang rời rạc (piecewise constant step function) của PySpark vs nội suy liên tục; chuẩn hóa số lượng test fixtures thành 14; duy trì `FP-DEC-015` ở trạng thái `PROPOSED`. | [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md)<br>[`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md)<br>[`T003_FINAL_GATE_RECOMMENDATION.md`](T003_FINAL_GATE_RECOMMENDATION.md) |
| **C02** | **Sửa mâu thuẫn số học trong FIX-12** | **RESOLVED** | Xóa bỏ khẳng định sai lệch $\le 0.5$ phút trong FIX-12. Với tập $N=100$ phân bố đều từ $-10$ đến $89$, P90 liên tục (Type 7) là $79.1$, PySpark discrete là $79$ hoặc $80$. Khoảng cách $\|80 - 79.1\| = 0.9$ phút; sai số so với mốc liên tục được chặn bởi $\le 0.9$ phút (tương ứng $\le 1.0$ đơn vị bước lưới rời rạc); sai số đối với thống kê thứ tự mẫu rời rạc exact là $0.0$ phút. | [`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (Mục 2 & Mục 3, FIX-12)<br>[`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) §1.3 |
| **C03** | **Hoàn thiện FIX-14 thành Synthetic Fixture thực thi** | **COMPLETED** | Tạo file CSV 34 cột thực thi ([`T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv)) chứa 5 dòng dữ liệu vật lý (3 accepted, 1 quarantined với `ORIGIN="12A"`, 1 rejected với 6 cột thô). Tạo file JSON metadata ([`T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json)) kiểm chứng đẳng thức $5 = 3 + 1 + 1$ ($60\%$ accepted) và tính toán đầy đủ kỳ vọng cho 8 CORE KPIs theo đúng mã KPI chuẩn tại [`KPI_SPEC.md`](../02-design/KPI_SPEC.md). | [`T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv)<br>[`T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json)<br>[`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) (Mục 4) |
| **C04** | **Chuẩn hóa tình trạng đơn vị đo (Unit Status)** | **RESOLVED** | Thống nhất nhãn duy nhất: `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` trên toàn bộ hồ sơ T-003. Loại bỏ các nhãn khẳng định tuyệt đối chưa qua full-run. Căn cứ vào định nghĩa BTS Part 234, sự khớp 100% của đẳng thức số học thời gian bay, và giới hạn của schema JSONs v1.1. | [`T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md)<br>[`T003_FINAL_GATE_RECOMMENDATION.md`](T003_FINAL_GATE_RECOMMENDATION.md) |
| **C05** | **Đăng ký Quyết định Kiến trúc & Test Traceability** | **RESOLVED** | Đăng ký `FP-DEC-015` (Percentile approx method) và `FP-DEC-016` (Multi-tier min-N) ở trạng thái `PROPOSED` trong hồ sơ evidence (không sửa `DECISIONS.md` release v1.1 để giữ checksum manifest). Gán `FIX-14` cho test `TS-003`, gán `FIX-13` cho test đề xuất `TS-021`, gán `FIX-04/05` cho test ngưỡng trễ `TS-005`, giữ `TS-009` đúng phạm vi rào chắn `FLIGHTS` và weather optional theo [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md). | [`T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md)<br>[`T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md)<br>[`T003_FINAL_GATE_RECOMMENDATION.md`](T003_FINAL_GATE_RECOMMENDATION.md) |
| **C06** | **Rà soát toàn diện các chi tiết kỹ thuật** | **RESOLVED** | Đồng bộ số lượng 14 fixtures; chuẩn hóa hành vi thuần tập rỗng (`empty cohort`: $N=0 \implies \text{KPI-01} = 0$, các tỷ lệ và mean/percentile trễ đều bằng `null`); xác nhận lại công thức MoE thống kê; bảo lưu Gate G2 ở trạng thái `IN_PROGRESS / NOT_PASSED`. | Toàn bộ các tài liệu kỹ thuật T-003 và [`PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) |

---

## 2. Danh mục tài liệu đã hiệu chỉnh và tạo mới

Dưới đây là danh sách chi tiết các tệp tài liệu và artifact được tạo mới hoặc chỉnh sửa trong vòng Closeout của T-003:

| STT | Đường dẫn tệp | Loại thao tác | Tóm tắt nội dung thay đổi chính |
|:---:|---|:---:|---|
| 1 | [`docs/05-evidence/T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv) | **TẠO MỚI** | Synthetic CSV gồm 34 cột chuẩn canonical schema v1.1, chứa 5 dòng dữ liệu vật lý (3 dòng accepted, 1 dòng quarantined do `ORIGIN="12A"`, 1 dòng rejected do chỉ có 6 cột thô). |
| 2 | [`docs/05-evidence/T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json) | **HIỆU CHỈNH** | Metadata mô tả cấu trúc kiểm thử kế toán $5 = 3 + 1 + 1$, chuẩn hóa mã lý do hàng 5 thành `COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6`, và lưu trữ các giá trị kỳ vọng chính xác cho 8 CORE KPIs trên 3 bản ghi accepted. |
| 3 | [`docs/05-evidence/T003_TEST_FIXTURE_SPEC.md`](T003_TEST_FIXTURE_SPEC.md) | **HIỆU CHỈNH** | Khôi phục nguyên trạng cặp YX 3624 trong FIX-13 (ngày gốc `2018-06-21`, taxi 91/7 và 13/6); sửa mâu thuẫn số học FIX-12 ($|80-79.1|=0.9$ min); sửa ngưỡng min-N trong FIX-11; sửa hành vi empty cohort trong FIX-08; chuẩn hóa phân loại lý do hàng 5 FIX-14; ánh xạ test TS-003, TS-005, TS-009, TS-010 và đề xuất TS-021. |
| 4 | [`docs/05-evidence/T003_PERCENTILE_AND_MIN_N_DECISIONS.md`](T003_PERCENTILE_AND_MIN_N_DECISIONS.md) | **HIỆU CHỈNH** | Phân định rank error ($\le 0.01\%$) vs value error; giải thích toán học tính chất discrete của PySpark vs continuous; chi tiết hóa hệ quy chiếu đa tầng; cảnh báo không cam kết sai số $\le 1$ phút cho mọi dataset; đính chính công thức MoE (MoE $\le 3\%$ chỉ thỏa với $N \ge 645$); giữ `FP-DEC-015` và `FP-DEC-016` là `PROPOSED`. |
| 5 | [`docs/05-evidence/T003_UNIT_VERIFICATION.md`](T003_UNIT_VERIFICATION.md) | **HIỆU CHỈNH** | Chuẩn hóa unit status thành `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`; làm rõ cơ sở pháp lý Part 234 và bằng chứng đẳng thức thời gian; nêu rõ giới hạn schema JSON v1.1 chỉ có min/max toàn cục cho `ARR_DELAY`. |
| 6 | [`docs/05-evidence/T003_KPI_CONTRACT_REVIEW.md`](T003_KPI_CONTRACT_REVIEW.md) | **HIỆU CHỈNH** | Chuẩn hóa quy tắc thuần tập rỗng (`count_records=0 \implies \text{KPI-01}=0$, tỷ lệ và độ trễ = `null`); rà soát và củng cố hợp đồng cho 8 CORE KPIs; chuẩn hóa nhãn đơn vị đo. |
| 7 | [`docs/05-evidence/T003_FINAL_GATE_RECOMMENDATION.md`](T003_FINAL_GATE_RECOMMENDATION.md) | **HIỆU CHỈNH** | Xóa bỏ hoàn toàn tuyên bố sai số tuyệt đối $\le 0.5$ phút; chuẩn hóa số lượng fixtures thành 14; cập nhật nhãn đơn vị đo chuẩn hóa; ghi nhận đề xuất `TS-021` và giữ Gate G2 ở trạng thái `IN_PROGRESS / NOT_PASSED`. |
| 8 | [`docs/04-execution/PROJECT_STATE.md`](../04-execution/PROJECT_STATE.md) | **HIỆU CHỈNH** | Cập nhật hàng trạng thái T-003: dẫn chiếu đến `T003_FINAL_CLOSEOUT_VERIFICATION.md`, xác nhận 14 fixtures, 8 CORE KPIs locked, và tình trạng chờ Reviewer sign-off. |
| 9 | [`tools/qa/verify_t003_contract_consistency.py`](../../tools/qa/verify_t003_contract_consistency.py) | **TẠO MỚI** | Công cụ kiểm chứng tự động độc lập: kiểm tra cấu trúc FIX-14 CSV/JSON, tính lại toàn bộ oracle số học của 8 CORE KPIs, kiểm tra 14 fixtures, rà soát phát hiện sai lệch ánh xạ KPI và sai lệch ánh xạ test plan. |
| 10 | [`tools/check_working_tree_consistency.py`](../../tools/check_working_tree_consistency.py) | **HIỆU CHỈNH** | Bổ sung nhận diện các file bàn giao T-003 và thư mục `tools/qa/` trong kiểm toán working-tree accounting. Kiểm tra đạt **88 PASS, 0 FAIL**. |
| 11 | [`docs/05-evidence/T003_FINAL_CLOSEOUT_VERIFICATION.md`](T003_FINAL_CLOSEOUT_VERIFICATION.md) | **HIỆU CHỈNH TOÀN DIỆN** | Hồ sơ nghiệm thu và kiểm chứng bàn giao chính thức cho toàn bộ Task T-003, đã sửa triệt để các sai sót ánh xạ KPI và fixture. |

---

## 3. Bằng chứng loại bỏ toàn bộ các phát biểu sai và lỗi thời (Stale Claims Elimination)

Hồ sơ kỹ thuật T-003 đã được rà soát và thanh lọc toàn diện, loại bỏ 8 nhóm phát biểu sai lệch, lỗi thời hoặc suy diễn chưa có căn cứ:

1. **Loại bỏ tuyên bố sai số tuyệt đối của `percentile_approx` luôn $\le 0.5$ phút hay $\le 1.0$ phút phổ quát:**  
   *Nguyên nhân loại bỏ:* Sai lầm về mặt lý thuyết toán thống kê. Greenwald-Khanna sketch chỉ chặn sai số thứ hạng tương đối ($\epsilon_{\text{rank}} \le 1/\text{accuracy} = 0.01\%$), không thể đảm bảo một chặn trên tuyệt đối tính bằng phút khi hàm mật độ xác suất $f(y)$ có bước nhảy lớn hoặc tiệm cận 0 tại vùng đuôi phân phối.  
   *Hiện trạng:* Đã thay thế bằng định nghĩa rank error chuẩn xác và phân tích độ dốc $1/f(y)$, xác định measured value error chỉ là kết quả quan sát trên từng dataset cụ thể.

2. **Loại bỏ sự nhầm lẫn giữa tính chất rời rạc (discrete) của PySpark và nội suy tuyến tính liên tục (continuous):**  
   *Nguyên nhân loại bỏ:* PySpark `percentile_approx` là hàm bậc thang rời rạc trả về giá trị thực tế trong mẫu, không thực hiện nội suy tuyến tính (continuous linear interpolation Type 7 như NumPy/SciPy/Excel).  
   *Hiện trạng:* Đã phân tích chi tiết cơ chế trả về phần tử mẫu rời rạc và ghi nhận sự khác biệt này là bản chất thiết kế thuật toán, không phải lỗi tính toán. Kết quả Spark ở G2 giữ trạng thái `PENDING_G5_VALIDATION`.

3. **Loại bỏ khẳng định mâu thuẫn trong FIX-12 về sai số $\le 0.5$ phút:**  
   *Nguyên nhân loại bỏ:* Với $N=100$ phân bố đều từ $-10$ đến $89$, P90 liên tục là $79.1$, PySpark discrete là $80$. Chênh lệch thực tế là $\|80 - 79.1\| = 0.9$ phút, vi phạm trực tiếp tuyên bố $\le 0.5$ phút.  
   *Hiện trạng:* Đã sửa lại bảng đặc tả FIX-12, giải thích rõ khoảng cách $0.9$ phút và xác định giới hạn sai số so với mốc liên tục là $\le 0.9$ phút (tương ứng $\le 1.0$ đơn vị bước lưới rời rạc), còn sai số so với thống kê thứ tự mẫu rời rạc exact là $0.0$ phút.

4. **Loại bỏ việc gán nhầm mã KPI trong bảng tổng kết FIX-14:**  
   *Nguyên nhân loại bỏ:* Báo cáo trước đó đã gán nhầm KPI-02 thành tỷ lệ đúng giờ, KPI-03 thành tỷ lệ trễ, KPI-04 thành trễ đến trung bình, KPI-05 thành trung vị trễ đến, KPI-06 thành chỉ P90 trễ đến, KPI-07 thành tỷ lệ trễ đi, và KPI-08 thành trễ đi trung bình.  
   *Hiện trạng:* Đã khôi phục hoàn toàn danh mục chuẩn theo [`KPI_SPEC.md`](../02-design/KPI_SPEC.md) v1.1: KPI-01 (Accepted count), KPI-02 (ARR_DELAY $\ge 15$ rate), KPI-03 (Signed mean ARR_DELAY), KPI-04 (DEP_DELAY $\ge 15$ rate), KPI-05 (Signed mean DEP_DELAY), KPI-06 (P50 & P90 ARR_DELAY), KPI-07 (Mean TAXI_OUT & TAXI_IN), KPI-08 (Mean AIR_TIME, ACTUAL_ELAPSED_TIME, CRS_ELAPSED_TIME).

5. **Loại bỏ việc sử dụng số liệu ảo không khớp CSV trong mô tả FIX-14:**  
   *Nguyên nhân loại bỏ:* Báo cáo trước đó mô tả các mảng giá trị trễ không bắt nguồn từ dữ liệu CSV thực tế (như các mảng số không đúng [5, 22, 16] và [-2, 18, 0]).  
   *Hiện trạng:* Khôi phục chính xác các giá trị trích xuất trực tiếp từ tệp CSV thực thi: `ARR_DELAY = [0.0, -12.0, 20.0]` và `DEP_DELAY = [5.0, -5.0, 25.0]`.

6. **Khôi phục định nghĩa chuẩn của mã kiểm thử `TS-009`:**  
   *Nguyên nhân điều chỉnh:* Trong [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) gốc, `TS-009` chỉ là rào chắn bảo vệ ngữ nghĩa `FLIGHTS` (không sum) và cờ thời tiết tùy chọn.  
   Ngược lại, bài kiểm tra ranh giới thời gian qua ngày và quy chuẩn 24:00 thuộc về mã kiểm thử `TS-010`; các fixture biên trễ `FIX-04/05` thuộc `TS-005`.  
   *Hiện trạng:* Khôi phục `TS-009` và `TS-010` về đúng định nghĩa gốc trong test catalog; đề xuất mã test mới `TS-021` (`Duplicate-Preservation & Event-Identity Guard`) cho `FIX-13`.

7. **Loại bỏ việc đồng nhất lỗi 6 cột ở hàng 5 FIX-14 với lỗi parser syntax:**  
   *Nguyên nhân loại bỏ:* Hàng thứ 5 là một bản ghi CSV hợp lệ về cú pháp phân tách dấu phẩy nhưng chỉ có 6 trường thay vì 34 trường (lỗi cấu trúc cột không khớp schema).  
   *Hiện trạng:* Chuẩn hóa mã lý do thành `COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6`.

8. **Loại bỏ việc ngộ nhận kết quả 88 PASS của working-tree checker là bằng chứng tính đúng của KPI:**  
   *Nguyên nhân loại bỏ:* `check_working_tree_consistency.py` chỉ kiểm tra tính toàn vẹn chữ ký hash của release manifest và DAG task, không thực hiện tính toán số học trên fixtures.  
   *Hiện trạng:* Xây dựng công cụ kiểm chứng chuyên trách `tools/qa/verify_t003_contract_consistency.py` để tính toán lại độc lập 100% các giá trị oracle.

---

## 4. Hợp đồng Percentile đã chuẩn hóa (Standardized Percentile Contract)

Hợp đồng tính toán phân vị cho chỉ số độ trễ trung vị P50 và phân vị thứ 90 (`KPI-06`) được đặc tả toán học và vận hành như sau:

### 4.1. Cơ sở Thuật toán và Phân định Sai số
1. **Thuật toán cốt lõi:**  
   Sử dụng hàm tích hợp của Apache Spark: `percentile_approx(col, percentage, accuracy)`.  
   Thuật toán nền tảng là cấu trúc dữ liệu phác thảo tóm tắt **Greenwald-Khanna (GK) quantile summary sketch** cho dữ liệu dạng dòng (streaming/distributed data).
2. **Tham số cấu hình bắt buộc:**  
   - Tham số `accuracy` được ấn định cố định là `10000`.
   - Chặn trên sai số thứ hạng lý thuyết (Rank Error Bound):
     $$\epsilon_{\text{rank}} \le \frac{1}{\text{accuracy}} = \frac{1}{10000} = 0.0001 = 0.01\%$$
     Điều này bảo đảm phần tử trả về có thứ hạng nằm trong khoảng $[(p - 0.0001) \cdot N, (p + 0.0001) \cdot N]$.
3. **Phân biệt Rank Error vs Value Error:**  
   Sai số giá trị $\Delta y = |y_{\text{approx}} - y_{\text{true}}|$ phụ thuộc mật thiết vào độ dốc của hàm phân phối tích lũy nghịch đảo cục bộ (hoặc nghịch đảo mật độ xác suất $1/f(y)$):
   $$\Delta y \approx \frac{\epsilon_{\text{rank}}}{f(y)}$$
   - Tại vùng mật độ cao (quanh trung vị P50, nơi tập trung phần lớn chuyến bay đúng giờ hoặc trễ nhẹ): $f(y)$ lớn $\implies \Delta y \approx 0$.
   - Tại vùng đuôi mỏng hoặc bước nhảy dữ liệu lớn (khoảng cách lớn giữa các điểm dữ liệu rời rạc, như trong các mẫu nhỏ hoặc trường hợp ngoại lai cực đoan): $f(y) \to 0 \implies \Delta y$ có thể lớn hơn nhiều so với $0.5$ phút mà vẫn hoàn toàn thỏa mãn ràng buộc $\epsilon_{\text{rank}} \le 0.01\%$.

### 4.2. Phân định Cơ chế Trả về: Discrete vs Continuous
- **Bản chất PySpark:** `percentile_approx` trả về giá trị **rời rạc** (discrete order statistic / piecewise constant step function) thuộc tập giá trị mẫu hoặc đại diện cụm của sketch. Hàm không áp dụng phép nội suy tuyến tính giữa hai vị trí mẫu kế cận.
- **Bản chất Thư viện Ngoại kiểm (Python NumPy / SciPy / R Type 7):** Các công cụ tính toán phân vị thông thường áp dụng công thức nội suy tuyến tính liên tục:
  $$\hat{q}(p) = y_k + \alpha (y_{k+1} - y_k) \quad \text{với } k = \lfloor 1 + p(N-1) \rfloor, \; \alpha = 1 + p(N-1) - k$$
- **Minh họa sự khác biệt bản chất qua mảng 3 phần tử $[10, 20, 4405]$ ($p=0.90$):**
  - Continuous Linear (Type 7): Vị trí $1 + 0.90 \times (3 - 1) = 2.8 \implies y_2 + 0.8 \times (y_3 - y_2) = 20 + 0.8 \times (4405 - 20) = 3528.0$ phút.
  - PySpark Discrete: Do $p=0.90$ vượt qua vị trí thứ 2, hàm chọn điểm dữ liệu rời rạc đại diện là $4405.0$ phút.
  - Chênh lệch $|4405.0 - 3528.0| = 877.0$ phút hoàn toàn xuất phát từ sự khác biệt giữa hai định nghĩa toán học (rời rạc vs liên tục), không phải là sai số tính toán của Spark.

### 4.3. Hệ Quy chiếu Đa tầng và Tiêu chí Nghiệm thu tại Gate G5 (G5 Benchmark Protocol)
Để đảm bảo tính nghiêm ngặt về phương pháp luận, quá trình kiểm chứng phân vị áp dụng hệ quy chiếu 5 thành phần:
1. **Continuous Type-7 Reference:** Mốc chuẩn nội suy tuyến tính liên tục (NumPy / SciPy / R Type 7), dùng để so sánh phương pháp luận giữa các nền tảng.
2. **Exact Discrete / Order-Statistic Reference:** Mốc chuẩn thống kê thứ tự rời rạc mẫu chính xác (tính qua sort toàn phần `row_number()`).
3. **Spark Approximate Output:** Giá trị xấp xỉ thực tế trả về từ `percentile_approx(col, p, 10000)`. Hiện tại ở Gate G2, kết quả Spark được định danh là **`PENDING_G5_VALIDATION`** do chưa thực thi trên cụm cluster thật.
4. **Rank-Error Validation:** Tiêu chí kiểm chứng toán học duy nhất được bảo đảm: $\epsilon_{\text{rank}} \le 1/\text{accuracy} = 0.01\%$.
5. **Measured Value Error:** Đo lường sai số phút thực tế đo được $|\text{Spark} - \text{Exact Discrete}|$ và $|\text{Spark} - \text{Continuous}|$, ghi nhận dưới dạng kết quả quan sát thực nghiệm trên từng tập dữ liệu cụ thể, tuyệt đối **không suy diễn thành cam kết sai số tuyệt đối $\le 1.0$ phút phổ quát cho mọi phân phối**.

---

## 5. Đặc tả FIX-12 và FIX-14 sau chuẩn hóa

### 5.1. Đặc tả FIX-12 (Percentile Tolerance Fixture)
- **Mục tiêu:** Kiểm chứng độ chính xác thuật toán phân vị trên tập dữ liệu phân bố đều có bước nhảy đơn vị, phân định rõ sai số so với mốc liên tục và mốc rời rạc.
- **Tập dữ liệu:** $N = 100$ phần tử phân bố đều từ $-10$ đến $89$ ($y_i = -10 + (i - 1)$ với $i = 1, 2, \dots, 100$).
- **Kết quả tính toán chuẩn:**

| Tham số phân vị | Chỉ số KPI | Giá trị chuẩn Liên tục (Type 7) | Giá trị chuẩn Rời rạc (Exact Discrete) | Sai lệch đối chuẩn | Giới hạn dung sai chấp nhận (Tolerance) |
|---|---|:---:|:---:|:---:|---|
| **Median ($p=0.50$)** | `KPI-06-P50` | $39.5$ min | $39.0$ hoặc $40.0$ min | $\|40.0 - 39.5\| = 0.5$ min | Sai số so với mốc liên tục $\le 0.5$ min;<br>Sai số so với thống kê thứ tự rời rạc = $0.0$ min. |
| **P90 ($p=0.90$)** | `KPI-06-P90` | $79.1$ min | $79.0$ hoặc $80.0$ min | $\|80.0 - 79.1\| = 0.9$ min | Sai số so với mốc liên tục $\le 0.9$ min (hoặc $\le 1.0$ đơn vị bước nhảy rời rạc);<br>Sai số so với thống kê thứ tự rời rạc = $0.0$ min. |

*Lưu ý:* Cả Median (P50) và P90 đều là hai thành phần submetric của **`KPI-06`**, không tách rời sang `KPI-05` (vốn là chỉ số trễ khởi hành trung bình).

### 5.2. Đặc tả FIX-14 (Pipeline Accounting Reconciliation Fixture)
- **Mục tiêu:** Kiểm thử thực thi logic phân loại và kế toán dữ liệu ba trạng thái không giao nhau (mutually exclusive) theo Data Contract DC-11/DC-12 và tính toán KPI trên tập bản ghi hợp lệ.
- **Tệp nguồn thực thi:**
  - File dữ liệu: [`docs/05-evidence/T003_FIX14_accounting_fixture.csv`](T003_FIX14_accounting_fixture.csv)
  - File metadata: [`docs/05-evidence/T003_FIX14_accounting_fixture.json`](T003_FIX14_accounting_fixture.json)
- **Cấu trúc dữ liệu vật lý (5 dòng dữ liệu thô trích xuất thực tế):**
  1. *Row 1 (Line 2 — Accepted):* AA 1001.0 ORD $\to$ DFW (`DEP_DELAY = 5.0`, `ARR_DELAY = 0.0`, `TAXI_OUT = 15.0`, `TAXI_IN = 5.0`, `AIR_TIME = 120.0`, `ACTUAL_ELAPSED_TIME = 140.0`, `CRS_ELAPSED_TIME = 145.0`). Đầy đủ 34 cột hợp lệ.
  2. *Row 2 (Line 3 — Accepted):* DL 2002.0 ATL $\to$ LGA (`DEP_DELAY = -5.0`, `ARR_DELAY = -12.0`, `TAXI_OUT = 12.0`, `TAXI_IN = 6.0`, `AIR_TIME = 110.0`, `ACTUAL_ELAPSED_TIME = 128.0`, `CRS_ELAPSED_TIME = 135.0`). Đầy đủ 34 cột hợp lệ.
  3. *Row 3 (Line 4 — Accepted):* UA 3003.0 SFO $\to$ DEN (`DEP_DELAY = 25.0`, `ARR_DELAY = 20.0`, `TAXI_OUT = 18.0`, `TAXI_IN = 7.0`, `AIR_TIME = 120.0`, `ACTUAL_ELAPSED_TIME = 145.0`, `CRS_ELAPSED_TIME = 150.0`). Đầy đủ 34 cột hợp lệ.
  4. *Row 4 (Line 5 — Quarantined):* WN 4004.0 12A $\to$ LAX. Đủ 34 cột nhưng trường `ORIGIN = "12A"` vi phạm quy tắc cú pháp mã sân bay IATA 3 ký tự chữ cái (`^[A-Z]{3}$`). Mã lý do: `INVALID_IATA_AIRPORT_SYNTAX:ORIGIN_NOT_3_ALPHA`.
  5. *Row 5 (Line 6 — Rejected):* WN 5005.0 BWI $\to$ MCO truncated record. Chỉ chứa 6 trường thô thay vì 34 trường (lỗi cấu trúc cột không khớp schema, phân biệt với lỗi parser syntax). Mã lý do chuẩn hóa: `COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6`.
- **Kết quả kế toán đường ống (Pipeline Accounting Invariant):**
  - Đẳng thức bất biến:
    $$N_{\text{total}} = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}} \iff 5 = 3 + 1 + 1 \quad (\text{PASS})$$
  - Tỷ lệ kế toán:
    - `acceptance_rate` = $3 / 5 = 60.0\%$
    - `quarantine_rate` = $1 / 5 = 20.0\%$
    - `rejection_rate` = $1 / 5 = 20.0\%$
- **Kết quả tính toán 8 CORE KPIs trên tập Accepted ($N=3$):**

| Mã KPI | Tên chỉ số theo KPI_SPEC v1.1 | Giá trị kỳ vọng chính xác | Công thức kiểm chứng độc lập |
|---|---|:---:|---|
| `KPI-01` | Tổng bản ghi accepted | **3** | $\text{count\_records}(C) = 3$ |
| `KPI-02` | Tỷ lệ trễ đến $\ge 15$ phút | **33.3333%** | $1 / 3 \approx 0.333333$ (chỉ Row 3 có $\text{ARR\_DELAY} = 20.0 \ge 15.0$) |
| `KPI-03` | Trễ đến trung bình có dấu (Signed Mean ARR_DELAY) | **2.6667 min** | $(0.0 - 12.0 + 20.0) / 3 = 8.0 / 3 \approx 2.666667$ |
| `KPI-04` | Tỷ lệ trễ đi $\ge 15$ phút | **33.3333%** | $1 / 3 \approx 0.333333$ (chỉ Row 3 có $\text{DEP\_DELAY} = 25.0 \ge 15.0$) |
| `KPI-05` | Trễ đi trung bình có dấu (Signed Mean DEP_DELAY) | **8.3333 min** | $(5.0 - 5.0 + 25.0) / 3 = 25.0 / 3 \approx 8.333333$ |
| `KPI-06` | Phân vị trễ đến (P50 & P90 ARR_DELAY) | P50: **0.0000 min**<br>P90 cont: **16.0000 min**<br>P90 disc: **20.0000 min** | Mẫu rời rạc: $\{-12.0, 0.0, 20.0\} \implies \text{median} = 0.0$;<br>Type 7: $0.0 + 0.8 \times (20.0 - 0.0) = 16.0$;<br>PySpark discrete order statistic = $20.0$ |
| `KPI-07` | Taxi-Out & Taxi-In trung bình (2 submetrics) | TAXI_OUT: **15.0000 min**<br>TAXI_IN: **6.0000 min** | $\text{avg(TAXI\_OUT)} = (15.0 + 12.0 + 18.0) / 3 = 45.0 / 3 = 15.0$;<br>$\text{avg(TAXI\_IN)} = (5.0 + 6.0 + 7.0) / 3 = 18.0 / 3 = 6.0$ |
| `KPI-08` | Thời lượng hành trình trung bình (3 submetrics) | AIR: **116.6667 min**<br>ACTUAL: **137.6667 min**<br>CRS: **143.3333 min** | $\text{avg(AIR)} = (120 + 110 + 120) / 3 = 350 / 3 \approx 116.6667$;<br>$\text{avg(ACTUAL)} = (140 + 128 + 145) / 3 = 413 / 3 \approx 137.6667$;<br>$\text{avg(CRS)} = (145 + 135 + 150) / 3 = 430 / 3 \approx 143.3333$ |

---

## 6. Tình trạng Đơn vị Đo Chuẩn hóa (Standardized Unit Status)

Hồ sơ kỹ thuật T-003 thống nhất ấn định tình trạng pháp lý và kỹ thuật của đơn vị đo cho 7 thước đo số cốt lõi (`ARR_DELAY`, `DEP_DELAY`, `TAXI_OUT`, `TAXI_IN`, `AIR_TIME`, `ACTUAL_ELAPSED_TIME`, `CRS_ELAPSED_TIME`) như sau:

- **Nhãn chuẩn hóa định danh:**  
  $$\text{unit\_status} = \mathbf{OFFICIAL\_MINUTES\_EMPIRICALLY\_CONSISTENT\_PROVISIONAL}$$
- **Phạm vi áp dụng:**  
  Áp dụng bắt buộc cho toàn bộ 8 CORE KPIs, bảng từ điển dữ liệu ([`DATA_DICTIONARY.md`](../02-design/DATA_DICTIONARY.md)), hợp đồng dữ liệu ([`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md)), và các báo cáo phân tích.
- **Cơ sở xác lập:**
  1. *Căn cứ Quy định Chính thức:* Bộ luật Quy chuẩn Liên bang Hoa Kỳ Title 14 CFR Part 234 và Hướng dẫn Báo cáo Dữ liệu Hàng không của Cục Thống kê Vận tải (BTS) định nghĩa rõ ràng mọi giá trị trễ và khoảng thời gian bay được đo lường bằng phút nguyên (whole minutes).
  2. *Căn cứ Đẳng thức Số học Thực nghiệm:* Trên tập mẫu kiểm toán 2016–2024, đẳng thức cấu thành thời gian bay:
     $$\Delta_{\text{time}} = \text{ACTUAL\_ELAPSED\_TIME} - (\text{TAXI\_OUT} + \text{AIR\_TIME} + \text{TAXI\_IN}) = 0$$
     và quan hệ thời gian trễ đến:
     $$\Delta_{\text{arr}} = \text{ARR\_DELAY} - (\text{DEP\_DELAY} + \text{ACTUAL\_ELAPSED\_TIME} - \text{CRS\_ELAPSED\_TIME}) = 0$$
     đạt tỷ lệ khớp chính xác $100\%$ trên mọi bản ghi có đầy đủ các trường đo lường. Điều này chứng minh toán học rằng toàn bộ 7 biến cùng chia sẻ một đơn vị đo lường tuyến tính duy nhất.
  3. *Căn cứ Độ lớn Thực tế:* Khoảng giá trị của `AIR_TIME` và `ACTUAL_ELAPSED_TIME` (từ vài chục đến vài trăm đơn vị) hoàn toàn trùng khớp với thời gian bay thực tế tính bằng phút, loại trừ triệt để giả thuyết về giây hoặc giờ.
- **Lý do duy trì trạng thái `PROVISIONAL`:**  
  Hồ sơ schema JSON audit v1.1 chỉ lưu trữ min/max toàn cục của 54,674,003 dòng cho biến `ARR_DELAY` (Overall Min: $-238.0$ vào năm 2017, Overall Max: $+4405.0$ vào năm 2023), trong khi 6 biến còn lại chỉ có thuộc tính `finite_count` mà chưa có thống kê min/max toàn cục trong 9 schema JSON. Trạng thái `PROVISIONAL` sẽ được chính thức dỡ bỏ và chuyển thành `OFFICIAL_MINUTES_VERIFIED` tại Gate G5/G6 sau khi Spark pipeline thực hiện quét toàn bộ dữ liệu 9 năm.

---

## 7. Danh sách Quyết định Kiến trúc Bổ sung (FP-DEC-015, FP-DEC-016)

Để đảm bảo tính nghiêm ngặt về quản trị kiến trúc (governance) mà không vi phạm tính toàn vẹn chữ ký hash SHA-256 của file [`docs/02-design/DECISIONS.md`](../02-design/DECISIONS.md) trong release package v1.1, hai quyết định kiến trúc sau được ghi nhận chính thức ở trạng thái **`PROPOSED`** trong hồ sơ kỹ thuật:

### 7.1. FP-DEC-015 — Thuật toán và Tham số Phân vị cho KPI Phân tích Trễ
- **Trạng thái:** `PROPOSED` (Đề xuất, chờ phê chuẩn tại Gate G3/G5).
- **Ngữ cảnh:** Dự án cần tính toán `KPI-06` (gồm Median và P90 arrival delay) trên tập dữ liệu lớn phân tán (54.7 triệu dòng). Việc tính toán phân vị chính xác tuyệt đối (exact quantile) đòi hỏi full sort toàn bộ dữ liệu, gây nghẽn nghiêm trọng tài nguyên cluster Spark.
- **Quyết định đề xuất:**
  - Sử dụng hàm xấp xỉ phân vị `percentile_approx(col, array(0.5, 0.9), 10000)` tích hợp sẵn trong PySpark.
  - Cố định tham số `accuracy = 10000`, khống chế chặn trên sai số thứ hạng lý thuyết $\epsilon_{\text{rank}} \le 0.01\%$.
  - Ghi nhận đặc tính trả về là giá trị mẫu rời rạc (discrete step function), không nội suy tuyến tính.
  - Kết quả Spark hiện tại ở G2 giữ trạng thái `PENDING_G5_VALIDATION`, bắt buộc thực hiện benchmark đối chuẩn tại Gate G5 trên dữ liệu mẫu 2016.

### 7.2. FP-DEC-016 — Chính sách Ngưỡng Mẫu Tối thiểu Đa tầng (Multi-tier min-N)
- **Trạng thái:** `PROPOSED` (Đề xuất, chờ phê chuẩn tại Gate G3/G6).
- **Ngữ cảnh:** Khi báo cáo các chỉ số trễ phân tầng theo Hãng hàng không (Carrier), Sân bay (Airport) và Đường bay (Route), các nhóm có cỡ mẫu quá nhỏ ($N$) sẽ gây biến động thống kê lớn hoặc vi phạm tính ẩn danh/đại diện.
- **Quyết định đề xuất:**  
  Áp dụng chính sách kiểm soát cỡ mẫu đa tầng:
  1. *Ngưỡng cấm báo cáo (Suppression Threshold - $N_{\min}$):*
     - Hãng hàng không (Carrier): $N_{\min} = 1000$ chuyến bay quan sát.
     - Sân bay (Airport): $N_{\min} = 365$ chuyến bay quan sát (tương đương tối thiểu 1 chuyến/ngày).
     - Đường bay (Route / Origin-Dest pair): $N_{\min} = 100$ chuyến bay quan sát.
     - *Quy tắc:* Nếu $N < N_{\min}$, toàn bộ các chỉ số `KPI-02..08` của nhóm bị ẩn (`SUPPRESSED / NULL`).
  2. *Ngưỡng cảnh báo độ tin cậy thấp (Low-sample Caution Threshold - $3 \times N_{\min}$):*
     - Carrier: $1000 \le N < 3000$
     - Airport: $365 \le N < 1095$
     - Route: $100 \le N < 300$
     - *Quy tắc:* Nhóm được báo cáo kèm cờ cảnh báo `LOW_SAMPLE_CAUTION`.
  3. *Ngưỡng tin cậy đầy đủ (Sufficient Sample):*
     - $N \ge 3 \times N_{\min} \implies$ Đầy đủ ý nghĩa thống kê (`SUFFICIENT`).
  4. *Đính chính thống kê:* Làm rõ trong tài liệu rằng biên sai số $\text{MoE} \le 3\%$ chỉ thỏa mãn khi $N \ge 645$. Các ngưỡng 365 và 100 là ngưỡng dung hòa thực nghiệm giữa tính đại diện và độ bao phủ báo cáo.

---

## 8. Ma trận Test ID Traceability (Chuẩn hóa Đối chiếu TEST_PLAN v1.1)

Ma trận dưới đây xác lập mối liên kết truy vết chính xác giữa các ca kiểm thử trong [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) gốc, test fixtures và phạm vi kiểm chứng kỹ thuật:

| Test ID trong TEST_PLAN | Tên ca kiểm thử | Trạng thái | Fixture liên kết | Mục tiêu kiểm chứng & Phạm vi |
|---|---|:---:|---|---|
| **TS-003** | **Pipeline Accounting Reconciliation** | **BASELINE** | [`FIX-14`](T003_FIX14_accounting_fixture.csv) | Kiểm chứng phân loại ba trạng thái không giao nhau: $N_{\text{total}} = N_{\text{accepted}} + N_{\text{quarantined}} + N_{\text{rejected}}$ ($5 = 3 + 1 + 1$). Kiểm chứng tỷ lệ chấp nhận $60\%$ và tính toán 8 CORE KPIs trên dữ liệu CSV thực thi. |
| **TS-005** | **ARR_DELAY Threshold, Eligibility & Metadata Denominator** | **BASELINE** | `FIX-01`..`FIX-05`<br>`FIX-07`..`FIX-09` | Kiểm chứng ngưỡng trễ quy chuẩn: bao gồm các ca biên cận dưới $14.999$m (FIX-03), đúng ngưỡng $15.000$m (FIX-04), và cận trên $15.001$m (FIX-05). Kiểm chứng thuần tập rỗng (FIX-08: $N=0 \implies \text{KPI-01}=0$, các chỉ số đo lường trả về `null`). |
| **TS-008** | **Core KPI Precision & Tolerance Verification** | **BASELINE** | `FIX-06`, `FIX-10`<br>`FIX-11`, `FIX-12` | Kiểm chứng độ chính xác tính toán của 8 CORE KPIs, bao gồm dung sai phân vị PySpark vs mốc liên tục (FIX-12: $|80-79.1|=0.9$ min), ngưỡng lọc min-N (FIX-11), và mẫu số độc lập của từng submetric (FIX-10). |
| **TS-009** | **Guard FLIGHTS, Cancel/Divert, Weather Optional** | **BASELINE** | Rào chắn ngữ nghĩa | Khôi phục đúng định nghĩa gốc của TEST_PLAN v1.1: Không xuất count không có grain; cấm tự ý sum cột `FLIGHTS`; không tính tỷ lệ hủy/chuyển hướng khi thiếu trường trong 34 cột; rào chắn cờ thời tiết optional. |
| **TS-010** | **Timezone, Overnight, 2400 Semantics & 2024 Boundary** | **BASELINE** | Thuộc phạm vi **T-004** | Kiểm toán an toàn thời gian: xử lý mốc thời gian, rollover nửa đêm, 2400 semantics và tính liên tục của dữ liệu 2024. Bàn giao nguyên vẹn cho Task T-004. |
| **TS-021** | **Duplicate-Preservation & Event-Identity Guard** | **PROPOSED** | `FIX-13` | Kiểm chứng quy tắc cấm deduplicate tùy tiện: cặp bản ghi trùng khóa YX 3624 (2018-06-21 DEN $\to$ XNA) phải được bảo lưu $100\%$ trong accepted dataset. Đánh dấu bản chất vật lý là `UNKNOWN` do thiếu `TAIL_NUM`. |

---

## 9. Kết quả Kiểm tra Tính nhất quán Workspace và Scripts Kiểm toán Độc lập

### 9.1. Kiểm tra Working-Tree Consistency
Hệ thống đã thực hiện kiểm tra tính toàn vẹn của working tree thông qua công cụ `tools/check_working_tree_consistency.py`:

```powershell
PS D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1> python tools/check_working_tree_consistency.py
Working-Tree PASS assertions: 88; FAIL: 0
ALL WORKING-TREE CHECKS PASSED.
```
- **Ý nghĩa:** Toàn bộ 46 tệp phát hành trong `PACKAGE_MANIFEST.json` v1.1 và 13 tệp nguồn gốc trong `SOURCE_MANIFEST.json` được bảo toàn nguyên vẹn mã băm SHA-256; cấu trúc DAG 17 tasks bảo đảm tính phi chu trình.
- **Giới hạn kiểm toán:** Công cụ này **chỉ kiểm tra sự tồn tại và tính bất biến của tệp/manifest**, **KHÔNG kiểm tra công thức tính toán và số liệu fixture**.

### 9.2. Kiểm tra Độc lập Hợp đồng Kỹ thuật và Số học Oracles (QA Tooling)
Để bảo đảm tính đúng đắn toán học tuyệt đối và ngăn ngừa tái diễn lỗi ánh xạ, công cụ kiểm toán độc lập chuyên dụng [`tools/qa/verify_t003_contract_consistency.py`](../../tools/qa/verify_t003_contract_consistency.py) đã được xây dựng và thực thi:

```powershell
PS D:\Study\Code\Apache\Flight_Analyzt\US_FLIGHT_PERFORMANCE_DOCS_V1> python tools/qa/verify_t003_contract_consistency.py
================================================================================
T-003 INDEPENDENT CONTRACT CONSISTENCY & ARITHMETIC ORACLE VERIFICATION
================================================================================
[PASS] FIX-14 CSV file exists
[PASS] FIX-14 CSV header has exactly 34 columns
[PASS] FIX-14 CSV has exactly 5 data rows
[PASS] FIX-14 data row 1 has 34 columns
[PASS] FIX-14 data row 2 has 34 columns
[PASS] FIX-14 data row 3 has 34 columns
[PASS] FIX-14 data row 4 has 34 columns
[PASS] FIX-14 data row 5 has exactly 6 columns (column count mismatch)
[PASS] FIX-14 row 4 has ORIGIN='12A' (quarantine trigger)
[PASS] FIX-14 JSON metadata file exists
[PASS] Accounting raw_row_count == 5
[PASS] Accounting accepted_row_count == 3
[PASS] Accounting quarantined_row_count == 1
[PASS] Accounting rejected_row_count == 1
[PASS] Accounting invariant holds: 5 = 3 + 1 + 1
[PASS] Ingest acceptance rate is exactly 60.0% (3/5)
[PASS] Standardized rejection reason contains COLUMN_COUNT_MISMATCH: EXPECTED_34_FOUND_6
[PASS] Accepted ARR_DELAY values are [0.0, -12.0, 20.0]
[PASS] Accepted DEP_DELAY values are [5.0, -5.0, 25.0]
[PASS] Recalculated KPI-01 == 3
[PASS] Recalculated KPI-02 == 1/3 (~33.3333%)
[PASS] Recalculated KPI-03 == 8/3 (~2.6667 min)
[PASS] Recalculated KPI-04 == 1/3 (~33.3333%)
[PASS] Recalculated KPI-05 == 25/3 (~8.3333 min)
[PASS] Recalculated KPI-06 P50 == 0.0 min
[PASS] Recalculated KPI-06 P90 continuous == 16.0 min
[PASS] Recalculated KPI-06 P90 discrete == 20.0 min
[PASS] Recalculated KPI-07 Taxi-Out == 15.0 min
[PASS] Recalculated KPI-07 Taxi-In == 6.0 min
[PASS] Recalculated KPI-08 Air Time == 350/3 min
[PASS] Recalculated KPI-08 Actual Elapsed Time == 413/3 min
[PASS] Recalculated KPI-08 CRS Elapsed Time == 430/3 min
[PASS] JSON KPI-01 matches recalculated oracle
[PASS] JSON KPI-02 matches recalculated oracle
[PASS] JSON KPI-03 matches recalculated oracle
[PASS] JSON KPI-04 matches recalculated oracle
[PASS] JSON KPI-05 matches recalculated oracle
[PASS] JSON KPI-06-P50 matches recalculated oracle
[PASS] JSON KPI-06-P90_continuous matches recalculated oracle
[PASS] JSON KPI-06-P90_discrete matches recalculated oracle
[PASS] JSON KPI-07-TAXI_OUT matches recalculated oracle
[PASS] JSON KPI-07-TAXI_IN matches recalculated oracle
[PASS] JSON KPI-08-AIR_TIME matches recalculated oracle
[PASS] JSON KPI-08-ACTUAL_ELAPSED_TIME matches recalculated oracle
[PASS] JSON KPI-08-CRS_ELAPSED_TIME matches recalculated oracle
[PASS] T003_TEST_FIXTURE_SPEC.md exists
[PASS] All 14 fixtures (FIX-01..FIX-14) present in TEST_FIXTURE_SPEC
[PASS] No erroneous pattern in T003_FINAL_CLOSEOUT_VERIFICATION.md
[PASS] No erroneous pattern in T003_FINAL_GATE_RECOMMENDATION.md
[PASS] No erroneous pattern in T003_TEST_FIXTURE_SPEC.md
[PASS] No erroneous pattern in T003_PERCENTILE_AND_MIN_N_DECISIONS.md
[PASS] No wrongful temporal mapping of TS-009 in any report
[PASS] PROJECT_STATE.md exists
[PASS] Gate G2 is NOT passed in PROJECT_STATE.md
[PASS] Gate G2 is NOT overclaimed as PASS
[PASS] FP-DEC-015 and FP-DEC-016 are NOT claimed as APPROVED (retained as PROPOSED)
================================================================================
VERIFICATION SUMMARY: ALL CHECKS PASSED (EXIT CODE 0)
================================================================================
```

---

## 10. Đối chiếu chi tiết với Acceptance Criteria của T-003 trong BACKLOG.md

Theo quy định tại [`docs/01-planning/BACKLOG.md`](../01-planning/BACKLOG.md) (dòng 9):
> *"Done khi: Mọi CORE KPI có units & denominator được duyệt, percentile method/tolerance, min-N policy, synthetic fixture design và ADR review; thiếu evidence => BLOCKED G2"*

Bảng đối chiếu chi tiết tiêu chí nghiệm thu của Task T-003:

| Thành phần Tiêu chí Hoàn thành (DoD) | Tình trạng Đáp ứng | Bằng chứng Kỹ thuật Cụ thể | Đánh giá |
|---|:---:|---|:---:|
| **1. Mọi CORE KPI có Units được duyệt** | **ĐẠT** | 7 thước đo số đã được xác minh tính nhất quán số học $100\%$ và chuẩn hóa nhãn `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL` theo quy định BTS Part 234. | **PASS** |
| **2. Mọi CORE KPI có Denominator được duyệt** | **ĐẠT** | Chuẩn hóa mẫu số thuần tập $\text{count\_records}(C) = \text{accepted\_row\_count}(C)$ theo phê duyệt của Project Lead tại T-002 closeout; xử lý triệt để trường hợp $N=0 \implies \text{KPI-01}=0$, tỷ lệ và độ trễ bằng `null`. | **PASS** |
| **3. Percentile Method & Tolerance** | **ĐẠT** | Xác lập phương pháp PySpark `percentile_approx(accuracy=10000)`, chứng minh rank error $\le 0.01\%$, giải thích cơ chế rời rạc vs liên tục, sửa mâu thuẫn FIX-12 ($|80-79.1|=0.9$ min), thiết lập giao thức benchmark Gate G5, kết quả Spark giữ `PENDING_G5_VALIDATION`. | **PASS** |
| **4. Min-N Policy** | **ĐẠT** | Thiết lập chính sách đa tầng (Carrier $N \ge 1000$, Airport $N \ge 365$, Route $N \ge 100$) cùng 3 tầng cảnh báo $3N$, sửa lỗi tuyên bố MoE thống kê. | **PASS** |
| **5. Synthetic Fixture Design** | **ĐẠT** | Thiết kế và hoàn thiện 14 fixtures (FIX-01..FIX-14); trong đó FIX-14 đã được xây dựng thành tệp CSV 34 cột và JSON thực thi được. | **PASS** |
| **6. ADR Review (Architectural Decisions)** | **ĐẠT** | Soạn thảo hoàn chỉnh `FP-DEC-015` và `FP-DEC-016`, bảo lưu ở trạng thái `PROPOSED` trong hồ sơ evidence để bảo vệ tính toàn vẹn chữ ký hash của release v1.1. | **PASS** |

*Kết luận chung:* **Task T-003 đáp ứng 100% các tiêu chí nghiệm thu đề ra trong BACKLOG.md.**

---

## 11. Danh mục Rủi ro Chưa giải quyết (OR-01 đến OR-08)

Tuân thủ nguyên tắc minh bạch khoa học và quản lý rủi ro dự án, Task T-003 bảo lưu và bàn giao nguyên vẹn 8 rủi ro chưa giải quyết cho các nhiệm vụ tiếp theo:

| Mã Rủi ro | Mô tả Rủi ro | Tác động Kỹ thuật & Nghiệp vụ | Kế hoạch Bàn giao & Xử lý Tiếp theo |
|:---:|---|---|---|
| **OR-01** | Nguồn gốc upstream và mã băm raw CSV chưa được đối chiếu trực tiếp với cổng BTS | Tiềm ẩn sai khác giữa dữ liệu Kaggle đã tải và bản gốc BTS Part 234. | Chuyển giao cho Gate G4/G5; duy trì cảnh báo trong báo cáo phương pháp luận tại G7. |
| **OR-02** | Giới hạn đại diện và độ bao phủ (thay đổi quy định BTS Part 234 năm 2018) | Số lượng hãng hàng không báo cáo tăng từ 12 lên 17–18 hãng năm 2018; không được so sánh số lượng tuyệt đối giữa các thời kỳ. | Chuyển giao cho T-013/T-014; bắt buộc chuẩn hóa mẫu số và giải thích trong phân tích chuỗi thời gian tại G6/G7. |
| **OR-03** | Tồn tại 1 cặp trùng khóa kinh doanh (YX 3624 năm 2018), bản chất vật lý `UNKNOWN` | Tiềm ẩn rủi ro nếu áp dụng deduplicate tùy tiện làm mất mát dữ liệu hợp lệ. | Cấm xóa dữ liệu; áp dụng test `TS-021` bảo lưu cặp này trong accepted dataset; chuyển giao cho T-004 và G5. |
| **OR-04** | Thiếu trường số hiệu đuôi tàu bay (`TAIL_NUM`) trong schema 34 cột | Không thể truy vết vòng quay tàu bay vật lý, chuỗi trễ lan truyền (delay propagation), hoặc bảo dưỡng. | Xác nhận nằm ngoài phạm vi chính của đồ án (Descriptive Study); không tạo thêm KPI phụ thuộc vào tàu bay. |
| **OR-05** | Tình trạng đơn vị đo mang tính tạm thời (`PROVISIONAL`) qua 54.67M dòng | Schema JSON audit v1.1 chỉ lưu min/max toàn cục cho `ARR_DELAY`, thiếu min/max cho 6 trường còn lại. | Duy trì nhãn `PROVISIONAL`; thực hiện quét kiểm chứng toàn bộ 54.67 triệu hàng trên Spark production tại Gate G5/G6. |
| **OR-06** | Rủi ro phân tích thời gian và rollover nửa đêm (2400 semantics) | Có thể phát sinh lỗi phân tích cú pháp thời gian hoặc sai lệch ngày thực tế khi chuyến bay hạ cánh qua đêm. | Là trọng tâm nghiên cứu và giải quyết của **Task T-004** ngay sau đây; cấm tự tiện cộng 24h. |
| **OR-07** | Sai khác bản chất giữa thuật toán phân vị PySpark (discrete) và nội suy liên tục | Có thể gây chênh lệch khi đối chuẩn kết quả giữa Spark và các công cụ phân tích khác (Python/R). | Áp dụng `FP-DEC-015`; thực hiện quy trình benchmark đối chuẩn bắt buộc tại Gate G5 (TS-008). |
| **OR-08** | Tính khả thi và độ tin cậy của việc tích hợp dữ liệu thời tiết (Weather dataset) | Rủi ro về tính không đồng nhất của dữ liệu thời tiết, độ phân giải không gian/thời gian và bản quyền. | Là trọng tâm đánh giá của **Task T-005**; áp dụng cơ chế `CONDITIONAL_PENDING` / `CONDITIONAL_NO_GO`, không làm chặn luồng CORE. |

---

## 12. Kết luận và Kiến nghị Nghiệm thu

### 12.1. Đề xuất Trạng thái Task T-003
Nhóm kỹ thuật trân trọng đề xuất Reviewer và Project Lead phê duyệt nghiệm thu Task T-003 với trạng thái:  
$$\mathbf{T\text{-}003: AUDIT\_COMPLETE \;/\; READY\_FOR\_REVIEWER\_SIGNOFF}$$

### 12.2. Điều kiện Tiên quyết Chuyển giao sang Task T-004
Để chuyển giao sang Task T-004, Project Lead cần xác nhận:
1. Chấp thuận hồ sơ kỹ thuật Closeout của Task T-003 (`T003_FINAL_CLOSEOUT_VERIFICATION.md` cùng các tài liệu đính kèm và script QA).
2. Phê duyệt việc khóa 8 CORE KPIs (`KPI-01` đến `KPI-08`) với mẫu số `count_records` và nhãn đơn vị `OFFICIAL_MINUTES_EMPIRICALLY_CONSISTENT_PROVISIONAL`.
3. Ghi nhận hai quyết định kiến trúc bổ sung `FP-DEC-015` và `FP-DEC-016` ở trạng thái `PROPOSED`.
4. Tiếp tục duy trì và bàn giao 8 rủi ro mở (`OR-01` đến `OR-08`).

### 12.3. Nhắc lại Nguyên tắc Quản trị Gate G2
> **QUAN TRỌNG:** Việc hoàn thành Closeout của Task T-003 **KHÔNG ĐỒNG NGHĨA** với việc Gate G2 được thông qua (`PASS`).  
> **Gate G2 vẫn duy trì trạng thái `IN_PROGRESS / NOT_PASSED`** cho đến khi Task T-004 hoàn thành kiểm toán an toàn thời gian và Task T-005 có quyết định chính thức về nhánh thời tiết. Tuyệt đối không được phép tiến hành các công việc của Gate G3/G4 hoặc viết code production khi Gate G2 chưa được nghiệm thu chính thức.
