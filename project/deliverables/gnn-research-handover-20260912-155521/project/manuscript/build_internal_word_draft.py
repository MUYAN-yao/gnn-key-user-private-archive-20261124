"""Build a non-template internal DOCX draft from the evidence-bounded Markdown.

This builder deliberately leaves frozen figures and result files untouched.
The resulting Word file is an internal review artifact, not a journal-template
submission document.
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript" / "temporal_key_user_identification_internal_draft_r44_mechanisms.docx"
FIGURE_WIDTH = Inches(6.25)
BODY_FONT = "SimSun"
HEADING_FONT = "SimHei"
EN_FONT = "Times New Roman"


def set_run_font(run, name: str, size: float, *, bold: bool = False, color: str = "000000", italic: bool = False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:ascii"), EN_FONT if name != EN_FONT else name)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), EN_FONT if name != EN_FONT else name)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    mar = tc_pr.first_child_found_in("w:tcMar")
    if mar is None:
        mar = OxmlElement("w:tcMar")
        tc_pr.append(mar)
    for side, value in {"top": top, "start": start, "bottom": bottom, "end": end}.items():
        node = mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def shade_cell(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:cantSplit")) is None:
        tr_pr.append(OxmlElement("w:cantSplit"))


def set_table_geometry(table, widths):
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_layout = tbl_pr.first_child_found_in("w:tblLayout")
    if tbl_layout is None:
        tbl_layout = OxmlElement("w:tblLayout")
        tbl_pr.append(tbl_layout)
    tbl_layout.set(qn("w:type"), "fixed")
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            cell.width = Inches(widths[i])
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(round(widths[i] * 1440)))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def normalize_markdown_math(text: str) -> str:
    """Convert the small Markdown-LaTex subset used in this draft to Word-safe text."""
    replacements = {
        r"\lambda": "λ",
        r"\eta": "η",
        r"\sigma": "σ",
        r"\leq": "≤",
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    text = re.sub(r"\\mathbb\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\operatorname\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"^\1", text)
    return text


def clean_inline(text: str) -> str:
    text = text.replace("**", "")
    text = text.replace("`", "")
    text = re.sub(r"\$\$(.*?)\$\$", r"\1", text)
    text = re.sub(r"\$(.*?)\$", r"\1", text)
    text = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", text)
    return normalize_markdown_math(text).strip()


def add_text_paragraph(doc: Document, text: str, *, style: str | None = None, align=None, bold=False, italic=False, size=11, font=BODY_FONT, color="000000", caption=False):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5 if caption else 8)
    p.paragraph_format.line_spacing = 1.333
    if align is not None:
        p.alignment = align
    if caption:
        p.paragraph_format.keep_with_next = False
    run = p.add_run(clean_inline(text))
    set_run_font(run, font, size, bold=bold, italic=italic, color=color)
    return p


def add_heading(doc: Document, level: int, text: str):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(16 if level == 1 else 12)
    p.paragraph_format.space_after = Pt(7 if level == 1 else 5)
    run = p.add_run(clean_inline(text))
    set_run_font(run, HEADING_FONT, 16 if level == 1 else 13, bold=True, color="1F4D78")
    return p


def parse_table(lines: list[str], start: int):
    rows = []
    i = start
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        content = lines[i].strip().strip("|")
        cells = [cell.strip() for cell in content.split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            rows.append([clean_inline(cell) for cell in cells])
        i += 1
    return rows, i


def add_markdown_table(doc: Document, rows: list[list[str]]):
    if not rows:
        return
    cols = len(rows[0])
    table = doc.add_table(rows=0, cols=cols)
    table.style = "Table Grid"
    for r, values in enumerate(rows):
        row = table.add_row()
        prevent_row_split(row)
        cells = row.cells
        for c, text in enumerate(values):
            p = cells[c].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c > 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            set_run_font(run, BODY_FONT, 7.5 if cols >= 7 else 8.5, bold=(r == 0))
            if r == 0:
                shade_cell(cells[c], "E8EEF5")
    if cols == 6:
        widths = [1.0, 0.75, 0.9, 1.0, 1.0, 1.85]
    elif cols == 9:
        widths = [0.75, 0.48, 0.72, 1.05, 1.2, 0.62, 0.58, 0.58, 0.52]
    elif cols == 3:
        widths = [1.55, 2.35, 2.7]
    else:
        widths = [6.5 / cols] * cols
    set_table_geometry(table, widths)
    set_repeat_table_header(table.rows[0])
    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def set_image_alt(inline_shape, description: str):
    doc_pr = inline_shape._inline.docPr
    doc_pr.set("descr", description)
    doc_pr.set("title", description[:120])


def add_markdown(doc: Document, path: Path, *, skip_first_title=False, title_override: str | None = None):
    lines = path.read_text(encoding="utf-8").splitlines()
    if title_override:
        add_heading(doc, 1, title_override)
    i = 0
    in_code = False
    code_lines: list[str] = []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_code:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(8)
                p.paragraph_format.left_indent = Inches(0.2)
                p.paragraph_format.line_spacing = 1.0
                run = p.add_run("\n".join(code_lines))
                set_run_font(run, "Courier New", 8.5)
                in_code, code_lines = False, []
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if not stripped or stripped == "---":
            i += 1
            continue
        if stripped.startswith("|"):
            rows, i = parse_table(lines, i)
            add_markdown_table(doc, rows)
            continue
        image = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
        if image:
            image_path = (path.parent / image.group(2)).resolve()
            if image_path.exists():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(5)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.keep_with_next = True
                inline = p.add_run().add_picture(str(image_path), width=FIGURE_WIDTH)
                set_image_alt(inline, image.group(1))
            else:
                add_text_paragraph(doc, f"[Missing figure: {image.group(1)}]", italic=True, color="9B1C1C")
            i += 1
            continue
        if stripped.startswith("# "):
            if not skip_first_title:
                add_heading(doc, 1, stripped[2:])
            skip_first_title = False
        elif stripped.startswith("## "):
            add_heading(doc, 1, stripped[3:])
        elif stripped.startswith("### "):
            add_heading(doc, 2, stripped[4:])
        elif stripped.startswith("$$"):
            equation = stripped.strip("$").strip()
            add_text_paragraph(doc, equation, align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, font=EN_FONT, size=11)
        elif re.match(r"^\d+\. ", stripped):
            p = doc.add_paragraph(style="List Number")
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.333
            run = p.add_run(re.sub(r"^\d+\. ", "", clean_inline(stripped)))
            set_run_font(run, BODY_FONT, 11)
        elif stripped.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.333
            run = p.add_run(clean_inline(stripped[2:]))
            set_run_font(run, BODY_FONT, 11)
        else:
            is_caption = stripped.startswith("图 ") or stripped.startswith("表 ")
            add_text_paragraph(
                doc,
                stripped,
                align=WD_ALIGN_PARAGRAPH.CENTER if is_caption else WD_ALIGN_PARAGRAPH.JUSTIFY,
                size=9 if is_caption else 11,
                caption=is_caption,
            )
        i += 1


def configure_document(doc: Document):
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.line_spacing = 1.333

    for level, size, before, after in [(1, 16, 16, 7), (2, 13, 12, 5)]:
        style = doc.styles[f"Heading {level}"]
        style.font.name = HEADING_FONT
        style._element.rPr.rFonts.set(qn("w:eastAsia"), HEADING_FONT)
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(31, 77, 120)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run("Internal working draft")
    set_run_font(run, EN_FONT, 8, color="666666", italic=True)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Evidence-bounded manuscript draft | Not a journal-template submission")
    set_run_font(run, EN_FONT, 8, color="666666")


def build():
    doc = Document()
    configure_document(doc)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(8)
    run = title.add_run("面向时间不确定性与跨社区约束的关键用户识别")
    set_run_font(run, HEADING_FONT, 22, bold=True)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(18)
    run = subtitle.add_run("Key User Identification under Temporal Uncertainty and Cross-Community Constraints")
    set_run_font(run, EN_FONT, 13, italic=True, color="1F4D78")

    add_markdown(doc, ROOT / "manuscript" / "draft_zh_v0_1.md", skip_first_title=True)

    doc.add_page_break()
    add_heading(doc, 1, "English Title, Abstract, and Keywords")
    en = (ROOT / "manuscript" / "abstract_en_v0_1.md").read_text(encoding="utf-8").split("## Translation Boundary")[0]
    for block in en.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("# "):
            add_text_paragraph(doc, block[2:], align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=15, font=EN_FONT)
        elif block.startswith("## "):
            p = doc.add_paragraph(style="Heading 2")
            p.paragraph_format.keep_with_next = True
            run = p.add_run(block[3:])
            set_run_font(run, EN_FONT, 13, bold=True, color="1F4D78")
        else:
            add_text_paragraph(doc, block.replace("\n", " "), align=WD_ALIGN_PARAGRAPH.JUSTIFY, font=EN_FONT)

    doc.core_properties.title = "面向时间不确定性与跨社区约束的关键用户识别"
    doc.core_properties.subject = "Internal evidence-bounded manuscript draft"
    doc.core_properties.author = ""
    doc.core_properties.comments = "Not an official journal template."
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
