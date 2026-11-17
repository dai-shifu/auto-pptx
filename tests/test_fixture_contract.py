"""Semantic checks keeping generated and committed fixtures in sync."""

import re
from pathlib import Path

from openpyxl import load_workbook
from pptx import Presentation

from src.template_matching import build_template_index
from tests.create_fixtures import (
    DATA_HEADERS,
    DATA_ROWS,
    DATA_SHEET,
    DETAIL_HEADERS,
    DETAIL_ROWS,
    DETAIL_SHEET,
    PROJECT_HEADERS,
    PROJECT_ROWS,
    PROJECT_ID_SHEET,
    TEMPLATE_NAMES,
    TEMPLATE_PLACEHOLDERS,
)


COMMITTED_FIXTURES = Path(__file__).parent / "fixtures"
PLACEHOLDER_RE = re.compile(r"\{\{(?!tpl::)(.+?)\}\}")


def test_generated_fixture_contract(generated_fixtures: Path):
    _assert_pptx_contract(generated_fixtures / "template.pptx")
    _assert_xlsx_contract(generated_fixtures / "test_data.xlsx")


def test_committed_fixture_contract():
    _assert_pptx_contract(COMMITTED_FIXTURES / "template.pptx")
    _assert_xlsx_contract(COMMITTED_FIXTURES / "test_data.xlsx")


def _assert_pptx_contract(path: Path) -> None:
    prs = Presentation(str(path))
    index = build_template_index(prs)

    assert len(prs.slides) == len(TEMPLATE_NAMES)
    assert tuple(index) == TEMPLATE_NAMES

    for template_name, expected_placeholders in TEMPLATE_PLACEHOLDERS.items():
        texts = _slide_texts(index[template_name])
        assert f"{{{{tpl::{template_name}}}}}" in texts
        found = {
            match.group(1)
            for text in texts
            for match in PLACEHOLDER_RE.finditer(text)
        }
        assert found == set(expected_placeholders)


def _assert_xlsx_contract(path: Path) -> None:
    wb = load_workbook(path, data_only=True)
    try:
        assert wb.sheetnames == [DATA_SHEET, PROJECT_ID_SHEET, DETAIL_SHEET]
        assert _row_values(wb[DATA_SHEET], 1) == DATA_HEADERS
        assert tuple(_row_values(wb[DATA_SHEET], row) for row in range(2, 5)) == DATA_ROWS
        assert _row_values(wb[PROJECT_ID_SHEET], 1) == PROJECT_HEADERS
        assert tuple(_row_values(wb[PROJECT_ID_SHEET], row) for row in range(2, 4)) == PROJECT_ROWS
        assert _row_values(wb[DETAIL_SHEET], 2) == DETAIL_HEADERS
        assert tuple(_row_values(wb[DETAIL_SHEET], row) for row in range(3, 5)) == DETAIL_ROWS
    finally:
        wb.close()


def _slide_texts(slide) -> list[str]:
    texts: list[str] = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            texts.append(shape.text_frame.text)
        if shape.has_table:
            texts.extend(cell.text for cell in shape.table.iter_cells())
    return texts


def _row_values(worksheet, row: int) -> tuple[str, ...]:
    return tuple(
        str(worksheet.cell(row=row, column=column).value or "")
        for column in range(1, worksheet.max_column + 1)
    )
