from pathlib import Path

import pytest
from openpyxl import Workbook
from pptx import Presentation
from pptx.util import Inches

from src.generator import GenerationResult, generate


def _presentation() -> Presentation:
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    marker = slide.shapes.add_textbox(Inches(-2), Inches(-2), Inches(1), Inches(1))
    marker.text = "{{tpl::cover}}"
    content = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(6), Inches(1))
    content.text = "{{标题}} / {{备注}}"
    return prs


def _workbook(path: Path, headers: list[str], rows: list[list[str]]) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "数据"
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(path)
    wb.close()
    return path


def test_generation_result_reports_partial_success(tmp_path):
    excel = _workbook(
        tmp_path / "data.xlsx",
        ["模板", "标题", "备注"],
        [["cover", "报告", ""], ["unknown", "跳过", ""]],
    )
    output = tmp_path / "output.pptx"

    result = generate(
        _presentation(),
        excel,
        "数据",
        [2, 3],
        output,
        template_column="模板",
        mapping={"标题": "标题"},
    )

    assert isinstance(result, GenerationResult)
    assert result.generated_pages == 1
    assert result.skipped_rows == [3]
    assert result.unmatched_templates == ["unknown"]
    assert result.unresolved_placeholders == ["备注"]
    assert output.exists()
    assert result.warnings


def test_duplicate_headers_are_rejected(tmp_path):
    excel = _workbook(tmp_path / "duplicate.xlsx", ["模板", "值", "值"], [["cover", "a", "b"]])

    with pytest.raises(ValueError, match="重复列名"):
        generate(
            _presentation(), excel, "数据", [2], tmp_path / "output.pptx",
            template_column="模板", mapping={},
        )


@pytest.mark.parametrize(
    ("mapping", "message"),
    [
        ({"不存在": "标题"}, "不存在的 Excel 列"),
        ({"标题": "标题", "备注": "标题"}, "同一占位符"),
    ],
)
def test_invalid_mapping_is_rejected(tmp_path, mapping, message):
    excel = _workbook(
        tmp_path / "mapping.xlsx",
        ["模板", "标题", "备注"],
        [["cover", "报告", "内容"]],
    )

    with pytest.raises(ValueError, match=message):
        generate(
            _presentation(), excel, "数据", [2], tmp_path / "output.pptx",
            template_column="模板", mapping=mapping,
        )


def test_zero_page_generation_does_not_create_output(tmp_path):
    excel = _workbook(tmp_path / "missing.xlsx", ["模板", "标题"], [["unknown", "报告"]])
    output = tmp_path / "output.pptx"

    with pytest.raises(ValueError, match="未生成任何幻灯片"):
        generate(
            _presentation(), excel, "数据", [2], output,
            template_column="模板", mapping={"标题": "标题"},
        )

    assert not output.exists()
