from pathlib import Path

import pytest
from openpyxl import Workbook
from pptx import Presentation

from src.excel_reader import extract_project_ids, find_row_by_project_id
from src.generator import generate
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


# ── end-to-end (single Excel) ──


def test_generate_with_excel(tmp_path, generated_fixtures: Path):
    """端到端测试：单 Excel 管线。

    使用测试 fixtures 的 Excel（test_data.xlsx），其中"模板"列值
    对应 PPT 模板的 {{tpl::cover}}, {{tpl::content}}, {{tpl::summary}} 标识。
    """
    prs = load_template(generated_fixtures / "template.pptx")
    output = tmp_path / "output.pptx"

    generate(
        prs=prs,
        excel_path=generated_fixtures / "test_data.xlsx",
        sheet_name="数据",
        selected_rows=[2, 3, 4],
        output_path=output,
    )

    result = Presentation(str(output))
    assert len(result.slides) >= 2  # 2 rows with valid template markers

    all_texts: list[str] = []
    for slide in result.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                all_texts.append(shape.text_frame.text)
            if shape.has_table:
                for cell in shape.table.iter_cells():
                    all_texts.append(cell.text)

    combined = " ".join(all_texts)
    assert "年度报告" in combined
    assert "张三" in combined


def test_generate_empty_selection(tmp_path, generated_fixtures: Path):
    """空选择应失败，且不留下输出文件。"""
    prs = load_template(generated_fixtures / "template.pptx")
    output = tmp_path / "output.pptx"

    with pytest.raises(ValueError):
        generate(
            prs=prs,
            excel_path=generated_fixtures / "test_data.xlsx",
            sheet_name="数据",
            selected_rows=[],
            output_path=output,
        )
    assert not output.exists()


def test_generate_invalid_sheet(tmp_path, generated_fixtures: Path):
    """无效 Sheet 名应抛出 ValueError。"""
    prs = load_template(generated_fixtures / "template.pptx")

    with pytest.raises(ValueError, match="Sheet"):
        generate(
            prs=prs,
            excel_path=generated_fixtures / "test_data.xlsx",
            sheet_name="不存在的Sheet",
            selected_rows=[2],
            output_path=tmp_path / "unused.pptx",
        )
