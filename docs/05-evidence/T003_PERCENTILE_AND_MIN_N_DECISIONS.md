# T-003: QUYẾT ĐỊNH THUẬT TOÁN PHÂN VỊ (KPI-06) VÀ CHÍNH SÁCH NGƯỠNG CỠ MẪU TỐI THIỂU (MIN-N RANKING POLICY)

- **Mã nhiệm vụ:** `T-003` (Sub-task 3: Percentile Algorithms & min-N Policy — Bản cập nhật R1)
- **Gate:** `G2` (Data Quality, Cohort & Metric Contracts)
- **Ngày thực hiện:** 2026-10-14
- **Vai trò:** Senior Big Data Engineer, Statistical Methodology Reviewer & Data Quality Auditor
- **Trạng thái đề xuất:** **`PROPOSED_DECISION_PENDING_REVIEW`** (Trình Reviewer xem xét, không tự gán nhãn `APPROVED`)
- **Văn bản tuân thủ:** [`AGENTS.md`](../../AGENTS.md), [`DATA_CONTRACT.md`](../02-design/DATA_CONTRACT.md), [`KPI_SPEC.md`](../02-design/KPI_SPEC.md), [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) (tiêu chí `TS-008`), [`DECISIONS.md`](../02-design/DECISIONS.md).

---

## 1. Hợp đồng Kỹ thuật Thuật toán Phân vị cho KPI-06 (P50 & P90)

### 1.1. Bối cảnh Bài toán Kỹ thuật Big Data
Trong phân tích hiệu suất chuyến bay, trung bình số học (`KPI-03`) rất nhạy cảm với các ca trễ cực đoan (chẳng hạn các chuyến bay bị hoãn sâu $1,000$ đến $4,405$ phút do bão tuyết kéo dài). Do đó, `KPI-06` (gồm `KPI-06-P50` — trung vị và `KPI-06-P90` — phân vị 90) là chỉ số thiết yếu để đo lường độ trễ điển hình và mức độ nghiêm trọng của đuôi phân phối trễ.

Tuy nhiên, trên quy mô dữ liệu phân tán 9 năm ($54.67$ triệu dòng, trung bình $6$ đến $7$ triệu dòng mỗi năm):
- **Phân vị chính xác liên tục (*Exact Continuous Percentiles*):** Đòi hỏi gom toàn bộ dữ liệu của phân vùng hoặc phân nhóm về một executor để sắp xếp toàn cục (*global sort*). Khi nhóm phân tích có kích thước lớn (ví dụ toàn bộ 7.16 triệu dòng năm 2019), thao tác này dẫn đến rủi ro tràn bộ nhớ (*Out-Of-Memory — OOM*) và làm giảm nghiêm trọng hiệu năng tính toán phân tán của Spark.
- **Phân vị xấp xỉ (*Approximate Percentiles*):** Sử dụng các cấu trúc dữ liệu phác họa (*data sketch* như Greenwald-Khanna GK sketch), cho phép tính toán song song, phân tán với bộ nhớ cố định và kiểm soát sai số thứ hạng lý thuyết.

### 1.2. Phân biệt Bản chất Toán học: Sai số Thứ hạng vs Sai số Giá trị Tuyệt đối

Theo tài liệu đặc tả chính thức của Apache Spark ([Spark SQL Built-in Functions: `percentile_approx`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.percentile_approx.html)):
> `percentile_approx(col, percentage [, accuracy])` — Trả về phân vị xấp xỉ của cột số `col`, là giá trị nhỏ nhất trong các giá trị đã sắp xếp sao cho không quá tỷ lệ `percentage` số phần tử nhỏ hơn giá trị đó.

Cần phân định rạch ròi hai khái niệm sai số mà vòng đánh giá trước đã nhầm lẫn:
1. **Sai số thứ hạng tương đối (*Rank Error* $\epsilon_{\text{rank}}$):**
   - Thuật toán GK sketch bảo đảm sai số thứ hạng tương đối có chặn trên:
     $$\epsilon_{\text{rank}} \le \frac{1}{\text{accuracy}}$$
   - Với `accuracy = 10,000`, sai số thứ hạng tối đa là $\epsilon_{\text{rank}} \le 0.0001$ ($0.01\%$). Nghĩa là phần tử được chọn có vị trí phân vị thực tế nằm trong khoảng $[p - 0.0001, p + 0.0001]$.
2. **Sai số giá trị tuyệt đối tính bằng phút (*Absolute Value Error* $\Delta y$):**
   - Sai số giá trị phụ thuộc vào hàm mật độ xác suất $f(y)$ tại điểm phân vị:
     $$\Delta y \approx \frac{\Delta \text{rank}}{f(y)}$$
   - Nếu phân phối có khoảng trống lớn (*gap*) hoặc đuôi phân phối rất thưa (ví dụ phân phối trễ bay có đuôi dài từ 20 đến 4405 phút), một sai số thứ hạng rất nhỏ $0.01\%$ vẫn có thể chuyển đổi thành sai số giá trị tuyệt đối lớn tính bằng phút.
   - **Đính chính khoa học:** Tuyệt đối không tuyên bố rằng `accuracy = 10000` bảo đảm sai số tuyệt đối dưới $0.1$ hay $0.5$ phút cho mọi phân phối bất kỳ.

### 1.3. Minh họa trên Hai Bộ Dữ liệu Kiểm chứng Chuẩn

#### Trường hợp 1: Fixture có đuôi cực đoan `[10.0, 20.0, 4405.0]` ($N=3$)
- **Nội suy liên tục chính xác (*Exact Continuous Interpolation*):**
  - Trung vị $p=0.5$: Vị trí rank $k = 0.5 \times (3 - 1) = 1.0 \implies \text{P50} = 20.0$ phút.
  - Phân vị 90 $p=0.9$: Vị trí rank $k = 0.9 \times (3 - 1) = 1.8 \implies \text{P90} = 0.2 \times 20.0 + 0.8 \times 4405.0 = \mathbf{3528.0}$ phút.
- **Phân vị xấp xỉ / rời rạc trong PySpark (`percentile_approx`):**
  - Hàm `percentile_approx` trả về một **giá trị quan sát thực tế trong tập dữ liệu** (hoặc giá trị trọng tâm centroid). Với $N=3$, phần vị 90 sẽ trả về giá trị quan sát $\mathbf{4405.0}$ phút (hoặc $20.0$ tùy định nghĩa bậc thang).
  - Khoảng chênh lệch giữa $3528.0$ và $4405.0$ là $877.0$ phút, hoàn toàn là do **sự khác biệt về định nghĩa toán học** giữa phép nội suy liên tục và hàm rời rạc của Spark, không phải là lỗi tính toán.

#### Trường hợp 2: Fixture 100 phần tử liên tục từ $-10.0$ đến $+89.0$ ($N=100$, bước $1.0$)
- **Nội suy liên tục chính xác:**
  - Vị trí $p=0.5$: $k = 0.5 \times 99 = 49.5 \implies \text{P50} = 0.5 \times 39.0 + 0.5 \times 40.0 = \mathbf{39.5}$.
  - Vị trí $p=0.9$: $k = 0.9 \times 99 = 89.1 \implies \text{P90} = 0.9 \times 79.0 + 0.1 \times 80.0 = \mathbf{79.1}$.
- **Phân vị xấp xỉ / rời rạc trong PySpark:**
  - Trả về một số nguyên quan sát trong mảng: $\text{P50} \in \{39.0, 40.0\}$ và $\text{P90} \in \{79.0, 80.0\}$.
  - Chênh lệch giữa giá trị xấp xỉ rời rạc và giá trị nội suy liên tục trên mảng $N=100$ có bước nhảy $1.0$ này:
    - Đối với P50 ($p=0.5$): $\|40.0 - 39.5\| = 0.5$ phút.
    - Đối với P90 ($p=0.9$): $\|80.0 - 79.1\| = 0.9$ phút (sai số so với mốc liên tục Type 7 được chặn bởi $\le 0.9$ phút, tương ứng $\le 1.0$ đơn vị bước lưới rời rạc; sai số so với thống kê thứ tự mẫu rời rạc exact là $0.0$ phút).
  - **Cảnh báo giới hạn toán học:** Khoảng chênh lệch $\le 0.9$ phút (hay $\le 1.0$ bước nhảy) này **chỉ là đặc tính đo lường quan sát (*measured value error*) trên tập dữ liệu phân bố đều bước $1.0$ cụ thể này**, tuyệt đối **không phải là cam kết sai số tuyệt đối $\le 1.0$ phút cho mọi dataset bất kỳ** chỉ dựa vào tham số `accuracy=10000`.

### 1.4. Đề xuất Kiến trúc cho Đồ án & Quy trình Benchmark tại Gate G5

1. **Khuyến nghị Lựa chọn PySpark (`FP-DEC-015` — PROPOSED):**
   - Đề xuất áp dụng hàm chuẩn của PySpark cho pipeline xử lý lớn:
     ```python
     percentile_approx(col("ARR_DELAY"), array(lit(0.5), lit(0.9)), accuracy=10000)
     ```
   - **Trạng thái Quản trị:** Giữ nguyên ở trạng thái **`PROPOSED`** (chờ phê duyệt chính thức trước G3/G5), chưa tuyên bố `APPROVED` hoặc test Spark đã PASS ở G2. Kết quả Spark ở G2 giữ trạng thái **`PENDING_G5_VALIDATION`**.
2. **Hệ Quy chiếu Đa tầng trong Kiểm chứng Phân vị:**
   - **Continuous Type-7 Reference:** Mốc chuẩn nội suy tuyến tính liên tục (NumPy / SciPy / R Type 7), dùng để so sánh phương pháp luận.
   - **Exact Discrete / Order-Statistic Reference:** Mốc chuẩn thống kê thứ tự rời rạc mẫu chính xác (tính qua sort toàn phần `row_number()`).
   - **Spark Approximate Output:** Giá trị xấp xỉ thực tế trả về từ `percentile_approx(col, p, 10000)`.
   - **Rank-Error Validation:** Tiêu chí kiểm chứng toán học duy nhất được bảo đảm: $\epsilon_{\text{rank}} \le 1/\text{accuracy} = 0.01\%$.
   - **Measured Value Error:** Đo lường $|\text{Spark} - \text{Exact Discrete}|$ và $|\text{Spark} - \text{Continuous}|$, ghi nhận dưới dạng kết quả quan sát trên từng tập dữ liệu cụ thể, không suy diễn thành chặn trên phổ quát.
3. **Quy trình Kiểm chuẩn Benchmark tại Gate G5 (G5 Empirical Benchmark Protocol):**
   - **Môi trường & Cấu hình:** Apache Spark 3.5.x / PySpark trên Python 3.10+, cấu hình executor memory/cores rõ ràng.
   - **Phân phối thử nghiệm:** Phân phối chuẩn $N(0, \sigma^2)$, phân phối đều $U(a, b)$, và phân phối trễ thực nghiệm từ 1 năm dữ liệu thật ($N \approx 7,000,000$ dòng).
   - **Kích thước mẫu kiểm chuẩn:** $10^4, 10^5, 10^6$ và full partition ($7 \times 10^6$).
   - **Chỉ số đo lường:** Thời gian thực thi, Peak Execution Memory, sai số thứ hạng thực tế và sai số phút đo lường được.
4. **Chuẩn hóa Hợp đồng Siêu dữ liệu Đầu ra (Metadata Contract):**
   Mọi bảng kết quả có `KPI-06` phải xuất kèm các trường siêu dữ liệu minh bạch:
   - `percentile_algorithm`: `"pyspark_percentile_approx_gk"`
   - `sketch_accuracy`: `10000`
   - `rank_error_bound`: `0.0001`
   - `interpolation_mode`: `"discrete_observed_value"`
   - `validation_status`: `"PENDING_G5_VALIDATION"`

---

## 2. Chính sách Ngưỡng Cỡ Mẫu Tối thiểu (min-N Policy for Rankings)

### 2.1. Phân tích Khoa học về Biên Sai số và Tính Đại diện Thống kê

Tại vòng T-003 trước, có tuyên bố rằng *"min-N bảo đảm biên sai số 95% không vượt quá $\pm 3.0\%$ cho mọi bảng xếp hạng"*. Báo cáo R1 này thực hiện hiệu chỉnh và phân định rạch ròi về mặt phương pháp luận:

Công thức biên sai số thống kê ở khoảng tin cậy $95\%$ cho một tỷ lệ nhị thức $p$:
$$\text{MoE}_{95\%} = 1.96 \times \sqrt{\frac{p(1 - p)}{N}}$$

Với tỷ lệ trễ đến trung bình toàn quần thể $p \approx 0.185$ ($18.5041\%$ theo audit):
$$\sqrt{p(1-p)} = \sqrt{0.185 \times 0.815} = \sqrt{0.150775} \approx 0.3883$$

Kiểm tra biên sai số thực tế tại các ngưỡng cỡ mẫu:
- **Tại $N = 100$ (Ngưỡng tuyến bay `route-year`):**
  $$\text{MoE} = 1.96 \times \frac{0.3883}{\sqrt{100}} = 1.96 \times 0.03883 \approx \mathbf{0.0761} \quad (\mathbf{\pm 7.61\%})$$
- **Tại $N = 365$ (Ngưỡng sân bay `airport-year`):**
  $$\text{MoE} = 1.96 \times \frac{0.3883}{\sqrt{365}} = 1.96 \times \frac{0.3883}{19.105} \approx \mathbf{0.0398} \quad (\mathbf{\pm 3.98\%})$$
- **Tại $N = 645$ (Điểm hòa vốn đạt sai số $3\%$):**
  $$\text{MoE} = 1.96 \times \frac{0.3883}{\sqrt{645}} \approx \mathbf{0.0300} \quad (\mathbf{\pm 3.00\%})$$
- **Tại $N = 1,000$ (Ngưỡng hãng hàng không `carrier-year`):**
  $$\text{MoE} = 1.96 \times \frac{0.3883}{\sqrt{1000}} = 1.96 \times 0.01228 \approx \mathbf{0.0241} \quad (\mathbf{\pm 2.41\%})$$

#### Kết luận Phương pháp luận Khoa học:
1. Mức đảm bảo sai số $\text{MoE} \le \pm 3.0\%$ **chỉ thỏa mãn khi $N \ge 645$**, do đó chỉ áp dụng được cho nhóm Hãng hàng không ($N_{\min} = 1,000$).
2. Đối với Sân bay ($N_{\min} = 365$), biên sai số là $\approx \pm 4.0\%$. Đối với Tuyến bay ($N_{\min} = 100$), biên sai số lên tới $\approx \pm 7.6\%$.
3. **Bản chất dữ liệu:** Dữ liệu chuyến bay là **dữ liệu quan sát hành chính (*observational census*)**, có sự tương quan chuỗi thời gian, ảnh hưởng dây chuyền thời tiết và phân cụm mạng bay, **không phải là mẫu ngẫu nhiên độc lập (i.i.d.)**.
4. **Bản chất của các ngưỡng min-N:** Các con số $1000 / 365 / 100$ là **ngưỡng kinh nghiệm thực hành kỹ thuật (*heuristic operational minimums*)** nhằm cân bằng giữa việc loại bỏ biến động ngẫu nhiên của các nhóm quá nhỏ với việc duy trì độ bao phủ thông tin của các sân bay và tuyến bay địa phương.

### 2.2. Bảng Phân tầng Ngưỡng min-N Thống nhất Toàn diện

Mẫu số $N$ dùng để xét ngưỡng bắt buộc phải là **$N_{\text{valid}}$ (`count_metric_valid`) của chính chỉ số đang xếp hạng**, không dùng tổng số dòng thô.

| Chiều phân nhóm xếp hạng | Ngưỡng Tối thiểu ($N_{\min}$) | Ngưỡng Cảnh báo ($3 \times N_{\min}$) | Biên sai số MoE ($95\%$, $p=0.185$) | Ý nghĩa Thực hành Kỹ thuật |
|---|:---:|:---:|:---:|---|
| **Hãng theo Năm (`carrier-year`)** | **$1,000$ chuyến** | **$3,000$ chuyến** | $\pm 2.41\%$ tại $N_{\min}$ | Ngay cả hãng nhỏ nhất có mặt 9 năm (Horizon Air `QX`) vẫn có $\approx 20,000$ chuyến. Ngưỡng 1,000 loại bỏ hoàn toàn nhiễu mẫu nhỏ. |
| **Sân bay theo Năm (`airport-year`)** | **$365$ chuyến** | **$1,095$ chuyến** | $\pm 3.98\%$ tại $N_{\min}$ | Tương đương tối thiểu **$1$ chuyến/ngày** trong năm. Ngưỡng cảnh báo $1,095$ tương đương trung bình $3$ chuyến/ngày. |
| **Tuyến bay theo Năm (`route-year`)** | **$100$ chuyến** | **$300$ chuyến** | $\pm 7.61\%$ tại $N_{\min}$ | Tương đương tối thiểu **$2$ chuyến/tuần** trên tuyến có hướng. Ngưỡng cảnh báo $300$ tương đương $\approx 6$ chuyến/tuần. |

### 2.3. Quy tắc Xếp hạng và Xử lý Đồng hạng (Ranking & Tie-Breaking Rules)

1. **Chiều sắp xếp:**
   - Xếp hạng On-time: Sắp xếp **tăng dần** theo tỷ lệ trễ (`KPI-02` hoặc `KPI-04`). Hãng/Sân bay/Tuyến bay có tỷ lệ trễ thấp nhất xếp hạng 1 (tốt nhất).
2. **Quy tắc giải quyết đồng hạng (*Tie-Breaking*):**
   - Nếu hai nhóm có cùng tỷ lệ trễ đến $\ge 15$m (ví dụ cùng $12.50\%$): Tiêu chí phụ thứ nhất là **độ trễ trung bình có dấu `KPI-03` thấp hơn** sẽ xếp trên.
   - Nếu vẫn bằng nhau: Xếp đồng hạng (`min_rank` hoặc `dense_rank`), sắp xếp thứ tự hiển thị ổn định theo bảng chữ cái mã định danh nhóm (`OP_CARRIER`, `ORIGIN`, `DEST`).
3. **Ba Trạng thái Phân loại Nhóm trong Bảng Xếp hạng:**
   - **`min_n_status = "SUPPRESSED"` (Ẩn cứng):** Khi $N_{\text{valid}} < N_{\min}$. Cột thứ hạng `rank = null`. Nhóm vẫn được lưu trong bảng kết quả chi tiết, nhưng bị loại khỏi các bảng xếp hạng công khai (Top 10 / Bottom 10).
   - **`min_n_status = "LOW_SAMPLE_CAUTION"` (Xếp hạng kèm cảnh báo):** Khi $N_{\min} \le N_{\text{valid}} < 3 \times N_{\min}$. Được gán thứ hạng bình thường nhưng bắt buộc hiển thị cờ cảnh báo mẫu nhỏ và số lượng chuyến bay thực tế.
   - **`min_n_status = "SUFFICIENT"` (Đủ điều kiện thống kê):** Khi $N_{\text{valid}} \ge 3 \times N_{\min}$. Thứ hạng đầy đủ và ổn định.

---

## 3. Khuyến nghị Quản trị

- Quyết định kiến trúc **`FP-DEC-015`** (Thuật toán phân vị PySpark) và **`FP-DEC-016`** (Chính sách min-N phân tầng) tiếp tục được duy trì ở trạng thái **`PROPOSED_DECISION_PENDING_REVIEW`**.
- Không tự ý tuyên bố các quyết định này đã được `APPROVED` trước khi có sự chấp thuận chính thức từ Reviewer.
