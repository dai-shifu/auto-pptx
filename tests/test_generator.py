from pathlib import Path

import pytest
from openpyxl import Workbook

from src.excel_reader import extract_project_ids, find_row_by_project_id
from src.pptx_engine import clone_slide, load_template, replace_in_slide
from src.template_matching import build_template_index

# ── clone_slide ──


def test_clone_slide_preserves_shapes(generated_fixtures: Path):
    prs = load_template(generated_fixtures / "template.pptx")
    tpl_index = build_template_index(prs)
    source = tpl_index["content"]
    source_count = len(source.shapes)

    cloned = clone_slide(prs, source)
    assert len(cloned.shapes) == source_count


def test_clone_slide_replace_placeholders(generated_fixtures: Path):
    prs = load_template(generated_fixtures / "template.pptx")
    tpl_index = build_template_index(prs)
    source = tpl_index["summary"]

    cloned = clone_slide(prs, source)
    replace_in_slide(cloned, {"日期": "2026-01-01", "总结": "测试通过"})

    texts = []
    for shape in cloned.shapes:
        if shape.has_text_frame:
            texts.append(shape.text_frame.text)
    combined = "".join(texts)
    assert "2026-01-01" in combined
    assert "测试通过" in combined
    assert "{{tpl::summary}}" in combined


def test_clone_slide_multiple_clones_same_source(generated_fixtures: Path):
    prs = load_template(generated_fixtures / "template.pptx")
    tpl_index = build_template_index(prs)
    source = tpl_index["content"]

    c1 = clone_slide(prs, source)
    c2 = clone_slide(prs, source)
    assert len(c1.shapes) == len(source.shapes)
    assert len(c2.shapes) == len(source.shapes)
    assert len(prs.slides) > 2


# ── extract_project_ids ──


def test_extract_project_ids(generated_fixtures: Path):
    from openpyxl import load_workbook
    wb = load_workbook(generated_fixtures / "test_data.xlsx", data_only=True)
    ws = wb["项目编号"]

    ids = extract_project_ids(ws, start_row=2, end_row=3, col_name="项目编号")
    assert len(ids) == 2
    assert ids[0] == "DEMO-001"
    assert ids[1] == "DEMO-002"
    wb.close()


def test_extract_project_ids_empty_range(generated_fixtures: Path):
    from openpyxl import load_workbook
    wb = load_workbook(generated_fixtures / "test_data.xlsx", data_only=True)
    ws = wb["项目编号"]

    ids = extract_project_ids(ws, start_row=6, end_row=6, col_name="项目编号")
    assert len(ids) == 0
    wb.close()


def test_extract_project_ids_missing_column():
    wb = Workbook()
    ws = wb.active
    ws.append(["其他列"])
    ws.append(["值"])

    with pytest.raises(ValueError, match="缺少"):
        extract_project_ids(ws, start_row=2, end_row=2, col_name="项目编号")
    wb.close()


# ── find_row_by_project_id ──


def test_find_row_by_project_id(generated_fixtures: Path):
    from openpyxl import load_workbook
    wb = load_workbook(generated_fixtures / "test_data.xlsx", data_only=True)
    ws = wb["项目明细"]

    row = find_row_by_project_id(ws, "DEMO-001", header_row=2)
    assert row is not None
    assert "填料" in row
    assert row["项目编号"] == "DEMO-001"
    wb.close()


def test_find_row_by_project_id_not_found(generated_fixtures: Path):
    from openpyxl import load_workbook
    wb = load_workbook(generated_fixtures / "test_data.xlsx", data_only=True)
    ws = wb["项目明细"]

    row = find_row_by_project_id(ws, "NONEXIST", header_row=2)
    assert row is None
    wb.close()
