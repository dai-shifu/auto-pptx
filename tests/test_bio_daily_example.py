"""Validate the user-facing example through the existing generation pipeline."""

from pathlib import Path

from openpyxl import load_workbook
from pptx import Presentation

from scripts.build_bio_daily import build_example
from src.generator import generate
from src.template_matching import build_template_index


EXAMPLE = Path(__file__).resolve().parents[1] / "examples/bio-daily"


def _slide_contents(path: Path) -> list[list[str]]:
    contents = []
    for slide in Presentation(str(path)).slides:
        texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                texts.append(shape.text)
            if shape.has_table:
                texts.extend(cell.text for cell in shape.table.iter_cells())
        contents.append(texts)
    return contents


def test_shipped_example_generates_with_automatic_mapping(tmp_path):
    """User files work with automatic suggestions and produce the documented order."""
    result = generate(
        Presentation(str(EXAMPLE / "template.pptx")),
        EXAMPLE / "data.xlsx", "日报数据", [2, 3, 4, 5, 6],
        tmp_path / "report.pptx", header_row=1,
    )
    assert result.generated_pages == 5
    assert result.warnings == []
    actual = _slide_contents(result.output_path)
    assert actual == _slide_contents(EXAMPLE / "sample-output.pptx")
    assert "{{tpl::日报总览}}" in actual[0]
    for page, project in zip(actual[1:4], ("DEMO-001", "DEMO-002", "DEMO-003")):
        assert project in page
    assert "{{tpl::风险与计划}}" in actual[4]
    for slide in Presentation(str(EXAMPLE / "template.pptx")).slides:
        marker = next(shape for shape in slide.shapes
                      if shape.has_text_frame and "{{tpl::" in shape.text)
        assert marker.left + marker.width <= 0


def test_builder_reproduces_delivered_content(tmp_path):
    """Protect the shipped XLSX and PPTX from drifting away from their builder."""
    result = build_example(tmp_path)
    assert result.warnings == []
    for name in ("template.pptx", "sample-output.pptx"):
        assert _slide_contents(tmp_path / name) == _slide_contents(EXAMPLE / name)
    rebuilt = load_workbook(tmp_path / "data.xlsx", data_only=True)
    shipped = load_workbook(EXAMPLE / "data.xlsx", data_only=True)
    try:
        assert rebuilt.sheetnames == shipped.sheetnames
        for sheet in rebuilt.sheetnames:
            assert list(rebuilt[sheet].values) == list(shipped[sheet].values)
    finally:
        rebuilt.close()
        shipped.close()
    index = build_template_index(Presentation(str(tmp_path / "template.pptx")))
    assert list(index) == ["日报总览", "项目进展", "风险与计划"]
