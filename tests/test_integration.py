from pathlib import Path

import pytest
from openpyxl import load_workbook
from pptx import Presentation

from src.generator import generate
from src.pptx_engine import load_template


def test_end_to_end(tmp_path, generated_fixtures: Path):
    """按选择顺序生成并替换内容，不保留原模板页。"""
    prs = load_template(generated_fixtures / "template.pptx")
    output = tmp_path / "output.pptx"

    generate(
        prs=prs,
        excel_path=generated_fixtures / "test_data.xlsx",
        sheet_name="数据",
        selected_rows=[4, 2, 3],
        output_path=output,
    )

    result = Presentation(str(output))
    assert len(result.slides) == 3
    expected_texts = (
        {"{{tpl::summary}}", "总结: 业绩优秀", "日期: 2026-01-01"},
        {"{{tpl::cover}}", "年度报告", "作者: 张三"},
        {"{{tpl::content}}", "姓名: 李四 - 部门: 华东区"},
    )
    for slide, expected in zip(result.slides, expected_texts):
        texts = {shape.text_frame.text for shape in slide.shapes if shape.has_text_frame}
        assert expected <= texts

    table, = (shape.table for shape in result.slides[2].shapes if shape.has_table)
    assert table.cell(1, 1).text == "500万"
    assert table.cell(2, 1).text == "120万"


def test_selected_rows_with_same_project_id_generate_separate_slides(tmp_path, generated_fixtures: Path):
    excel = generated_fixtures / "test_data.xlsx"
    workbook = load_workbook(excel)
    sheet = workbook.create_sheet("重复编号")
    sheet.append(("模板", "标题", "项目编号"))
    sheet.append(("cover", "第一份报告", "DEMO-001"))
    sheet.append(("cover", "第二份报告", "DEMO-001"))
    workbook.save(excel)
    workbook.close()

    output = tmp_path / "output.pptx"
    generate(
        prs=load_template(generated_fixtures / "template.pptx"),
        excel_path=excel,
        sheet_name=sheet.title,
        selected_rows=[2, 3],
        output_path=output,
        template_column="模板",
        mapping={"标题": "标题", "项目编号": "作者"},
    )

    first, second = Presentation(str(output)).slides
    for slide, title in ((first, "第一份报告"), (second, "第二份报告")):
        texts = {shape.text_frame.text for shape in slide.shapes if shape.has_text_frame}
        assert {title, "作者: DEMO-001"} <= texts


def test_end_to_end_empty(tmp_path, generated_fixtures: Path):
    """空选择应失败，且不留下输出文件。"""
    prs = load_template(generated_fixtures / "template.pptx")
    output = tmp_path / "output.pptx"

    with pytest.raises(ValueError, match=r"^未选择任何数据行，无法生成 PPT$"):
        generate(
            prs=prs,
            excel_path=generated_fixtures / "test_data.xlsx",
            sheet_name="数据",
            selected_rows=[],
            output_path=output,
        )
    assert not output.exists()


def test_invalid_sheet(tmp_path, generated_fixtures: Path):
    """未知工作表应报错，且不留下输出文件。"""
    prs = load_template(generated_fixtures / "template.pptx")
    output = tmp_path / "output.pptx"

    with pytest.raises(ValueError, match=r"^Sheet '不存在的Sheet' 不存在，可用 Sheet:"):
        generate(
            prs=prs,
            excel_path=generated_fixtures / "test_data.xlsx",
            sheet_name="不存在的Sheet",
            selected_rows=[2],
            output_path=output,
        )
    assert not output.exists()
