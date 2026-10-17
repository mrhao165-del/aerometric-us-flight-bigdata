# T009-R1: RESIDUAL RISKS, TECHNICAL DEVIATIONS & DOWNSTREAM OBLIGATIONS

**Task ID:** `T-009` (Controlled PySpark Bootstrap, Validator Compatibility & Evidence Verification)  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer & Repository Governance Engineer  
**Date:** 2026-10-17  
**Status:** `AUDITED_AND_MANAGED`  

---

## 1. Rà Soát Độ Lệch Kỹ Thuật (Technical Deviations Audit)

Quá trình triển khai kỹ thuật của `T-009` đã được đối soát chặt chẽ với các tài liệu chuẩn tắc cấp cao:
- **Hợp đồng dữ liệu (`DATA_CONTRACT.md`):** Tuân thủ tuyệt đối quy tắc hạch toán dòng DC-11 và định nghĩa mẫu số độ phủ DC-12. Không có bất kỳ độ lệch nào.
- **Từ điển dữ liệu (`DATA_DICTIONARY.md`):** Không có thay đổi schema hoặc kiểu dữ liệu.
- **Kiến trúc PySpark (`ARCHITECTURE.md`):** Cấu trúc module `src/flight_pipeline` và ngân sách bộ nhớ 8 GB heap được tuân thủ chính xác.
- **Quyết định kiến trúc (`DECISIONS.md`):** 17 quyết định FP-DEC-001..017 được bảo tồn 100%.

**Kết luận về độ lệch:** **KHÔNG CÓ ĐỘ LỆCH NGOÀI Ý MUỐN (ZERO UNPLANNED DEVIATIONS)**.

---

## 2. Quản Lý Rủi Ro Tồn Đọng (Residual Risks & Mitigation)

Dựa trên kết quả thực nghiệm tại trạm làm việc cục bộ, các rủi ro kỹ thuật tồn đọng và biện pháp kiểm soát tương ứng được ghi nhận như sau:

| Mã Rủi Ro | Mô Tả Rủi Ro Kỹ Thuật | Mức Độ | Biện Pháp Kiểm Soát & Giảm Thiểu Đã Triển Khai |
|---|---|:---:|---|
| **R-TECH-01** | **Khóa tệp trên Windows NTFS:** Trình quét virus (Windows Defender) hoặc tiến trình nền có thể giữ lock tạm thời trên các tệp parquet trong quá trình move/rename thư mục staging. | Trung bình | Module `publication.py` đã tích hợp vòng lặp thử lại (retry loop) với backoff thời gian ngắn và cơ chế xử lý ngoại lệ an toàn, đảm bảo atomic-like move trên NTFS. |
| **R-TECH-02** | **Áp lực bộ nhớ khi xử lý 54.7 triệu dòng:** Việc chạy Spark local mode trên 16 GB RAM vật lý của máy tính có thể bị áp lực nếu không phân vùng dữ liệu theo từng năm. | Trung bình | Thiết kế kiến trúc đã khóa cứng phân vùng theo năm `YEAR` (2016–2024). T-007 và T-008 bắt buộc phải xử lý dữ liệu theo từng phân vùng năm độc lập, không nạp toàn bộ 9 năm vào RAM cùng lúc. |
| **R-TECH-03** | **Xung đột phiên bản Python giữa Driver và Worker:** Khả năng executor subprocess gọi sai trình thông dịch Python trên Windows. | Thấp | Đã triệt để khắc phục bằng cách thiết lập `PYSPARK_PYTHON = sys.executable` ở cấp độ tiến trình trong `spark_config.py`. |
| **R-TECH-04** | **Bảo trì sổ đăng ký tệp toàn vẹn (Zero-Unrecognized Rule):** Mỗi tệp mới sinh ra trong các task tiếp theo đều bắt buộc phải được đăng ký hash để vượt qua validator. | Thấp | Tiếp tục duy trì quy trình cập nhật tự động `EVIDENCE_DELIVERABLE_REGISTER.json` và kiểm tra bằng `check_working_tree_consistency.py`. |

---

## 3. Nghĩa Vụ Ràng Buộc Với Các Nhiệm Vụ Hạ Nguồn (Downstream Obligations)

Các giai đoạn tiếp theo (khi được Project Lead phê duyệt mở cổng) bắt buộc phải tuân thủ các nghĩa vụ kỹ thuật sau:
1. **Đối với Ingestion Pipeline (`T-007`):**
   - Bắt buộc phải sử dụng hàm `publish_partition_safely()` từ `src.flight_pipeline.storage.publication` để ghi dữ liệu Parquet phân vùng.
   - Bắt buộc phải tạo và ghi `RunManifest` kèm giá trị băm SHA-256 cho từng năm dữ liệu được nạp.
2. **Đối với Data Quality Validation (`T-008`):**
   - Bắt buộc phải sử dụng các hàm vị từ trong `src.flight_pipeline.quality.predicates` (`is_finite_numeric`, `is_valid_arr_delay`, v.v.) để kiểm tra 7 thước đo liên tục.
   - Bắt buộc phải sử dụng model `RowAccounting` để hạch toán chính xác 3 phân loại `accepted`, `quarantined`, `rejected`, bảo đảm không thất thoát dòng dữ liệu nào ($A + Q + R \equiv T$).
3. **Đối với KPI Calculation (`T-010` đến `T-013`):**
   - Chỉ được tính toán trên tập `accepted` (hoặc tập hợp lệ theo đặc tả từng chỉ số) và tuân thủ đúng định nghĩa mẫu số trong `DATA_CONTRACT.md` (DC-12).
