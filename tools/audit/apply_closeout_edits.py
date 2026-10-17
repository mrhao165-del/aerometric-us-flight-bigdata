# Script to apply precise targeted closeout text adjustments
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 1. Update T002_DUPLICATE_ANALYSIS.md
dup_path = ROOT / "docs" / "05-evidence" / "T002_DUPLICATE_ANALYSIS.md"
lines = dup_path.read_text(encoding="utf-8").splitlines()

# Replace lines 127-128 and 141-142
new_lines = []
for line in lines:
    if line.strip().startswith("- Do đó, việc candidate key chứa `OP_CARRIER` chỉ có duy nhất 1 cặp trùng lặp"):
        new_lines.append("   - Cần làm rõ (C03 Resolution): Trong dữ liệu có tồn tại **đúng một nhóm trùng candidate key thuộc cùng hãng khai thác `OP_CARRIER = YX`** (năm 2018). Cặp trùng này khác biệt về mốc giờ vận hành thực tế do hoãn sâu, không phải do trùng lặp dữ liệu codeshare.")
        new_lines.append("   - Ngoại trừ trường hợp đơn lẻ trên, không quan sát thấy hiện tượng trùng lặp khóa mang tính hệ thống nào khác trong cùng hãng khai thác.")
    elif line.strip().startswith("- Việc codeshare có tạo ra bản ghi thừa dưới mã hãng khác hay không là"):
        new_lines.append("   - Việc các chuyến bay liên danh codeshare có bị trích xuất trùng lặp dưới các mã hãng khác nhau (ví dụ một bản ghi tiếp thị mang mã hãng lớn và một bản ghi khai thác mang mã hãng khu vực) hay không là **hoàn toàn không thể xác định được từ các trường hiện có (`NOT_DETERMINABLE_FROM_AVAILABLE_FIELDS`)**, do thiếu trường tiếp thị (`MKT_CARRIER`), số hiệu máy bay (`TAIL_NUM`) hoặc mã định danh hành trình gốc của DOT.")
    elif line.strip().startswith("3. **Quy tắc giám sát drift tại G4/G5:**"):
        new_lines.append("3. **Quy tắc thiết kế kiểm thử tại G4/G5 (Test Fixture Design Scope — C05 Resolution):**")
        new_lines.append("   - Các bài kiểm thử `TS-009` (G2 design / G5 execution), `TS-012` (G5 execution) và `TS-020` (G4 synthetic / G6 full) trong [`TEST_PLAN.md`](../03-quality/TEST_PLAN.md) hiện đang ở trạng thái **thiết kế quy tắc (*SPECIFIED / DESIGN_BASELINE*)**, chưa phải test code đã thực thi trên production.")
    else:
        new_lines.append(line)

dup_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
print("Updated T002_DUPLICATE_ANALYSIS.md successfully.")

# 2. Update PROJECT_STATE.md
ps_path = ROOT / "docs" / "04-execution" / "PROJECT_STATE.md"
ps_lines = ps_path.read_text(encoding="utf-8").splitlines()
new_ps_lines = []
for line in ps_lines:
    if line.startswith("| **T-002** |"):
        new_ps_lines.append("| **T-002** | **AUDIT_COMPLETE / REVIEW_PENDING** | [`T002_FINAL_ACCEPTANCE_CHECK.md`](../05-evidence/T002_FINAL_ACCEPTANCE_CHECK.md) (kèm [`T002_R1_INDEPENDENT_REVIEW.md`](../05-evidence/T002_R1_INDEPENDENT_REVIEW.md), [`T002_FLIGHT_GRAIN_AUDIT.md`](../05-evidence/T002_FLIGHT_GRAIN_AUDIT.md), [`T002_DUPLICATE_ANALYSIS.md`](../05-evidence/T002_DUPLICATE_ANALYSIS.md), [`T002_DENOMINATOR_RECOMMENDATION.md`](../05-evidence/T002_DENOMINATOR_RECOMMENDATION.md)) | Cấp hạt: Scheduled Flight Leg Record; FLIGHTS = 1.0 (100%); 1 cặp trùng khóa YX 3624 (2018, bản chất vật lý UNKNOWN chuyển T-004); Cấm dedup tùy tiện; Mẫu số: count_records; Chờ reviewer sign-off. |")
    else:
        new_ps_lines.append(line)

ps_path.write_text("\n".join(new_ps_lines) + "\n", encoding="utf-8")
print("Updated PROJECT_STATE.md successfully.")
