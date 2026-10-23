# -*- coding: utf-8 -*-
"""
tools/export/build_report_docx.py
Full-fidelity academic report DOCX generator for T-016.
Converts the authoritative T016_FINAL_ACADEMIC_REPORT.md into a beautifully styled
Microsoft Word document (.docx) containing 100% of the report sections, all 80 headings,
7 formatted multi-column data tables, 2 callout boxes, 15 embedded 300 DPI figures, and appendices.
"""

import os
import sys
import re
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

OUTPUT_DIR = Path(r"D:\Flight_Audit_Exports\G7_T016_FINAL_DELIVERABLES")
CORRECTED_OUTPUT_DIR = OUTPUT_DIR / "corrected"
ANALYTICS_DIR = BASE_DIR / "data" / "analytics" / "runs" / "t014_analysis_2016_2024_v4"
CHARTS_DIR = ANALYTICS_DIR / "charts"

# Brand Color Palette
COLOR_NAVY = RGBColor(26, 54, 93)       # #1A365D Main Navy
COLOR_SLATE = RGBColor(45, 55, 72)      # #2D3748 Header Slate
COLOR_BLUE = RGBColor(49, 130, 206)     # #3182CE Accent Blue
COLOR_BODY = RGBColor(45, 55, 72)       # Text Body
COLOR_MUTED = RGBColor(113, 128, 150)   # Captions / Secondary
COLOR_CODE = RGBColor(155, 44, 44)      # Dark Red for inline code

HEX_NAVY = "1A365D"
HEX_LIGHT_BG = "F7FAFC"
HEX_ALT_ROW = "F8FAFC"
HEX_BORDER = "CBD5E0"
HEX_MUTED = "718096"

def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_borders(cell, top="CBD5E0", bottom="CBD5E0", left="CBD5E0", right="CBD5E0", sz="4"):
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="{"single" if top else "none"}" w:sz="{sz}" w:space="0" w:color="{top or "auto"}"/>'
        f'<w:bottom w:val="{"single" if bottom else "none"}" w:sz="{sz}" w:space="0" w:color="{bottom or "auto"}"/>'
        f'<w:left w:val="{"single" if left else "none"}" w:sz="{sz}" w:space="0" w:color="{left or "auto"}"/>'
        f'<w:right w:val="{"single" if right else "none"}" w:sz="{sz}" w:space="0" w:color="{right or "auto"}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_formatted_runs(paragraph, text, default_size=11, default_color=None, default_bold=False, default_italic=False):
    """
    Parses inline Markdown formatting (**bold**, *italic*, `code`) and adds styled runs.
    """
    pattern = re.compile(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)')
    tokens = pattern.split(text)
    for tok in tokens:
        if not tok:
            continue
        bold = default_bold
        italic = default_italic
        code = False
        val = tok
        if tok.startswith('**') and tok.endswith('**') and len(tok) >= 4:
            bold = True
            val = tok[2:-2]
        elif tok.startswith('*') and tok.endswith('*') and len(tok) >= 2:
            italic = True
            val = tok[1:-1]
        elif tok.startswith('`') and tok.endswith('`') and len(tok) >= 2:
            code = True
            val = tok[1:-1]

        run = paragraph.add_run(val)
        run.bold = bold
        run.italic = italic
        if code:
            run.font.name = "Consolas"
            run.font.size = Pt(max(8.5, default_size - 1))
            run.font.color.rgb = COLOR_CODE
        else:
            run.font.name = "Times New Roman"
            run.font.size = Pt(default_size)
            if default_color:
                run.font.color.rgb = default_color
            else:
                run.font.color.rgb = COLOR_BODY

def add_callout_box(doc, text_lines, title="LƯU Ý PHƯƠNG PHÁP LUẬN"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    set_cell_background(cell, HEX_LIGHT_BG)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

    # Thick left border
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="36" w:space="0" w:color="{HEX_NAVY}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_before = Pt(2)
    p0.paragraph_format.space_after = Pt(3)
    p0.paragraph_format.line_spacing = 1.15

    for idx, line in enumerate(text_lines):
        clean_line = line.strip().lstrip('>').strip()
        if not clean_line:
            continue
        if idx == 0:
            p = p0
        else:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15

        add_formatted_runs(p, clean_line, default_size=10.5, default_color=COLOR_BODY)

    # Empty spacer after table
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def render_table_block(doc, table_lines):
    if len(table_lines) < 2:
        return

    # Parse rows
    parsed_rows = []
    alignments = []
    for idx, l in enumerate(table_lines):
        cells = [c.strip() for c in l.strip().split('|')[1:-1]]
        if idx == 1:
            # Alignment row
            for c in cells:
                if c.startswith(':') and c.endswith(':'):
                    alignments.append(WD_ALIGN_PARAGRAPH.CENTER)
                elif c.endswith(':'):
                    alignments.append(WD_ALIGN_PARAGRAPH.RIGHT)
                else:
                    alignments.append(WD_ALIGN_PARAGRAPH.LEFT)
            continue
        parsed_rows.append(cells)

    if not parsed_rows:
        return

    header = parsed_rows[0]
    data_rows = parsed_rows[1:]
    col_count = len(header)
    row_count = len(parsed_rows)

    table = doc.add_table(rows=row_count, cols=col_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Font size based on column count
    font_size = 8.0 if col_count >= 10 else (8.5 if col_count >= 7 else 9.5)
    padding_dxa = 60 if col_count >= 10 else 100

    # Format header
    hdr_cells = table.rows[0].cells
    for col_idx, cell in enumerate(hdr_cells):
        set_cell_background(cell, HEX_NAVY)
        set_cell_margins(cell, top=padding_dxa, bottom=padding_dxa, left=padding_dxa, right=padding_dxa)
        set_cell_borders(cell, top="1A365D", bottom="1A365D", left="1A365D", right="1A365D", sz="6")
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.alignment = alignments[col_idx] if col_idx < len(alignments) else WD_ALIGN_PARAGRAPH.LEFT
        text_val = header[col_idx] if col_idx < len(header) else ""
        add_formatted_runs(p, text_val, default_size=font_size, default_color=RGBColor(255, 255, 255), default_bold=True)

    # Set tblHeader and cantSplit on header row
    trPr = table.rows[0]._element.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    # Format data rows
    for r_idx, d_row in enumerate(data_rows, 1):
        row_cells = table.rows[r_idx].cells
        is_even = (r_idx % 2 == 0)
        bg_hex = HEX_ALT_ROW if is_even else "FFFFFF"

        # cantSplit on data row
        r_trPr = table.rows[r_idx]._element.get_or_add_trPr()
        r_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        for col_idx, cell in enumerate(row_cells):
            set_cell_background(cell, bg_hex)
            set_cell_margins(cell, top=padding_dxa, bottom=padding_dxa, left=padding_dxa, right=padding_dxa)
            set_cell_borders(cell, top="CBD5E0", bottom="CBD5E0", left="CBD5E0", right="CBD5E0", sz="4")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.05
            p.alignment = alignments[col_idx] if col_idx < len(alignments) else WD_ALIGN_PARAGRAPH.LEFT

            text_val = d_row[col_idx] if col_idx < len(d_row) else ""
            add_formatted_runs(p, text_val, default_size=font_size, default_color=COLOR_BODY)

    # Add gentle space after table
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def generate_report_docx(output_dir=None):
    target_dir = Path(output_dir) if output_dir else CORRECTED_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    docx_path = target_dir / "T016_FINAL_ACADEMIC_REPORT.docx"
    md_source_path = target_dir / "T016_FINAL_ACADEMIC_REPORT.md"

    if not md_source_path.exists():
        # Fall back to parent deliverables directory
        md_source_path = OUTPUT_DIR / "T016_FINAL_ACADEMIC_REPORT.md"

    print(f"Reading Markdown source for DOCX generation: {md_source_path}")
    with open(md_source_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    lines = md_text.splitlines()

    # Initialize Document
    doc = docx.Document()

    # Page Margins: 1 inch (72 pt = 1440 dxa)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

        # Header
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("ĐỒ ÁN PHÂN TÍCH HIỆU SUẤT KHAI THÁC CHUYẾN BAY NỘI ĐỊA HOA KỲ GIAI ĐOẠN 2016–2024")
        r_hdr.font.name = "Times New Roman"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.color.rgb = COLOR_MUTED

        # Footer
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ftr = p_ftr.add_run("Trang ")
        r_ftr.font.name = "Times New Roman"
        r_ftr.font.size = Pt(9.0)
        r_ftr.font.color.rgb = COLOR_MUTED
        # Add PAGE field
        fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        p_ftr._p.append(fldSimple)

    # Parsing state machine
    i = 0
    total_lines = len(lines)
    heading_count = 0

    while i < total_lines:
        line = lines[i]
        sline = line.strip()

        # 1. Blank line
        if not sline:
            i += 1
            continue

        # 2. Horizontal divider `---`
        if sline == "---":
            i += 1
            continue

        # 3. Headings (#, ##, ###, ####)
        if sline.startswith('#'):
            heading_count += 1
            hashes, title = sline.split(None, 1)
            level = len(hashes)

            if level == 1:
                # Main Document Title
                h = doc.add_heading(title, level=0)
                h.paragraph_format.space_before = Pt(18)
                h.paragraph_format.space_after = Pt(4)
                h.paragraph_format.keep_with_next = True
                h.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in h.runs:
                    r.bold = True
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(20)
                    r.font.color.rgb = COLOR_NAVY
            elif level == 2:
                if heading_count == 2:
                    # Subtitle under main title
                    h = doc.add_heading(title, level=2)
                    h.paragraph_format.space_before = Pt(0)
                    h.paragraph_format.space_after = Pt(16)
                    h.paragraph_format.keep_with_next = True
                    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in h.runs:
                        r.bold = True
                        r.italic = True
                        r.font.name = "Times New Roman"
                        r.font.size = Pt(13)
                        r.font.color.rgb = COLOR_SLATE
                else:
                    # Chapter / Major Heading (Word Heading 1)
                    h = doc.add_heading(title, level=1)
                    h.paragraph_format.space_before = Pt(18)
                    h.paragraph_format.space_after = Pt(8)
                    h.paragraph_format.keep_with_next = True
                    for run in h.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(15)
                        run.font.bold = True
                        run.font.color.rgb = COLOR_NAVY
            elif level == 3:
                # Section (Word Heading 2)
                h = doc.add_heading(title, level=2)
                h.paragraph_format.space_before = Pt(12)
                h.paragraph_format.space_after = Pt(6)
                h.paragraph_format.keep_with_next = True
                for run in h.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(12.5)
                    run.font.bold = True
                    run.font.color.rgb = COLOR_SLATE
            elif level == 4:
                # Subsection (Word Heading 3)
                h = doc.add_heading(title, level=3)
                h.paragraph_format.space_before = Pt(8)
                h.paragraph_format.space_after = Pt(4)
                h.paragraph_format.keep_with_next = True
                for run in h.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(11.5)
                    run.font.bold = True
                    run.font.color.rgb = COLOR_NAVY
            i += 1
            continue

        # 4. Blockquotes / Callout boxes (`> ...`)
        if sline.startswith('>'):
            callout_lines = []
            while i < total_lines and lines[i].strip().startswith('>'):
                callout_lines.append(lines[i].strip())
                i += 1
            add_callout_box(doc, callout_lines)
            continue

        # 5. Table block (`| ...`)
        if sline.startswith('|'):
            table_lines = []
            while i < total_lines and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            render_table_block(doc, table_lines)
            continue

        # 6. Embedded Figure (`![Caption](path)`)
        if sline.startswith('![') and '](' in sline:
            match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', sline)
            if match:
                caption = match.group(1)
                img_path_str = match.group(2)
                filename = img_path_str.split('/')[-1]
                full_img_path = CHARTS_DIR / filename

                if full_img_path.exists():
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(10)
                    p_img.paragraph_format.space_after = Pt(2)
                    p_img.paragraph_format.keep_with_next = True
                    run_img = p_img.add_run()
                    run_img.add_picture(str(full_img_path), width=Inches(6.2))

                    # Check next line for caption note `*Hình X.Y: ...*`
                    if i + 1 < total_lines and lines[i + 1].strip().startswith('*') and lines[i + 1].strip().endswith('*'):
                        caption_text = lines[i + 1].strip()[1:-1]
                        p_cap = doc.add_paragraph()
                        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_cap.paragraph_format.space_before = Pt(2)
                        p_cap.paragraph_format.space_after = Pt(10)
                        r_cap = p_cap.add_run(caption_text)
                        r_cap.font.name = "Times New Roman"
                        r_cap.font.size = Pt(9.5)
                        r_cap.italic = True
                        r_cap.font.color.rgb = COLOR_MUTED
                        i += 1  # consume caption line
                else:
                    # Missing image placeholder
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    r_ph = p_img.add_run(f"[Hình minh họa: {caption} — Tệp nguồn: {filename}]")
                    r_ph.font.name = "Times New Roman"
                    r_ph.italic = True
                    r_ph.font.color.rgb = COLOR_MUTED
            i += 1
            continue

        # 7. Math Equation (`$$...$$`)
        if sline.startswith('$$') and sline.endswith('$$'):
            eq_text = sline[2:-2].strip()
            p_eq = doc.add_paragraph()
            p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_eq.paragraph_format.space_before = Pt(6)
            p_eq.paragraph_format.space_after = Pt(6)
            r_eq = p_eq.add_run(eq_text)
            r_eq.font.name = "Times New Roman"
            r_eq.font.size = Pt(11)
            r_eq.italic = True
            r_eq.font.color.rgb = COLOR_NAVY
            i += 1
            continue

        # 8. Fenced Code Block (``` ... ```)
        if sline.startswith('```'):
            code_lines = []
            i += 1
            while i < total_lines and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1 # consume closing ```

            # Render code box
            table = doc.add_table(rows=1, cols=1)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = False
            table.columns[0].width = Inches(6.5)
            cell = table.cell(0, 0)
            set_cell_background(cell, HEX_LIGHT_BG)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            set_cell_borders(cell, top="CBD5E0", bottom="CBD5E0", left="1A365D", right="CBD5E0", sz="4")
            
            p_code = cell.paragraphs[0]
            p_code.paragraph_format.space_before = Pt(2)
            p_code.paragraph_format.space_after = Pt(2)
            p_code.paragraph_format.line_spacing = 1.05
            r_code = p_code.add_run("\n".join(code_lines))
            r_code.font.name = "Consolas"
            r_code.font.size = Pt(8.5)
            r_code.font.color.rgb = COLOR_SLATE

            p_sp = doc.add_paragraph()
            p_sp.paragraph_format.space_before = Pt(0)
            p_sp.paragraph_format.space_after = Pt(4)
            continue

        # 9. Bullet point (`- ` or `* `)
        if sline.startswith('- ') or sline.startswith('* '):
            is_nested = line.startswith('  ') or line.startswith('\t')
            bullet_text = sline[2:].strip()

            p_b = doc.add_paragraph()
            p_b.paragraph_format.left_indent = Inches(0.5 if is_nested else 0.25)
            p_b.paragraph_format.space_before = Pt(1)
            p_b.paragraph_format.space_after = Pt(2.5)
            p_b.paragraph_format.line_spacing = 1.15

            r_bullet = p_b.add_run("• " if not is_nested else "– ")
            r_bullet.bold = True
            r_bullet.font.name = "Times New Roman"
            r_bullet.font.size = Pt(11)
            r_bullet.font.color.rgb = COLOR_NAVY if not is_nested else COLOR_SLATE

            add_formatted_runs(p_b, bullet_text, default_size=11, default_color=COLOR_BODY)
            i += 1
            continue

        # 10. Numbered List item (`1. ...`, `2. ...`)
        num_match = re.match(r'^\s*(\d+)\.\s+(.*)', sline)
        if num_match:
            num_str = num_match.group(1)
            item_text = num_match.group(2)

            p_n = doc.add_paragraph()
            p_n.paragraph_format.left_indent = Inches(0.25)
            p_n.paragraph_format.space_before = Pt(1.5)
            p_n.paragraph_format.space_after = Pt(2.5)
            p_n.paragraph_format.line_spacing = 1.15

            r_num = p_n.add_run(f"{num_str}. ")
            r_num.bold = True
            r_num.font.name = "Times New Roman"
            r_num.font.size = Pt(11)
            r_num.font.color.rgb = COLOR_NAVY

            add_formatted_runs(p_n, item_text, default_size=11, default_color=COLOR_BODY)
            i += 1
            continue

        # 11. Regular paragraph
        p_norm = doc.add_paragraph()
        p_norm.paragraph_format.space_before = Pt(2)
        p_norm.paragraph_format.space_after = Pt(6)
        p_norm.paragraph_format.line_spacing = 1.15
        p_norm.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        add_formatted_runs(p_norm, sline, default_size=11, default_color=COLOR_BODY)
        i += 1

    # Save document
    doc.save(docx_path)
    file_size = os.path.getsize(docx_path)
    print(f"DOCX academic report generated: {docx_path} ({file_size:,} bytes, {heading_count} headings processed)")
    return docx_path

if __name__ == "__main__":
    generate_report_docx()
