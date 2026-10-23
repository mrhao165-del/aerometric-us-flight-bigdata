# -*- coding: utf-8 -*-
"""
tools/export/build_presentation_pptx.py
Generates T016_FINAL_PRESENTATION.pptx with 16 professional widescreen (16:9) slides,
embedded high-resolution charts, structured stat cards, and speaker notes.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from tools.export.report_content import PROJECT_METADATA

OUTPUT_DIR = Path(r"D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES")
CORRECTED_OUTPUT_DIR = OUTPUT_DIR / "corrected"
ANALYTICS_DIR = BASE_DIR / "data" / "analytics" / "runs" / "t014_analysis_2016_2024_v4"
CHARTS_DIR = ANALYTICS_DIR / "charts"

# Color Palette Constants
COLOR_NAVY = RGBColor(26, 54, 93)       # #1A365D Main Navy
COLOR_DARK_SLATE = RGBColor(45, 55, 72) # #2D3748 Header Slate
COLOR_BLUE = RGBColor(49, 130, 206)     # #3182CE Accent Blue
COLOR_TEAL = RGBColor(49, 151, 149)     # #319795 Accent Teal
COLOR_BG_LIGHT = RGBColor(248, 250, 252)# #F8FAFC Slide Light Background
COLOR_CARD_BG = RGBColor(255, 255, 255) # White Card
COLOR_BORDER = RGBColor(226, 232, 240)  # #E2E8F0 Card Border
COLOR_TEXT_MAIN = RGBColor(26, 32, 44)  # #1A202C Body Text
COLOR_TEXT_MUTED = RGBColor(113, 128, 150) # #718096 Secondary Text
COLOR_MUTED = RGBColor(113, 128, 150)   # #718096 Secondary Text
COLOR_WHITE = RGBColor(255, 255, 255)

def create_shape(slide, shape_type, left, top, width, height, fill_color, border_color=None):
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_header(slide, title_text, category_text="NGHIÊN CỨU DỮ LIỆU LỚN HÀNG KHÔNG HOA KỲ (2016–2024)"):
    # Header container
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.name = "Arial"
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_BLUE

    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.name = "Arial"
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY
    p_title.space_before = Pt(2)

def add_bullet_item(text_frame, bold_prefix, text, font_size=13, space_before=6):
    p = text_frame.add_paragraph() if len(text_frame.paragraphs[0].text) > 0 else text_frame.paragraphs[0]
    p.space_before = Pt(space_before)
    r_prefix = p.add_run()
    r_prefix.text = bold_prefix + " "
    r_prefix.font.bold = True
    r_prefix.font.name = "Arial"
    r_prefix.font.size = Pt(font_size)
    r_prefix.font.color.rgb = COLOR_NAVY

    r_text = p.add_run()
    r_text.text = text
    r_text.font.name = "Arial"
    r_text.font.size = Pt(font_size)
    r_text.font.color.rgb = COLOR_TEXT_MAIN

def set_slide_background(slide, color):
    create_shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5), color)

def generate_presentation_pptx(output_dir=None):
    target_dir = Path(output_dir) if output_dir else CORRECTED_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    pptx_path = target_dir / "T016_FINAL_PRESENTATION.pptx"

    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # ==========================================
    # SLIDE 1: TITLE SLIDE (Dark Navy)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, COLOR_NAVY)

    # Accent decorative bar
    create_shape(s1, MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.5), Inches(0.12), Inches(4.5), COLOR_BLUE)

    tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(1.4), Inches(10.5), Inches(4.6))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "BÁO CÁO KHOA HỌC TỔNG KẾT ĐỀ ÁN"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE

    p = tf1.add_paragraph()
    p.text = "PHÂN TÍCH HIỆU SUẤT KHAI THÁC CHUYẾN BAY\nNỘI ĐỊA HOA KỲ GIAI ĐOẠN 2016–2024"
    p.font.name = "Arial"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(8)

    p = tf1.add_paragraph()
    p.text = "Quy Trình Phân Tích Thống Kê Mô Tả Dữ Liệu Lớn Trên Nền Tảng Apache Spark & PySpark"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_before = Pt(8)

    p = tf1.add_paragraph()
    p.text = (
        "• Không gian mẫu: 54,674,003 chuyến bay accepted (2016–2024) | 117 tệp Curated Parquet (3.31 GB)\n"
        "• Khung phân tích: 8 CORE KPIs | 6 chiều tổng hợp (57,015 cohorts) | 684,180 dòng KPI xuất bản\n"
        f"• Đơn vị thực hiện: {PROJECT_METADATA['authors']}\n"
        f"• Snapshot cơ sở: {PROJECT_METADATA['kpi_run_id']} & {PROJECT_METADATA['analysis_run_id']} | Gate G7 | {PROJECT_METADATA['submission_date']}"
    )
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(203, 213, 224)
    p.space_before = Pt(20)

    s1.notes_slide.notes_text_frame.text = (
        "Kính chào Thầy/Cô và Hội đồng. Hôm nay nhóm xin trình bày Báo cáo tổng kết đề án Phân tích hiệu suất "
        "khai thác chuyến bay nội địa Hoa Kỳ giai đoạn 2016–2024 trên nền tảng Dữ liệu lớn Apache Spark và PySpark. "
        "Đề án đã xử lý thành công toàn bộ 54,674,003 bản ghi chuyến bay trong 9 năm liên tục, tính toán 8 CORE KPIs "
        "và trả lời trọn vẹn 5 câu hỏi nghiên cứu khoa học."
    )

    # ==========================================
    # SLIDE 2: RESEARCH MOTIVATION
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, COLOR_BG_LIGHT)
    add_header(s2, "Động Lực Nghiên Cứu & Bài Toán Big Data Hàng Không")

    # 3 Cards Layout
    cards_data = [
        ("Tầm Vóc & Thiệt Hại Mạng Lưới", "Hệ thống Không phận Hoa Kỳ (NAS) kết nối hàng nghìn chặng bay mỗi ngày. Hiện tượng chậm trễ chuyến bay gây thiệt hại ước tính hàng chục tỷ USD/năm (Ball et al., 2010), lãng phí nhiên liệu và gia tăng phát thải carbon."),
        ("Giai đoạn 9 Năm Đặc Biệt (2016–2024)", "Khởi đầu bằng tăng trưởng bùng nổ (2016–2019), tiếp nối bởi cú sốc đứt gãy chưa từng có do đại dịch COVID-19 (2020), và kết thúc bằng làn sóng phục hồi nhu cầu dẫn đến tái tắc nghẽn hạ tầng (2021–2024)."),
        ("Lựa Chọn Nền Tảng Khả Mở", "Quy mô 54.7 triệu bản ghi, 34.5 GB dữ liệu thô. Apache Spark / PySpark được lựa chọn thay thế cho các thư viện xử lý trong bộ nhớ đơn nút như Pandas nhằm đảm bảo khả năng tính toán khả mở, phân vùng dữ liệu tối ưu và thực thi tin cậy trên môi trường thực tế của đồ án (Windows 11, OpenJDK 21 LTS).")
    ]
    for i, (ctitle, cdesc) in enumerate(cards_data):
        cleft = Inches(0.8 + i * 4.0)
        create_shape(s2, MSO_SHAPE.ROUNDED_RECTANGLE, cleft, Inches(1.8), Inches(3.7), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
        create_shape(s2, MSO_SHAPE.RECTANGLE, cleft, Inches(1.8), Inches(3.7), Inches(0.1), COLOR_BLUE)

        tb = s2.shapes.add_textbox(cleft + Inches(0.3), Inches(2.2), Inches(3.1), Inches(4.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = f"0{i+1}"
        p0.font.size = Pt(24)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_BLUE

        p1 = tf.add_paragraph()
        p1.text = ctitle
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_NAVY
        p1.space_before = Pt(6)

        p2 = tf.add_paragraph()
        p2.text = cdesc
        p2.font.size = Pt(13)
        p2.font.color.rgb = COLOR_TEXT_MAIN
        p2.space_before = Pt(12)

    s2.notes_slide.notes_text_frame.text = (
        "Động lực nghiên cứu xuất phát từ tầm quan trọng kinh tế to lớn của ngành hàng không Hoa Kỳ và bài toán xử lý "
        "54.7 triệu bản ghi dữ liệu. PySpark và định dạng Parquet được lựa chọn nhằm cung cấp kiến trúc tính toán khả mở, "
        "quản lý bộ nhớ hiệu quả và độ ổn định cao trên môi trường Windows 11 và Java 21 LTS của đồ án, thay vì dựa vào các công cụ trong bộ nhớ đơn nút như Pandas."
    )

    # ==========================================
    # SLIDE 3: OBJECTIVES & 5 CORE RQS
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, COLOR_BG_LIGHT)
    add_header(s3, "Mục Tiêu Khoa Học & 5 Câu Hỏi Nghiên Cứu (RQ-01..05)")

    rqs = [
        ("RQ-01", "Quy Mô & Tính Quy Luật Mùa Vụ", "Sản lượng chuyến bay biến động như thế nào qua 9 năm? Quy luật mùa vụ theo tháng biểu hiện đỉnh/đáy ra sao? (KPI-01)"),
        ("RQ-02", "Phân Bố Trễ & Đuôi Dài Lệch Phải", "Phân phối trễ cất/hạ cánh có đặc trưng gì? Tại sao Trung vị P50 âm trong khi Mean dương? P90 kéo dãn ra sao? (KPI-02..06)"),
        ("RQ-03", "Hãng Bay, Điểm Nghẽn Hubs & Chặng Bay", "Hiệu suất đúng giờ phân hóa thế nào giữa các hãng? Siêu sân bay nào trễ nhất? Tính bất đối xứng tuyến 2 chiều? (KPI-01..05)"),
        ("RQ-04", "Cú Sốc 2020 & Hiện Tượng Tái Tắc Nghẽn", "Đại dịch tác động thế nào đến sản lượng và độ trễ? Giai đoạn phục hồi 2021–2024 có gây tái tắc nghẽn? (KPI-01..08)"),
        ("RQ-05", "Động Học Lăn Bánh & Đệm Lịch Trình", "Thời gian Taxi chiếm tỷ trọng bao nhiêu trong hành trình? Chiến lược đệm lịch trình (CRS vs Actual) của các hãng? (KPI-07..08)")
    ]
    for i, (rq_code, rq_name, rq_desc) in enumerate(rqs):
        top_y = Inches(1.7 + i * 1.05)
        create_shape(s3, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_y, Inches(11.7), Inches(0.92), COLOR_CARD_BG, COLOR_BORDER)
        create_shape(s3, MSO_SHAPE.RECTANGLE, Inches(0.8), top_y, Inches(1.2), Inches(0.92), COLOR_NAVY)

        tb_code = s3.shapes.add_textbox(Inches(0.8), top_y + Inches(0.2), Inches(1.2), Inches(0.5))
        p_c = tb_code.text_frame.paragraphs[0]
        p_c.text = rq_code
        p_c.alignment = PP_ALIGN.CENTER
        p_c.font.bold = True
        p_c.font.size = Pt(16)
        p_c.font.color.rgb = COLOR_WHITE

        tb_text = s3.shapes.add_textbox(Inches(2.2), top_y + Inches(0.08), Inches(10.1), Inches(0.75))
        tf_t = tb_text.text_frame
        tf_t.word_wrap = True
        p_t1 = tf_t.paragraphs[0]
        p_t1.text = rq_name
        p_t1.font.bold = True
        p_t1.font.size = Pt(14)
        p_t1.font.color.rgb = COLOR_NAVY

        p_t2 = tf_t.add_paragraph()
        p_t2.text = rq_desc
        p_t2.font.size = Pt(11.5)
        p_t2.font.color.rgb = COLOR_TEXT_MAIN
        p_t2.space_before = Pt(2)

    s3.notes_slide.notes_text_frame.text = (
        "Nghiên cứu tập trung vào 5 câu hỏi trọng tâm. Đây là các câu hỏi mang tính bản chất: từ quy mô, hình thái phân phối "
        "đến so sánh hãng, sân bay, cú sốc đại dịch và động học thời gian lăn bánh mặt đất."
    )

    # ==========================================
    # SLIDE 4: DATA SOURCE & MANDATORY LIMITATIONS
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, COLOR_BG_LIGHT)
    add_header(s4, "Không Gian Dữ Liệu & 4 Ràng Buộc Phương Pháp Bắt Buộc")

    # Left: Data Census Card
    create_shape(s4, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_l = s4.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.4))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "Không Gian Mẫu 54.7 Triệu Bản Ghi"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    add_bullet_item(tf_l, "• Nguồn dữ liệu:", "Tổng hợp chuyến bay nội địa Hoa Kỳ 2016–2024.", 12, 10)
    add_bullet_item(tf_l, "• Dân số kiểm duyệt:", "54,674,003 bản ghi accepted (100% tuân thủ Data Contract DC-11).", 12, 6)
    add_bullet_item(tf_l, "• Lưu trữ cột:", "117 tệp Apache Parquet phân tán, 3,308,617,408 bytes (~3.31 GB).", 12, 6)
    add_bullet_item(tf_l, "• Schema nguồn:", "34 cột CSV thô → 17 cột Curated Parquet chuẩn hóa.", 12, 6)
    add_bullet_item(tf_l, "• Bản chất nghiên cứu:", "Thống kê mô tả quan sát (Descriptive Observational Study), không suy diễn quan hệ nhân quả.", 12, 6)

    # Right: 4 Mandatory Constraints
    create_shape(s4, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_r = s4.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.4))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p_r = tf_r.paragraphs[0]
    p_r.text = "4 Ràng Buộc Quản Trị & Khoa Học Bắt Buộc"
    p_r.font.size = Pt(16)
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_BLUE

    add_bullet_item(tf_r, "1. OR-03 (Xác thực đơn vị):", "7 trường số đo CORE đối soát BTS Part 234 qua TS-018 Option B đạt 10,500/10,500 điểm trùng khớp 100%.", 12, 8)
    add_bullet_item(tf_r, "2. OR-05 (Khoảng trống Tháng 3/2024):", "Năm 2024 khuyết 31 ngày Tháng 3 (335/366 ngày quan sát), ghi nhận source_coverage_status = PARTIAL.", 12, 6)
    add_bullet_item(tf_r, "3. OR-07 (Loại trừ Thời tiết):", "Phân nhánh thời tiết T-015 giữ trạng thái CONDITIONAL_NO_GO, loại trừ hoàn toàn khỏi phân tích CORE.", 12, 6)
    add_bullet_item(tf_r, "4. OR-08 (Nhận dạng nguồn Kaggle):", "Ghi nhận trạng thái IDENTITY_UNVERIFIED / ACCEPTED_NON_BLOCKING đối với tác giả tải lên.", 12, 6)

    s4.notes_slide.notes_text_frame.text = (
        "Chúng tôi đặc biệt nhấn mạnh tính liêm chính học thuật: đề án công khai toàn bộ 4 giới hạn bắt buộc OR-03, "
        "OR-05, OR-07, OR-08. Toàn bộ các kết luận đều dựa trên dữ liệu thật và đối soát độc lập với BTS TranStats."
    )

    # ==========================================
    # SLIDE 5: BIG DATA ARCHITECTURE & PARQUET
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, COLOR_BG_LIGHT)
    add_header(s5, "Kiến Trúc Big Data: Apache Spark & Lưu Trữ Cột Parquet")

    # Architecture Pipeline Diagram
    stages = [
        ("Giai Đoạn 1: Raw Data", "9 tệp CSV hàng năm\n34.5 GB dữ liệu thô\n34 cột nguồn ban đầu"),
        ("Giai Đoạn 2: ETL & Curated", "PySpark Preflight Validation\nContract DC-11/12 (Accepted)\n117 tệp Parquet (3.31 GB)"),
        ("Giai Đoạn 3: CORE KPI", "kpi_run_2016_2024_v1\n6 chiều (57,015 cohorts)\n684,180 dòng KPI xuất bản"),
        ("Giai Đoạn 4: Analytics", "t014_analysis_2016_2024_v4\n12 bảng CSV & Parquet\n16 biểu đồ 300 DPI & 20 RES")
    ]
    for i, (stitle, sdesc) in enumerate(stages):
        x = Inches(0.8 + i * 2.95)
        create_shape(s5, MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(2.75), Inches(3.0), COLOR_CARD_BG, COLOR_BORDER)
        create_shape(s5, MSO_SHAPE.RECTANGLE, x, Inches(1.8), Inches(2.75), Inches(0.08), COLOR_NAVY if i % 2 == 0 else COLOR_BLUE)

        tb = s5.shapes.add_textbox(x + Inches(0.15), Inches(2.0), Inches(2.45), Inches(2.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = stitle
        p0.font.bold = True
        p0.font.size = Pt(13)
        p0.font.color.rgb = COLOR_NAVY

        p1 = tf.add_paragraph()
        p1.text = sdesc
        p1.font.size = Pt(11.5)
        p1.font.color.rgb = COLOR_TEXT_MAIN
        p1.space_before = Pt(8)

    # Bottom Stat Banner: 10.4x Compression
    create_shape(s5, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.1), Inches(11.7), Inches(1.6), COLOR_NAVY)
    tb_b = s5.shapes.add_textbox(Inches(1.1), Inches(5.2), Inches(11.1), Inches(1.4))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    p.text = "HIỆU QUẢ KỸ THUẬT VƯỢT BẬC CỦA ĐỊNH DẠNG CỘT APACHE PARQUET NÉN SNAPPY"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(254, 215, 102)

    p_sub = tf_b.add_paragraph()
    p_sub.text = (
        "• Tỷ lệ nén dữ liệu: Đạt ~10.4 lần (từ 34.5 GB CSV thô xuống đúng 3.31 GB Parquet trên 117 tệp phân tán).\n"
        "• Column Projection & Predicate Pushdown: Tối ưu hóa truy vấn bằng cách chỉ nạp các cột cần thiết cho từng chỉ số và đẩy điều kiện lọc xuống tầng lưu trữ Parquet, giảm thiểu đáng kể chi phí quét đĩa vật lý.\n"
        "• Benchmark CORE KPI (T-013): Bộ tối ưu hóa Catalyst và Tungsten Engine xử lý 8 CORE KPIs trên 54.7M dòng trong 510.7 giây (thước đo hiệu năng được phê duyệt riêng cho tác vụ T-013 CORE KPI, không đại diện cho toàn bộ thời gian quy trình đầu cuối)."
    )
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = COLOR_WHITE
    p_sub.space_before = Pt(4)

    s5.notes_slide.notes_text_frame.text = (
        "Kiến trúc dữ liệu trải qua 4 giai đoạn chặt chẽ. Định dạng Parquet nén Snappy đạt tỷ lệ nén 10.4 lần, "
        "kết hợp cơ chế chiếu cột (column projection) và đẩy bộ lọc (predicate pushdown) giúp tối ưu hóa truy vấn mà không cần quét toàn bộ tệp thô. "
        "Thời gian 510.7 giây là mốc benchmark hiệu năng được phê duyệt chính thức riêng cho tác vụ tính toán 8 CORE KPIs (T-013), "
        "không đại diện cho tổng thời gian toàn bộ quy trình đầu cuối."
    )

    # ==========================================
    # SLIDE 6: DATA QUALITY & CONTRACT DC-11/12
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, COLOR_BG_LIGHT)
    add_header(s6, "Kiểm Soát Chất Lượng Dữ Liệu & Hợp Đồng Dữ Liệu (DC-11/12)")

    # 3 Pillars
    pillars = [
        ("Accepted (Được Chấp Nhận)", "54,674,003 bản ghi (100%)", "Vượt qua toàn bộ vị từ kiểm tra kiểu dữ liệu, miền giá trị và tính toàn vẹn nghiệp vụ. Toàn bộ các phép tính KPI chỉ thực hiện trên tập accepted."),
        ("Quarantined (Cách Ly)", "0 bản ghi (0.00%)", "Dành cho các bản ghi vi phạm tính toàn vẹn ngữ nghĩa hoặc thiếu khóa nghiệp vụ có thể phục hồi. Không có dòng nào bị cô lập ở cấp 9 năm."),
        ("Rejected (Loại Bỏ)", "0 bản ghi (0.00%)", "Dành cho các bản ghi sai hỏng cấu trúc nghiêm trọng hoặc vi phạm không thể khắc phục. Không có bản ghi nào bị từ chối ở cấp 9 năm.")
    ]
    for i, (ptitle, pstat, pdesc) in enumerate(pillars):
        x = Inches(0.8 + i * 4.0)
        create_shape(s6, MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.7), Inches(3.2), COLOR_CARD_BG, COLOR_BORDER)
        create_shape(s6, MSO_SHAPE.RECTANGLE, x, Inches(1.8), Inches(3.7), Inches(0.08), COLOR_BLUE if i == 0 else COLOR_MUTED)

        tb = s6.shapes.add_textbox(x + Inches(0.2), Inches(2.0), Inches(3.3), Inches(2.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = ptitle
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = COLOR_NAVY

        p1 = tf.add_paragraph()
        p1.text = pstat
        p1.font.bold = True
        p1.font.size = Pt(16)
        p1.font.color.rgb = COLOR_BLUE if i == 0 else COLOR_TEXT_MUTED
        p1.space_before = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = pdesc
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_TEXT_MAIN
        p2.space_before = Pt(8)

    # Invariant Box
    create_shape(s6, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.3), Inches(11.7), Inches(1.5), COLOR_CARD_BG, COLOR_BORDER)
    tb_inv = s6.shapes.add_textbox(Inches(1.1), Inches(5.4), Inches(11.1), Inches(1.3))
    tf_inv = tb_inv.text_frame
    tf_inv.word_wrap = True
    p = tf_inv.paragraphs[0]
    p.text = "BẤT BIẾN BẢO TOÀN SỐ HÀNG & PHÂN LOẠI LOẠI TRỪ LẪN NHAU (DC-11/12)"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_NAVY

    p_sub = tf_inv.add_paragraph()
    p_sub.text = (
        "• Công thức bảo toàn kiểm toán: N_raw = N_accepted + N_quarantined + N_rejected = 54,674,003 dòng.\n"
        "• Khẳng định tính độc lập phân nhánh thời tiết (FP-DEC-017): Bản ghi CORE hợp lệ tuyệt đối không bị cách ly vì thiếu 6 cột thời tiết.\n"
        "• Ghi nhận độ phủ nguồn: VERIFIED_WITH_SCOPE (2016–2023) và PARTIAL (2024 khuyết Tháng 3 theo OR-05)."
    )
    p_sub.font.size = Pt(11.5)
    p_sub.font.color.rgb = COLOR_TEXT_MAIN
    p_sub.space_before = Pt(4)

    s6.notes_slide.notes_text_frame.text = (
        "Hợp đồng dữ liệu DC-11/12 xác lập chuẩn mực kiểm toán khắt khe: Accepted, Quarantined và Rejected hoàn toàn loại trừ lẫn nhau. "
        "Toàn bộ 54.7 triệu bản ghi đều đạt chuẩn accepted."
    )

    # ==========================================
    # SLIDE 7: CORE KPI FRAMEWORK & METHODOLOGY
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, COLOR_BG_LIGHT)
    add_header(s7, "Khung 8 CORE KPI & Các Nguyên Tắc Phương Pháp Luận")

    # Left: 8 KPIs
    create_shape(s7, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_kpi = s7.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.4))
    tf_kpi = tb_kpi.text_frame
    tf_kpi.word_wrap = True
    p = tf_kpi.paragraphs[0]
    p.text = "Danh Mục 8 CORE KPIs (12 Luồng Chỉ Số)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    add_bullet_item(tf_kpi, "• KPI-01:", "Tổng bản ghi accepted N (RQ-01)", 11.5, 6)
    add_bullet_item(tf_kpi, "• KPI-02:", "Tỷ lệ trễ đến ≥15 phút (%) (RQ-02/03/04)", 11.5, 4)
    add_bullet_item(tf_kpi, "• KPI-03:", "Trễ đến trung bình có dấu (phút) (RQ-02/03/04)", 11.5, 4)
    add_bullet_item(tf_kpi, "• KPI-04:", "Tỷ lệ trễ cất cánh ≥15 phút (%) (RQ-02/03/04)", 11.5, 4)
    add_bullet_item(tf_kpi, "• KPI-05:", "Trễ cất cánh trung bình có dấu (phút) (RQ-02/03/04)", 11.5, 4)
    add_bullet_item(tf_kpi, "• KPI-06:", "Phân vị trễ đến P50 & P90 (phút) (RQ-02/03/04)", 11.5, 4)
    add_bullet_item(tf_kpi, "• KPI-07:", "Taxi-Out TB & Taxi-In TB (2 submetrics) (RQ-05)", 11.5, 4)
    add_bullet_item(tf_kpi, "• KPI-08:", "Air Time, Actual & CRS Elapsed TB (3 submetrics) (RQ-05)", 11.5, 4)

    # Right: 4 Methodological Rules
    create_shape(s7, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_rules = s7.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.4))
    tf_rules = tb_rules.text_frame
    tf_rules.word_wrap = True
    p = tf_rules.paragraphs[0]
    p.text = "4 Nguyên Tắc Phương Pháp Luận Chặt Chẽ"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE

    add_bullet_item(tf_rules, "1. Mẫu số hợp lệ riêng (N_valid):", "Mỗi KPI/submetric tính trên tập bản ghi có giá trị hữu hạn của riêng trường đó. Không quy đồng mẫu số thô.", 11, 7)
    add_bullet_item(tf_rules, "2. Gộp theo trọng số mẫu (Weighted Pooling):", "Tỷ lệ gộp nhiều năm: P_pooled = [Tổng (P_y * N_valid,y)] / [Tổng N_valid,y]. Cấm lấy trung bình cộng giản đơn các tỷ lệ.", 11, 5)
    add_bullet_item(tf_rules, "3. Phân tầng cỡ mẫu (FP-DEC-016):", "So sánh N_valid riêng của từng chỉ số với N_min (Hãng: 1,000; Sân bay: 365; Tuyến có hướng: 100/năm). 3 cấp độ: SUPPRESSED (N_valid < N_min), LOW_SAMPLE_CAUTION (N_min ≤ N_valid < 3*N_min), SUFFICIENT (N_valid ≥ 3*N_min).", 10.5, 5)
    add_bullet_item(tf_rules, "4. Cấm gộp phân vị (Percentile Prohibition):", "P50, P90 tính bằng GK-sketch xấp xỉ; tuyệt đối không lấy trung bình phân vị giữa các năm do tính phi tuyến.", 11, 5)

    s7.notes_slide.notes_text_frame.text = (
        "Khung 8 CORE KPIs tuân thủ nghiêm ngặt quy tắc mẫu số hợp lệ riêng N_valid cho từng chỉ số và quyết định FP-DEC-016: "
        "phân loại độ tin cậy mẫu theo 3 cấp độ (SUPPRESSED khi N_valid < N_min, LOW_SAMPLE_CAUTION khi N_min <= N_valid < 3*N_min, "
        "và SUFFICIENT khi N_valid >= 3*N_min) dựa trên ngưỡng tối thiểu đã duyệt: 1,000 (hãng-năm), 365 (sân bay-năm), 100 (tuyến có hướng-năm). "
        "Đồng thời, áp dụng gộp tỷ lệ theo trọng số mẫu và tuyệt đối cấm gộp các phân vị giữa các cohort."
    )

    # ==========================================
    # SLIDE 8: RQ-01 RESULTS (Volume & Seasonality)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, COLOR_BG_LIGHT)
    add_header(s8, "RQ-01: Quy Mô Sản Lượng 9 Năm & Tính Quy Luật Mùa Vụ")

    # Embedded Image Left
    img_rq1 = CHARTS_DIR / "CHART_RQ01_01_annual_accepted_volume.png"
    if img_rq1.exists():
        s8.shapes.add_picture(str(img_rq1), Inches(0.8), Inches(1.8), width=Inches(6.4))

    # Right: Stat Cards & Bullet Findings
    create_shape(s8, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.8), Inches(5.0), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_rq1 = s8.shapes.add_textbox(Inches(7.7), Inches(2.0), Inches(4.6), Inches(4.4))
    tf_rq1 = tb_rq1.text_frame
    tf_rq1.word_wrap = True
    p = tf_rq1.paragraphs[0]
    p.text = "Phát Hiện Định Lượng Chính (RQ-01)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    add_bullet_item(tf_rq1, "• Tăng trưởng tiền đại dịch:", "5.54M chuyến (2016) tăng lên đỉnh 7.16M chuyến (2019, +2.5% YoY, chiếm 13.10% 9 năm) [RES-001].", 12, 8)
    add_bullet_item(tf_rq1, "• Cú sốc đáy năm 2020:", "Sụt giảm nghiêm trọng -39.79% xuống còn 4,312,091 chuyến bay do đại dịch [RES-001].", 12, 6)
    add_bullet_item(tf_rq1, "• Quá trình phục hồi:", "Đạt 5.76M (2021) và phục hồi vững chắc đạt 6,645,461 chuyến vào năm 2023 [RES-001].", 12, 6)
    add_bullet_item(tf_rq1, "• Mùa vụ Tháng 7 đỉnh cao:", "Trong đúng 6/9 năm, đỉnh sản lượng rơi vào Tháng 7 (>600K chuyến/tháng) [RES-002].", 12, 6)
    add_bullet_item(tf_rq1, "• Đáy Tháng 2 & Đáy Tháng 5/2020:", "Tháng 2 có lượng chuyến thấp nhất (8/9 năm). Riêng 2020, đáy rơi vào Tháng 5 với 163,767 chuyến [RES-003].", 12, 6)
    add_bullet_item(tf_rq1, "• Giới hạn năm 2024 PARTIAL:", "Năm 2024 đạt 6,284,841 chuyến trên 11 tháng quan sát (khuyết Tháng 3 theo OR-05) [RES-020].", 12, 6)

    s8.notes_slide.notes_text_frame.text = (
        "Kết quả RQ-01: Sản lượng đạt đỉnh năm 2019 với 7.16 triệu chuyến, sau đó giảm gần 40% trong năm 2020. "
        "Tính mùa vụ rất rõ rệt với đỉnh tháng 7 và đáy tháng 2. Lưu ý năm 2024 chỉ quan sát 11 tháng theo OR-05."
    )

    # ==========================================
    # SLIDE 9: RQ-02 RESULTS (Delay & Long Tail)
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, COLOR_BG_LIGHT)
    add_header(s9, "RQ-02: Phân Bố Thời Gian Trễ & Hiện Tượng Đuôi Dài Lệch Phải")

    # Embedded Image Left
    img_rq2 = CHARTS_DIR / "CHART_RQ02_03_arrival_delay_percentiles_p50_p90.png"
    if img_rq2.exists():
        s9.shapes.add_picture(str(img_rq2), Inches(0.8), Inches(1.8), width=Inches(6.4))

    # Right: Findings
    create_shape(s9, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.8), Inches(5.0), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_rq2 = s9.shapes.add_textbox(Inches(7.7), Inches(2.0), Inches(4.6), Inches(4.4))
    tf_rq2 = tb_rq2.text_frame
    tf_rq2.word_wrap = True
    p = tf_rq2.paragraphs[0]
    p.text = "Phát Hiện Định Lượng Chính (RQ-02)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    add_bullet_item(tf_rq2, "• Tỷ lệ trễ đến biến động:", "Đạt đáy 9.73% (2020), tăng vọt lên đỉnh 20.99% (2022) và 20.81% (2024) [RES-004].", 12, 8)
    add_bullet_item(tf_rq2, "• Trễ trung bình có dấu âm duy nhất 2020:", "Năm 2020 đạt -5.11 phút (hạ cánh sớm hơn lịch), các năm khác dương (+3.5 đến +7.1 phút) [RES-005].", 12, 6)
    add_bullet_item(tf_rq2, "• Trung vị P50 luôn ở mức âm:", "P50 dao động trong khoảng [-11.0, -5.0] phút qua cả 9 năm. Hơn 50% chuyến bay đến sớm! [RES-006].", 12, 6)
    add_bullet_item(tf_rq2, "• Phân vị P90 kéo dãn:", "P90 đạt +42.0m (2022) và +43.0m (2024); khoảng cách P90-P50 dao động 25–49 phút (38–49 phút các năm bình thường, 25 phút năm 2020) [RES-007].", 12, 6)
    add_bullet_item(tf_rq2, "• Nghịch lý phân phối lệch phải:", "Do 10–20% chuyến bay trễ rất nặng kéo lệch giá trị trung bình lên mức dương, trái ngược với trung vị P50 âm của đa số hành khách.", 12, 6)

    s9.notes_slide.notes_text_frame.text = (
        "Kết quả RQ-02 chỉ ra một nghịch lý thống kê quan trọng: Hơn 50% chuyến bay thực tế hạ cánh sớm (P50 từ -5 đến -11 phút), "
        "nhưng giá trị trung bình lại dương (+3.5 đến +7.1 phút) do bị 10-20% chuyến bay trễ nặng kéo dãn đuôi phải (khoảng cách P90-P50 từ 25 đến 49 phút)."
    )

    # ==========================================
    # SLIDE 10: RQ-03 RESULTS (Airlines)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, COLOR_BG_LIGHT)
    add_header(s10, "RQ-03: So Sánh Hiệu Suất Các Hãng Hàng Không Chủ Lực")

    # Embedded Image Left
    img_rq3_1 = CHARTS_DIR / "CHART_RQ03_01_top_carriers_on_time_performance.png"
    if img_rq3_1.exists():
        s10.shapes.add_picture(str(img_rq3_1), Inches(0.8), Inches(1.8), width=Inches(6.4))

    # Right: Carrier Comparison Card
    create_shape(s10, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.8), Inches(5.0), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_c = s10.shapes.add_textbox(Inches(7.7), Inches(2.0), Inches(4.6), Inches(4.4))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = "Phân Hóa Hiệu Suất Hãng Bay (RQ-03)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    add_bullet_item(tf_c, "• Southwest Airlines (WN):", "Sản lượng lớn nhất 11,133,643 chuyến (20.36% thị phần), tỷ lệ đúng giờ gộp 80.67%, Taxi-Out thấp nhất (12.46 phút) [RES-008].", 12, 8)
    add_bullet_item(tf_c, "• Delta Air Lines (DL):", "Hiệu suất đúng giờ hàng đầu trong nhóm lớn với 85.81%, trễ đến TB chỉ +0.66 phút trên 7,821,658 chuyến [RES-009].", 12, 6)
    add_bullet_item(tf_c, "• American Airlines (AA):", "Sản lượng 7,518,473 chuyến, đúng giờ 79.61%, trễ đến TB +7.00 phút [RES-009].", 12, 6)
    add_bullet_item(tf_c, "• United Airlines (UA):", "Sản lượng 5,083,571 chuyến, đúng giờ 81.35%, trễ đến TB +4.35 phút.", 12, 6)
    add_bullet_item(tf_c, "• JetBlue Airways (B6):", "Đúng giờ thấp nhất nhóm lớn với 73.61% (trễ đến 26.39%), trễ đến TB lên tới +11.34 phút do mạng lưới tập trung vùng Đông Bắc.", 12, 6)

    s10.notes_slide.notes_text_frame.text = (
        "Ở câu hỏi RQ-03, Southwest dẫn đầu về sản lượng với hơn 11.1 triệu chuyến bay và thời gian lăn bánh ngắn nhờ mô hình điểm-điểm. "
        "Trong khi đó, Delta Air Lines dẫn đầu về tỷ lệ đúng giờ với 85.81% và trễ trung bình chỉ 0.66 phút."
    )

    # ==========================================
    # SLIDE 11: RQ-03 RESULTS (Hubs & Route Asymmetry)
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, COLOR_BG_LIGHT)
    add_header(s11, "RQ-03 (tiếp): Điểm Nghẽn Sân Bay & Bất Đối Xứng Chặng Bay")

    # Embedded Image Left
    img_rq3_4 = CHARTS_DIR / "CHART_RQ03_04_directed_route_delay_asymmetry.png"
    if img_rq3_4.exists():
        s11.shapes.add_picture(str(img_rq3_4), Inches(0.8), Inches(1.8), width=Inches(6.4))

    # Right: Findings
    create_shape(s11, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.8), Inches(5.0), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_h = s11.shapes.add_textbox(Inches(7.7), Inches(2.0), Inches(4.6), Inches(4.4))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True
    p = tf_h.paragraphs[0]
    p.text = "Điểm Nghẽn & Bất Đối Xứng (RQ-03)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    add_bullet_item(tf_h, "• Siêu điểm nghẽn EWR (Newark):", "Năm 2022 ghi nhận tỷ lệ trễ cất cánh lên tới 27.67% trên quy mô N = 123,277 chuyến (đạt SUFFICIENT) [RES-010].", 12, 8)
    add_bullet_item(tf_h, "• Các Hub áp lực cao khác:", "Chicago O'Hare (ORD) năm 2024 trễ cất cánh 22.48% (N = 251,485); LaGuardia (LGA) năm 2019 trễ cất cánh 22.63% (N = 166,283) [RES-010].", 12, 6)
    add_bullet_item(tf_h, "• Bất đối xứng cặp ORD <-> LGA (2019):", "Chiều ORD->LGA trễ 31.42% so với LGA->ORD trễ 28.60% (chênh lệch 2.82 điểm %, N = 28,277 chuyến) [RES-011].", 12, 6)
    add_bullet_item(tf_h, "• Bất đối xứng cặp LAX <-> SFO (2019):", "Chiều LAX->SFO trễ 24.33% so với SFO->LAX trễ 21.87% (chênh lệch 2.46 điểm %, N = 28,174 chuyến) [RES-011].", 12, 6)
    add_bullet_item(tf_h, "• Ý nghĩa vận hành:", "Chứng minh độ trễ chịu sự chi phối áp đảo bởi tình trạng tắc nghẽn và thời tiết tại sân bay đến hơn là sân bay xuất phát.", 12, 6)

    s11.notes_slide.notes_text_frame.text = (
        "Chúng tôi phát hiện hiện tượng bất đối xứng vận hành rất rõ rệt trên các cặp chặng bay hai chiều: chiều bay về các sân bay "
        "tắc nghẽn như LaGuardia hay San Francisco luôn có tỷ lệ trễ cao hơn từ 2.46% đến 2.82% so với chiều ngược lại."
    )

    # ==========================================
    # SLIDE 12: RQ-04 RESULTS (Pandemic & Re-congestion)
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, COLOR_BG_LIGHT)
    add_header(s12, "RQ-04: Cú Sốc Đại Dịch 2020 & Tái Tắc Nghẽn Hậu Phục Hồi")

    # Embedded Image Left
    img_rq4 = CHARTS_DIR / "CHART_RQ04_01_pandemic_period_kpi_comparison.png"
    if img_rq4.exists():
        s12.shapes.add_picture(str(img_rq4), Inches(0.8), Inches(1.8), width=Inches(6.4))

    # Right: Findings
    create_shape(s12, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.8), Inches(5.0), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_p = s12.shapes.add_textbox(Inches(7.7), Inches(2.0), Inches(4.6), Inches(4.4))
    tf_p = tb_p.text_frame
    tf_p.word_wrap = True
    p = tf_p.paragraphs[0]
    p.text = "Phát Hiện Định Lượng Chính (RQ-04)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    add_bullet_item(tf_p, "• Cú sốc đại dịch năm 2020:", "Sản lượng giảm 39.79% xuống 4.31M chuyến, tỷ lệ trễ đến giảm một nửa xuống 9.73% [RES-012].", 12, 8)
    add_bullet_item(tf_p, "• Kỷ lục đúng giờ Tháng 4/2020:", "Tỷ lệ đúng giờ đạt đỉnh lịch sử 95.15% (tỷ lệ trễ chỉ 4.85%) trên 179,835 chuyến bay [RES-013].", 12, 6)
    add_bullet_item(tf_p, "• Hiện tượng tái tắc nghẽn (2022–2024):", "Khi sản lượng phục hồi lên 6.41M (2022) và 6.65M (2023), tỷ lệ trễ đến tăng vọt lên 20.99% (2022), 20.54% (2023) và 20.81% (2024) [RES-014].", 12, 6)
    add_bullet_item(tf_p, "• Trễ vượt mức tiền đại dịch:", "Tỷ lệ trễ giai đoạn 2022–2024 vượt qua cả mức năm 2019 (19.11%), phản ánh sự thiếu đồng bộ giữa nhu cầu bay và phục hồi nhân lực/hạ tầng.", 12, 6)
    add_bullet_item(tf_p, "• Khẳng định phi nhân quả:", "Trình bày như hiện tượng đồng biến động thực nghiệm; không suy diễn nhân quả đơn lẻ.", 12, 6)

    s12.notes_slide.notes_text_frame.text = (
        "RQ-04 làm rõ tác động của đại dịch: năm 2020 hiệu suất đúng giờ tăng vọt (tháng 4 đạt 95.15% đúng giờ), nhưng khi nhu cầu phục hồi, "
        "tỷ lệ trễ đã tăng vọt lên 20.99% vào năm 2022, vượt qua cả mức trước dịch. Đây là minh chứng rõ nét cho hiện tượng tái tắc nghẽn."
    )

    # ==========================================
    # SLIDE 13: RQ-05 RESULTS (Taxi & Buffer)
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, COLOR_BG_LIGHT)
    add_header(s13, "RQ-05: Động Học Lăn Bánh Mặt Đất & Biên Đệm Lịch Trình")

    # Embedded Image Left
    img_rq5 = CHARTS_DIR / "CHART_RQ05_02_elapsed_time_and_schedule_buffer.png"
    if img_rq5.exists():
        s13.shapes.add_picture(str(img_rq5), Inches(0.8), Inches(1.8), width=Inches(6.4))

    # Right: Findings
    create_shape(s13, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.8), Inches(5.0), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_t = s13.shapes.add_textbox(Inches(7.7), Inches(2.0), Inches(4.6), Inches(4.4))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    p = tf_t.paragraphs[0]
    p.text = "Phát Hiện Định Lượng Chính (RQ-05)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    add_bullet_item(tf_t, "• Taxi-Out biến động mạnh:", "Bình quân toàn quốc từ 15.25 phút (2020) lên 17.95 phút (2024) [RES-015]. Taxi-In ổn định từ 6.82 đến 8.37 phút [RES-016].", 12, 8)
    add_bullet_item(tf_t, "• Siêu tắc nghẽn tại JFK & EWR:", "Sân bay JFK dẫn đầu với Taxi-Out TB lên tới 26.21 phút (N = 129,620) [RES-017]; EWR 23.76m, LGA 23.58m, ORD 22.45m.", 12, 6)
    add_bullet_item(tf_t, "• Đệm lịch trình luôn dương:", "Chênh lệch giữa 2 giá trị TB cận biên (CRS - Actual Elapsed) luôn dương qua cả 9 năm (+4.87 đến +7.08 phút) [RES-018].", 12, 6)
    add_bullet_item(tf_t, "• Phân rã hành trình bay (2016):", "Actual Elapsed TB đạt 140.16m; tỷ lệ giữa các giá trị TB cận biên: Air Time ~83.14%, Taxi-Out ~11.55%, Taxi-In ~5.31% [RES-019].", 12, 6)

    s13.notes_slide.notes_text_frame.text = (
        "Kết quả RQ-05 cho thấy thời gian lăn bánh trên mặt đất đóng góp đáng kể: tại JFK hành khách mất trung bình 26.2 phút chỉ để lăn ra cất cánh. "
        "Chênh lệch giữa hai giá trị trung bình cận biên công bố (CRS và Actual Elapsed Time) luôn dương từ 4.87 đến 7.08 phút; đây là so sánh mô tả giữa các giá trị trung bình, không suy diễn nhân quả hay ý đồ chủ quan của hãng bay."
    )

    # ==========================================
    # SLIDE 14: TECHNICAL PERFORMANCE & AUDIT
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14, COLOR_BG_LIGHT)
    add_header(s14, "Hiệu Năng Big Data & Kết Quả Kiểm Thử Độc Lập")

    # 4 Performance Metric Cards
    metrics = [
        ("510.7 Giây (~8.5 Phút)", "Thời Gian Xử Lý Toàn Bộ 9 Năm", "Tổng hợp 6 chiều phân tích trên 54.7 triệu bản ghi bằng PySpark Catalyst (T-013)."),
        ("10.4 Lần Nén Lưu Trữ", "Hiệu Quả Định Dạng Cột Parquet", "Giảm không gian đĩa từ 34.5 GB CSV xuống đúng 3.31 GB Parquet nén Snappy."),
        ("PySpark 4.0.1 / Java 21", "Môi Trường Thực Thi Xác Thực", "Vận hành trên nền OpenJDK 21 LTS 64-bit, xử lý an toàn không phát sinh lỗi tràn bộ nhớ (OOM)."),
        ("100% Trùng Khớp BTS", "Kiểm Định TS-018 Option B", "10,500/10,500 điểm kiểm tra đối chiếu trực tiếp dữ liệu BTS Part 234 đạt bitwise match.")
    ]
    for i, (mval, mtitle, mdesc) in enumerate(metrics):
        col = i % 2
        row = i // 2
        x = Inches(0.8 + col * 5.95)
        y = Inches(1.8 + row * 2.5)

        create_shape(s14, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.75), Inches(2.3), COLOR_CARD_BG, COLOR_BORDER)
        create_shape(s14, MSO_SHAPE.RECTANGLE, x, y, Inches(5.75), Inches(0.08), COLOR_NAVY if i % 2 == 0 else COLOR_BLUE)

        tb = s14.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), Inches(5.35), Inches(2.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = mval
        p0.font.bold = True
        p0.font.size = Pt(20)
        p0.font.color.rgb = COLOR_NAVY

        p1 = tf.add_paragraph()
        p1.text = mtitle
        p1.font.bold = True
        p1.font.size = Pt(13)
        p1.font.color.rgb = COLOR_BLUE
        p1.space_before = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = mdesc
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = COLOR_TEXT_MAIN
        p2.space_before = Pt(6)

    s14.notes_slide.notes_text_frame.text = (
        "Hệ thống đạt hiệu năng vượt trội: nén 10.4 lần, xử lý toàn bộ 54.7 triệu dòng trong 510.7 giây, vận hành ổn định trên PySpark 4.0.1 và OpenJDK 21 LTS. "
        "Toàn bộ 29 unit tests phân tích và 91/91 audit checks đều đạt PASS 100%."
    )

    # ==========================================
    # SLIDE 15: METHODOLOGICAL LIMITATIONS
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, COLOR_BG_LIGHT)
    add_header(s15, "Giới Hạn Phương Pháp Luận & Khuyến Nghị Vận Hành")

    # Left: Limitations
    create_shape(s15, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_lim = s15.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.4))
    tf_lim = tb_lim.text_frame
    tf_lim.word_wrap = True
    p = tf_lim.paragraphs[0]
    p.text = "Giới Hạn Nghiên Cứu Khoa Học Bắt Buộc"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    add_bullet_item(tf_lim, "• OR-03:", "Xác thực đơn vị đo trên mẫu phân tầng 10,500 điểm kiểm tra BTS, không suy diễn toàn bộ census.", 11.5, 6)
    add_bullet_item(tf_lim, "• OR-05:", "Năm 2024 khuyết Tháng 3 (335/366 ngày quan sát, PARTIAL); cấm so sánh trực tiếp sản lượng như năm đủ.", 11.5, 4)
    add_bullet_item(tf_lim, "• OR-07:", "Loại trừ dữ liệu thời tiết (T-015 CONDITIONAL_NO_GO); không có biểu đồ thời tiết.", 11.5, 4)
    add_bullet_item(tf_lim, "• OR-08:", "Nguồn Kaggle ghi nhận IDENTITY_UNVERIFIED / ACCEPTED_NON_BLOCKING.", 11.5, 4)
    add_bullet_item(tf_lim, "• Phi nhân quả:", "Dữ liệu quan sát hồi cứu không khẳng định quan hệ nhân quả duy nhất.", 11.5, 4)
    add_bullet_item(tf_lim, "• Thiếu cờ hủy chuyến:", "Schema nguồn không chứa CANCELLED / DIVERTED, không tính KPI-11.", 11.5, 4)

    # Right: Recommendations
    create_shape(s15, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), COLOR_CARD_BG, COLOR_BORDER)
    tb_rec = s15.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.4))
    tf_rec = tb_rec.text_frame
    tf_rec.word_wrap = True
    p = tf_rec.paragraphs[0]
    p.text = "Khuyến Nghị Vận Hành Thực Tiễn"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE

    add_bullet_item(tf_rec, "1. Quản lý luồng mặt đất (FAA & Airports):", "Triển khai Surface Metering tại JFK, EWR, LGA, ORD để cắt giảm thời gian Taxi-Out đang vượt 22–26 phút.", 11.5, 8)
    add_bullet_item(tf_rec, "2. Cân đối slot bay hai chiều:", "Điều chỉnh phân bổ slot trên các tuyến bất đối xứng (ORD-LGA, LAX-SFO) nhằm giảm dồn ứ giờ cao điểm tại sân bay đến.", 11.5, 6)
    add_bullet_item(tf_rec, "3. Cấu trúc thời gian dự kiến (Airlines):", "Nghiên cứu sự phân bổ thời gian lịch trình và thời gian thực tế theo mùa và khung giờ nhằm tối ưu kế hoạch bay.", 11.5, 6)
    add_bullet_item(tf_rec, "4. Quản trị rủi ro đuôi dài (Tail Risk):", "Theo dõi sát phân vị P90 thay vì chỉ theo dõi trễ trung bình để chủ động kích hoạt phương án phục hồi đội bay.", 11.5, 6)

    s15.notes_slide.notes_text_frame.text = (
        "Chúng tôi tóm tắt các giới hạn và đề xuất 4 khuyến nghị vận hành thực tiễn: từ tối ưu hóa quản lý luồng mặt đất tại các siêu hub "
        "đến nghiên cứu cấu trúc thời gian dự kiến và quản trị rủi ro đuôi dài P90."
    )

    # ==========================================
    # SLIDE 16: CONCLUSION & Q&A (Dark Navy)
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16, COLOR_NAVY)

    # Decorative border
    create_shape(s16, MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.5), Inches(0.12), Inches(4.5), COLOR_BLUE)

    tb16 = s16.shapes.add_textbox(Inches(1.5), Inches(1.4), Inches(10.5), Inches(4.6))
    tf16 = tb16.text_frame
    tf16.word_wrap = True

    p = tf16.paragraphs[0]
    p.text = "KẾT LUẬN KHOA HỌC & BÀN GIAO KỸ THUẬT"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE

    p = tf16.add_paragraph()
    p.text = "HOÀN TẤT TOÀN DIỆN NHIỆM VỤ T-016 (GATE G7)"
    p.font.name = "Arial"
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(8)

    p = tf16.add_paragraph()
    p.text = (
        "• Hoàn tất 100% mục tiêu: Xây dựng thành công quy trình Big Data PySpark trên 54.7 triệu bản ghi.\n"
        "• Sản phẩm bàn giao: Báo cáo khoa học (DOCX + MD), Bộ trình chiếu (PPTX), Hướng dẫn tái lập (Guide),\n"
        "  Sổ đăng ký kết quả (20 RES-IDs), 16 biểu đồ khoa học 300 DPI, và Chỉ mục đối chiếu Claim-to-Evidence.\n"
        "• Độ tin cậy & Tái lập: Toàn bộ kiểm thử PASS 100%, bảo toàn bất biến dữ liệu và niêm phong có kiểm soát.\n\n"
        "XIN TRÂN TRỌNG CẢM ƠN THẦY/CÔ VÀ HỘI ĐỒNG!\n"
        "SẴN SÀNG TIẾP NHẬN CÂU HỎI & PHẢN BIỆN (Q&A)"
    )
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_before = Pt(16)

    s16.notes_slide.notes_text_frame.text = (
        "Bài trình bày của nhóm xin được kết thúc tại đây. Nhóm xin trân trọng cảm ơn Thầy/Cô và Hội đồng đã lắng nghe, "
        "và rất mong nhận được các câu hỏi, góp ý từ Hội đồng để hoàn thiện đề án."
    )

    prs.save(str(pptx_path))
    file_size = os.path.getsize(pptx_path)
    print(f"PPTX presentation generated: {pptx_path} ({file_size:,} bytes, 16 slides)")
    return pptx_path

if __name__ == "__main__":
    generate_presentation_pptx()
