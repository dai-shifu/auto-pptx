"""Build the synthetic protein daily-report example with the existing pipeline.

Run from the project root: uv run python -m scripts.build_bio_daily
Previews are exported separately from sample-output.pptx in PowerPoint.
"""

import argparse
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

from src.generator import GenerationResult, generate


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "examples/bio-daily"
SHEET_NAME = "日报数据"
WIDTH, HEIGHT = 13.333333, 7.5
FONT = "Microsoft YaHei"
NAVY, TEAL, MINT = "172D38", "287E80", "B8E1D5"
PAPER, WHITE, INK, MUTED = "F6F8F7", "FFFFFF", "203B46", "637680"
PALE, LINE, AMBER = "E7F1EE", "D9E4E0", "E5B975"
HEADERS = (
    "模板", "日期", "项目编号", "项目名称", "负责人", "团队",
    "项目总数", "今日完成", "待关注", "今日摘要", "重点事项",
    "当前阶段", "表达进展", "纯化进展", "浓度", "纯度", "回收量",
    "实验结论", "下一步",
    "风险事项1", "处理安排1", "风险负责人1",
    "风险事项2", "处理安排2", "风险负责人2",
    "次日任务1", "次日负责人1", "次日任务2", "次日负责人2",
    "次日任务3", "次日负责人3",
)
COMMON = {"日期": "2026-11-16", "团队": "蛋白研发组 · 示例"}
ROWS = (
    {**COMMON, "模板": "日报总览", "项目总数": "03", "今日完成": "01",
     "待关注": "01", "今日摘要": "完成 1 项纯化记录复核，推进 2 项表达与纯化任务。",
     "重点事项": "DEMO-002 的回收量需复核；次日优先完成记录核对与补充取样安排。"},
    {**COMMON, "模板": "项目进展", "项目编号": "DEMO-001",
     "项目名称": "重组蛋白 A · 表达与纯化", "负责人": "成员 A",
     "当前阶段": "纯化记录复核", "表达进展": "已完成表达与收集；样本编号核对完成。",
     "纯化进展": "已完成亲和纯化，今日整理洗脱组分与检测记录。",
     "浓度": "1.8 mg/mL", "纯度": "92%", "回收量": "8.6 mg",
     "实验结论": "本次数据已整理，进入项目内部复核。",
     "下一步": "完成复核后，安排下一阶段样本使用。"},
    {**COMMON, "模板": "项目进展", "项目编号": "DEMO-002",
     "项目名称": "融合蛋白 B · 亲和纯化与回收复核", "负责人": "成员 B",
     "当前阶段": "回收结果复核", "表达进展": "表达与收集已完成，原始记录已归档。",
     "纯化进展": "本轮纯化已完成，回收量待复核。",
     "浓度": "0.9 mg/mL", "纯度": "86%", "回收量": "3.2 mg",
     "实验结论": "待核对组分体积与记录。",
     "下一步": "复核洗脱记录与计算过程，形成问题清单。"},
    {**COMMON, "模板": "项目进展", "项目编号": "DEMO-003",
     "项目名称": "重组蛋白 C · 小规模表达评估", "负责人": "成员 C",
     "当前阶段": "表达样本整理", "表达进展": "本轮取样已完成，正在整理样本与记录。",
     "纯化进展": "尚未进入纯化阶段，等待表达结果复核。",
     "浓度": "未测定", "纯度": "未测定", "回收量": "未测定",
     "实验结论": "本轮进度已记录，纯化结果尚未测定。",
     "下一步": "完成表达结果整理，确认是否进入纯化。"},
    {**COMMON, "模板": "风险与计划",
     "风险事项1": "DEMO-002\n回收量待复核",
     "处理安排1": "核对组分体积、编号和计算记录，复核后更新结论。",
     "风险负责人1": "成员 B", "风险事项2": "DEMO-003\n表达结果待整理",
     "处理安排2": "完成样本与原始记录核对，再确认后续纯化安排。",
     "风险负责人2": "成员 C",
     "次日任务1": "完成 DEMO-001 记录复核", "次日负责人1": "成员 A",
     "次日任务2": "复核 DEMO-002 回收结果", "次日负责人2": "成员 B",
     "次日任务3": "整理 DEMO-003 表达结果", "次日负责人3": "成员 C"},
)
MAPPING = {header: header for header in HEADERS[1:]}


def _color(value: str) -> RGBColor:
    return RGBColor.from_string(value)


def _font(run, size: float, color: str, bold: bool = False) -> None:
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = _color(color)
    east_asian = OxmlElement("a:ea")
    east_asian.set("typeface", FONT)
    run._r.get_or_add_rPr().append(east_asian)


def _text(slide, text: str, x: float, y: float, w: float, h: float,
          size: float = 16, color: str = INK, bold: bool = False,
          align=PP_ALIGN.LEFT, name: str = ""):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    shape.name = name or text[:40]
    frame = shape.text_frame
    frame.clear()
    frame.margin_left = frame.margin_right = 0
    frame.margin_top = frame.margin_bottom = 0
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.NONE
    for i, line in enumerate(text.split("\n")):
        paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        paragraph.alignment = align
        paragraph.line_spacing = 1.2
        paragraph.space_after = Pt(2)
        run = paragraph.add_run()
        run.text = line
        _font(run, size, color, bold)
    return shape


def _rect(slide, x: float, y: float, w: float, h: float,
          fill: str, stroke: str | None = None, oval: bool = False):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL if oval else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _color(fill)
    shape._element.spPr.append(OxmlElement("a:effectLst"))
    if stroke:
        shape.line.color.rgb = _color(stroke)
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def _base(prs, template: str, section: str, dark: bool = False):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # Use an actual shape: the generator clones shapes, not slide backgrounds.
    _rect(slide, 0, 0, WIDTH, HEIGHT, NAVY if dark else PAPER)
    _text(slide, "{{tpl::" + template + "}}", -5, -1, 4, .4, 10)
    _text(slide, "BIOPROCESS  /  DAILY REPORT", .65, .4, 7, .25,
          10, MINT if dark else TEAL, True)
    _text(slide, "{{日期}}", 10.1, .4, 2.55, .3, 11,
          MINT if dark else MUTED, align=PP_ALIGN.RIGHT)
    _text(slide, "{{团队}}", .65, 7.02, 6.5, .25, 10,
          MINT if dark else MUTED)
    _text(slide, "虚构示例  /  " + section, 9.0, 7.02, 3.65, .25, 10,
          MINT if dark else MUTED, align=PP_ALIGN.RIGHT)
    return slide


def _table(slide, values, widths, x: float, y: float, row_heights):
    shape = slide.shapes.add_table(
        len(values), len(widths), Inches(x), Inches(y),
        Inches(sum(widths)), Inches(sum(row_heights)),
    )
    shape.name = "可编辑结果表" if len(widths) == 2 else "可编辑风险表"
    table = shape.table
    table.first_row = True
    for c, width in enumerate(widths):
        table.columns[c].width = Inches(width)
    for r, cells in enumerate(values):
        table.rows[r].height = Inches(row_heights[r])
        for c, value in enumerate(cells):
            cell = table.cell(r, c)
            cell.text = value
            cell.margin_left = cell.margin_right = Inches(.18)
            cell.margin_top = cell.margin_bottom = Inches(.1)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = _color(NAVY if r == 0 else WHITE if r % 2 else PALE)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.space_after = Pt(0)
                paragraph.line_spacing = 1.15
                for run in paragraph.runs:
                    _font(run, 14, WHITE if r == 0 else INK, r == 0)
    return table


def build_template(destination: Path) -> Path:
    """Create three fully editable report pages with off-canvas template markers."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(WIDTH), Inches(HEIGHT)
    props = prs.core_properties
    props.title = "蛋白表达与纯化日报 · 示例模板"
    props.subject = "Synthetic daily report; no real experimental data"
    props.author = "auto-pptx"
    props.last_modified_by = "auto-pptx"
    props.created = props.modified = datetime(2026, 11, 16)

    slide = _base(prs, "日报总览", "OVERVIEW", True)
    _text(slide, "表达与纯化\n研发日报", .65, 1.15, 7.5, 1.65, 40, WHITE, True)
    _text(slide, "PROTEIN EXPRESSION & PURIFICATION", .68, 3.0, 8, .35, 12, MINT)
    # Repeated circles evoke sample wells; all are native editable shapes.
    for r in range(3):
        for c in range(3):
            _rect(slide, 10.1 + c * .75, 1.2 + r * .75, .46, .46,
                  TEAL if (r + c) % 3 == 0 else "294650", oval=True)
    for x, label, key in ((.65, "在跟项目", "项目总数"), (3.25, "今日完成", "今日完成"),
                          (5.85, "待关注", "待关注")):
        _rect(slide, x, 3.85, 2.25, 1.35, "24414B")
        _text(slide, label, x + .2, 4.02, 1.85, .3, 12, MINT)
        _text(slide, "{{" + key + "}}", x + .2, 4.42, 1.85, .6, 32, WHITE, True)
    _text(slide, "今日摘要", .65, 5.6, 1.6, .35, 16, MINT, True)
    _text(slide, "{{今日摘要}}", .65, 6.08, 7.25, .65, 17, WHITE)
    _rect(slide, 9.0, 3.85, 3.65, 2.9, "24414B")
    _text(slide, "关注事项", 9.28, 4.1, 3.1, .35, 16, AMBER, True)
    _text(slide, "{{重点事项}}", 9.28, 4.7, 3.1, 1.65, 16, WHITE)

    slide = _base(prs, "项目进展", "PROJECT")
    _text(slide, "{{项目编号}}", .65, 1.0, 3.0, .35, 14, TEAL, True)
    _text(slide, "{{项目名称}}", .65, 1.48, 10.2, .75, 30, INK, True)
    _text(slide, "负责人：{{负责人}}", 10.3, 1.03, 2.35, .35, 12,
          MUTED, align=PP_ALIGN.RIGHT)
    _rect(slide, .65, 2.42, 12, .66, PALE)
    _text(slide, "当前阶段", .87, 2.59, 1.2, .3, 12, TEAL, True)
    _text(slide, "{{当前阶段}}", 2.22, 2.55, 9.9, .4, 16, INK, True)
    _text(slide, "01  表达进展", .65, 3.43, 4.3, .35, 16, TEAL, True)
    _text(slide, "{{表达进展}}", .65, 3.93, 4.4, .7, 16)
    _text(slide, "02  纯化进展", .65, 4.88, 4.3, .35, 16, TEAL, True)
    _text(slide, "{{纯化进展}}", .65, 5.38, 4.4, .7, 16)
    _table(slide, (("记录指标", "本次结果"), ("浓度", "{{浓度}}"),
                   ("纯度", "{{纯度}}"), ("回收量", "{{回收量}}")),
           (1.35, 2.0), 5.5, 3.43, (.52, .56, .56, .56))
    _text(slide, "{{实验结论}}", 5.5, 5.88, 3.35, .62, 14)
    _rect(slide, 9.3, 3.43, 3.35, 2.95, WHITE, LINE)
    _rect(slide, 10.5, 4.05, .95, .65, PALE, LINE)
    _rect(slide, 10.67, 4.2, .18, .18, TEAL, oval=True)
    _text(slide, "实验图片", 9.6, 5.0, 2.75, .35, 16, MUTED, True,
          align=PP_ALIGN.CENTER)
    _text(slide, "可手动添加，或删除此区域", 9.5, 5.56, 2.95, .55, 11,
          MUTED, align=PP_ALIGN.CENTER)
    _text(slide, "下一步", .65, 6.48, 1.05, .3, 12, TEAL, True)
    _text(slide, "{{下一步}}", 1.85, 6.43, 10.8, .4, 14)

    slide = _base(prs, "风险与计划", "NEXT STEPS")
    _text(slide, "风险与次日计划", .65, 1.03, 11.7, .75, 36, INK, True)
    _text(slide, "将待复核事项落实到具体安排与负责人", .65, 1.97, 11.5, .4, 16, MUTED)
    _text(slide, "待处理事项", .65, 2.8, 7, .4, 20, TEAL, True)
    _table(slide, (("事项", "处理安排", "负责人"),
                   ("{{风险事项1}}", "{{处理安排1}}", "{{风险负责人1}}"),
                   ("{{风险事项2}}", "{{处理安排2}}", "{{风险负责人2}}")),
           (2.0, 3.65, 1.2), .65, 3.42, (.55, 1.18, 1.18))
    _rect(slide, 8.05, 2.8, 4.6, 3.85, NAVY)
    _text(slide, "次日行动", 8.35, 3.08, 3.95, .4, 20, WHITE, True)
    for i, y in enumerate((3.91, 4.76, 5.61), 1):
        _rect(slide, 8.35, y, .38, .38, TEAL, oval=True)
        _text(slide, str(i), 8.35, y + .015, .38, .3, 12, WHITE, True,
              align=PP_ALIGN.CENTER)
        _text(slide, "{{次日任务" + str(i) + "}}", 8.94, y - .03, 3.35, .43, 14, WHITE)
        _text(slide, "{{次日负责人" + str(i) + "}}", 8.94, y + .4, 3.3, .28, 10, MINT)
    prs.save(str(destination))
    return destination


def build_workbook(destination: Path) -> Path:
    """Create the five report rows and a short field guide, without formulas."""
    wb = Workbook()
    wb.properties.creator = wb.properties.lastModifiedBy = "auto-pptx"
    wb.properties.title = "蛋白表达与纯化日报 · 虚构示例"
    wb.properties.created = wb.properties.modified = datetime(2026, 11, 16)
    ws = wb.active
    ws.title = SHEET_NAME
    ws.append(HEADERS)
    for row in ROWS:
        ws.append([row.get(header, "") for header in HEADERS])
    ws.freeze_panes = "F2"
    ws.auto_filter.ref = ws.dimensions
    ws.sheet_view.zoomScale = 85
    for i, header in enumerate(HEADERS, 1):
        ws.column_dimensions[get_column_letter(i)].width = (
            44 if any(word in header for word in ("摘要", "进展", "安排", "事项", "结论", "下一步", "任务"))
            else 32 if header == "项目名称" else 18
        )
    for row in ws:
        for cell in row:
            cell.font = Font(name=FONT, size=11, color=INK)
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            if cell.row == 1:
                cell.font = Font(name=FONT, size=11, color=WHITE, bold=True)
                cell.fill = PatternFill("solid", fgColor=NAVY)
            elif cell.row % 2 == 0:
                cell.fill = PatternFill("solid", fgColor=PALE)
        ws.row_dimensions[row[0].row].height = 54 if row[0].row > 1 else 30
    guide = wb.create_sheet("填写说明")
    for values in (
        ("用途", "蛋白表达与纯化日报；全部内容为虚构示例，不作实验依据。"),
        ("操作", "选择“日报数据”、标题行 1、模板列“模板”，同名映射，勾选五行。"),
        ("顺序", "日报总览 → 三条项目进展 → 风险与计划；预期生成五页。"),
        ("总览", "项目总数、今日完成与待关注由填写者提供，程序不会跨行统计。"),
        ("字段", "按模板填写对应字段，其余列可留空；未测定指标请明确填“未测定”。"),
        ("长度", "项目名建议不超过 22 字，进展/结论不超过 32 字，下一步不超过 34 字。"),
        ("图片", "在 PowerPoint 中手动添加；保留比例，可删除图片区提示和装饰。"),
        ("检查", "每次生成后检查页数、警告、文字换行与数据准确性。"),
    ):
        guide.append(values)
    guide.column_dimensions["A"].width = 16
    guide.column_dimensions["B"].width = 96
    for row in guide:
        guide.row_dimensions[row[0].row].height = 34
        for cell in row:
            cell.font = Font(name=FONT, size=11, color=INK)
            cell.alignment = Alignment(wrap_text=True, vertical="center")
    wb.save(destination)
    wb.close()
    return destination


def build_example(destination: Path = DESTINATION) -> GenerationResult:
    """Build template, workbook and sample via the same generator as the GUI."""
    destination.mkdir(parents=True, exist_ok=True)
    template = build_template(destination / "template.pptx")
    workbook = build_workbook(destination / "data.xlsx")
    result = generate(
        Presentation(str(template)), workbook, SHEET_NAME,
        list(range(2, len(ROWS) + 2)), destination / "sample-output.pptx",
        template_column="模板", mapping=MAPPING, header_row=1,
    )
    if result.generated_pages != 5 or result.warnings:
        raise ValueError(f"Example generation failed: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DESTINATION)
    args = parser.parse_args()
    build_example(args.output)


if __name__ == "__main__":
    main()
