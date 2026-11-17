"""Build the small, repository-owned XLSX and PPTX test fixtures.

The builders in this module are the fixture contract. Tests normally write
the assets to ``tmp_path``; running this file refreshes the committed copies
under ``tests/fixtures`` for developer convenience.
All example project identifiers and row values are fabricated for testing.
"""

from pathlib import Path

from openpyxl import Workbook
from pptx import Presentation
from pptx.util import Inches


FIXTURES_DIR = Path(__file__).parent / "fixtures"

DATA_SHEET = "数据"
DATA_HEADERS = ("模板", "标题", "作者", "姓名", "部门", "销售额", "利润", "总结", "日期")
DATA_ROWS = (
    ("cover", "年度报告", "张三", "", "", "", "", "", ""),
    ("content", "", "", "李四", "华东区", "500万", "120万", "", ""),
    ("summary", "", "", "", "", "", "", "业绩优秀", "2026-01-01"),
)
PROJECT_ID_SHEET = "项目编号"
PROJECT_HEADERS = ("项目编号", "备注")
PROJECT_ROWS = (("DEMO-001", "首个项目"), ("DEMO-002", "第二个项目"))
DETAIL_SHEET = "项目明细"
DETAIL_HEADERS = ("项目编号", "填料", "日期")
DETAIL_ROWS = (("DEMO-001", "Ni-NTA", "2026-01-01"), ("DEMO-002", "GST", "2026-01-02"))

TEMPLATE_NAMES = ("cover", "content", "summary")
TEMPLATE_PLACEHOLDERS = {
    "cover": ("标题", "作者"),
    "content": ("姓名", "部门", "销售额", "利润"),
    "summary": ("总结", "日期"),
}


def build_template_pptx(destination: str | Path) -> Path:
    """Create the canonical three-slide template at *destination*."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    cover = prs.slides.add_slide(prs.slide_layouts[6])
    _add_textbox(cover, "{{tpl::cover}}", -5, -5, 3, 0.5)
    _add_textbox(cover, "{{标题}}", 1, 2, 10, 1)
    _add_textbox(cover, "作者: {{作者}}", 1, 3.5, 10, 0.5)

    content = prs.slides.add_slide(prs.slide_layouts[6])
    _add_textbox(content, "{{tpl::content}}", -5, -5, 3, 0.5)
    _add_textbox(content, "姓名: {{姓名}} - 部门: {{部门}}", 1, 0.5, 10, 0.5)
    table = content.shapes.add_table(3, 2, Inches(1), Inches(1.5), Inches(6), Inches(3)).table
    table.cell(0, 0).text = "项目"
    table.cell(0, 1).text = "数值"
    table.cell(1, 0).text = "销售额"
    table.cell(1, 1).text = "{{销售额}}"
    table.cell(2, 0).text = "利润"
    table.cell(2, 1).text = "{{利润}}"
    _add_textbox(content, "公司名称", 1, 5, 10, 0.5)

    summary = prs.slides.add_slide(prs.slide_layouts[6])
    _add_textbox(summary, "{{tpl::summary}}", -5, -5, 3, 0.5)
    _add_textbox(summary, "总结: {{总结}}", 1, 2, 10, 1)
    _add_textbox(summary, "日期: {{日期}}", 1, 3.5, 10, 0.5)

    prs.save(str(destination))
    return destination


def build_test_xlsx(destination: str | Path) -> Path:
    """Create the canonical workbook at *destination*."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    data = wb.active
    data.title = DATA_SHEET
    data.append(DATA_HEADERS)
    for row in DATA_ROWS:
        data.append(row)

    project_ids = wb.create_sheet(PROJECT_ID_SHEET)
    project_ids.append(PROJECT_HEADERS)
    for row in PROJECT_ROWS:
        project_ids.append(row)

    details = wb.create_sheet(DETAIL_SHEET)
    details.append(("测试说明", "标题位于第二行"))
    details.append(DETAIL_HEADERS)
    for row in DETAIL_ROWS:
        details.append(row)

    wb.save(str(destination))
    wb.close()
    return destination


def build_fixture_set(directory: str | Path) -> tuple[Path, Path]:
    """Create both canonical assets under *directory*."""
    directory = Path(directory)
    return (
        build_template_pptx(directory / "template.pptx"),
        build_test_xlsx(directory / "test_data.xlsx"),
    )


def _add_textbox(slide, text: str, left: float, top: float, width: float, height: float) -> None:
    box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    box.text_frame.text = text


# Backwards-compatible command helpers used by developers.
def create_template_pptx() -> Path:
    return build_template_pptx(FIXTURES_DIR / "template.pptx")


def create_test_excel() -> Path:
    return build_test_xlsx(FIXTURES_DIR / "test_data.xlsx")


if __name__ == "__main__":
    template_path, workbook_path = build_fixture_set(FIXTURES_DIR)
    print(f"Created: {template_path}")
    print(f"Created: {workbook_path}")
