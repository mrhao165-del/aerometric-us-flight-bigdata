# T009-UNBLOCK BASELINE & PRE-CHANGE INSPECTION AUDIT

**Task ID:** `T009-UNBLOCK-R1`  
**Gate:** `G4`  
**Auditor:** Senior Software Engineer, Repository Governance Engineer & Independent QA Engineer  
**Timestamp:** 2026-10-17T08:20:00+07:00  
**Status:** `BASELINE_VERIFIED / EXTERNAL_BACKUP_CONFIRMED`  

---

## 1. Mục Đích & Phạm Vi Thực Hiện

Tài liệu này ghi nhận kết quả kiểm toán tiền thực thi cho nhiệm vụ quản trị **`T009-UNBLOCK-R1`**, được Project Lead phê duyệt có giới hạn nhằm:
1. Xác minh hiện trạng Git và các công cụ quản lý phiên bản trước khi can thiệp.
2. Kiểm toán tệp `.gitignore` và chính sách bảo vệ dữ liệu thô / bí mật.
3. Kiểm kê toàn bộ tệp bằng chứng ban đầu trong `docs/05-evidence/T009/` kèm mã băm SHA-256.
4. Thiết lập bản sao lưu ngoại vi an toàn (bên ngoài repository) trước khi chuẩn hóa cấu trúc.

---

## 2. Kết Quả Kiểm Tra Git Baseline & Cấu Hình

| Tiêu chí | Lệnh kiểm tra | Kết quả quan sát thực tế | Đánh giá an toàn |
|---|---|---|:---:|
| **Sự tồn tại của Git** | `Test-Path .git` | `False` | Chưa có Git repository tại root |
| **Git tại thư mục cha** | `Test-Path ..\.git` | `False` | Không có Git repository lồng nhau |
| **Phiên bản Git CLI** | `git --version` | `git version 2.53.0.windows.2` | Sẵn sàng cho khởi tạo cục bộ |
| **Định danh Git User** | `git config user.name` | `mrhao165-del` | Đã cấu hình trên hệ thống |
| **Định danh Git Email** | `git config user.email` | `mr.hao165@gmail.com` | Đã cấu hình trên hệ thống |
| **Chính sách Git Mode** | Lệnh chỉ thị T009-UNBLOCK-R1 | Cho phép `git init` cục bộ | Project Lead đã cấp phép |

---

## 3. Kiểm Toán Tệp `.gitignore` & Bảo Vệ Dữ Liệu Thô

Tệp `.gitignore` hiện tại được ghim cố định trong `PACKAGE_MANIFEST.json` (315 bytes, SHA-256: `cf71bf4e52ec4d214129bf215c182937b71fb43f0cbcc62ef49e100772b55459`).

### Nội dung cấu hình loại trừ:
```text
# Data and generated artifacts - keep outside normal Git
.env
.env.*
!.env.example
__pycache__/
*.pyc
.ipynb_checkpoints/
data/raw/
data/staging/
data/processed/
data/curated/
data/temp/
artifacts/runs/
artifacts/cache/
*.pt
*.parquet
*.csv
# Keep small audited JSON/MD evidence files in docs/05-evidence/inputs/
```

### Đánh giá an toàn:
1. **Dữ liệu thô 14.15 GiB (`data/raw/`):** Được bảo vệ hoàn toàn khỏi Git bởi quy tắc `data/raw/` và `*.csv`.
2. **Dữ liệu phái sinh Parquet (`*.parquet`):** Được loại trừ khỏi Git.
3. **Mô hình đồ thị cấm kỵ (`*.pt`):** Được loại trừ khỏi Git.
4. **Biến môi trường bí mật (`.env`):** Được loại trừ khỏi Git.
5. **Tính bất biến của `.gitignore`:** Không được phép chỉnh sửa `.gitignore` vì sẽ làm sai lệch mã băm kiểm toán trong `PACKAGE_MANIFEST.json`. Việc stage Git phải được thực hiện có kiểm soát bằng cách chỉ định tường minh danh sách tệp.

---

## 4. Kiểm Kê Toàn Bộ Bằng Chứng Ban Đầu của T-009

Trước khi chuẩn hóa, thư mục `docs/05-evidence/T009/` chứa 6 tệp vật lý:

| Đường dẫn tệp ban đầu (trong bản sao lưu ngoại vi) | Kích thước (Bytes) | Mã băm SHA-256 |
|---|---:|---|
| `T009_ORIGINAL/01_DOCUMENT_READING_AND_AUTHORITY_AUDIT.md` | 15.354 | `1c7e4565193b774bf9f80052354e9c39346f513b919f7cb6b73d1fa1f16e017d` |
| `T009_ORIGINAL/02_BASELINE_AND_SCOPE_REPORT.md` | 10.077 | `066e0b1bc4bb0289f0ca2650b2a46586977d230a8fce1284d7507f0733186b80` |
| `T009_ORIGINAL/08_RISK_AND_DEVIATION_REPORT.md` | 7.627 | `8348141315453c30b26ac3e7ecc82265b27641a9a98c9d8ddb0873f927ed2266` |
| `T009_ORIGINAL/10_FINAL_T009_REVIEW.md` | 7.986 | `52b75cb0b7e3a33df85cf8363bd5ff896f860ce9a78c779130db7e01eb2ddfe2` |
| `T009_ORIGINAL/logs/regression_consistency.log` | 1.117 | `ba9999b614afe59010db6a6dba0effd72c9317999b64f17363fab6a394b29988` |
| `T009_ORIGINAL/logs/regression_t006.log` | 2.582 | `d6ac11cc5e83b796d2cc29d713b65d911987445b835e2a3c2c3609d6fbefb5f6` |

---

## 5. Xác Nhận Sao Lưu Ngoại Vi An Toàn

Bản sao lưu đầy đủ đã được tạo lập thành công bên ngoài cây repository tại:  
`D:\Study\Code\Apache\Flight_Analyzt\T009_UNBLOCK_BACKUP_20261017_081700\`

### Danh mục tệp đã sao lưu:
1. `T009_ORIGINAL/` (Chứa toàn bộ 6 tệp gốc của T-009).
2. `EVIDENCE_DELIVERABLE_REGISTER.json.pre_unblock.bak` (51.502 bytes, SHA-256: `870cb2aed459460f0d8da49255948a56238038dff6f55f5ccd7b964dffea0f60`).
3. `BACKUP_MANIFEST.json` (Ghi nhận đầy đủ kích thước byte và SHA-256 của toàn bộ tệp sao lưu).

**Kết luận:** Điều kiện an toàn Phase A hoàn toàn đạt yêu cầu. Sẵn sàng cho Phase B (chuẩn hóa bằng chứng phẳng).
