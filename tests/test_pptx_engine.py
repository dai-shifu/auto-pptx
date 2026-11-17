from pathlib import Path

import pytest

from src.pptx_engine import load_template, replace_in_slide


def test_load_template(generated_fixtures: Path):
    prs = load_template(generated_fixtures / "template.pptx")
    assert len(prs.slides) == 3


def test_load_template_not_found():
    with pytest.raises(FileNotFoundError, match="模板文件不存在"):
        load_template("nonexistent.pptx")


def test_replace_text_placeholder(generated_fixtures: Path):
    prs = load_template(generated_fixtures / "template.pptx")
    slide = prs.slides[0]  # cover
    replace_in_slide(slide, {"标题": "测试标题", "作者": "测试作者"})

    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            texts.append(shape.text_frame.text)

    assert any("测试标题" in t for t in texts)
    assert any("测试作者" in t for t in texts)
    assert not any("{{标题}}" in t for t in texts)


def test_replace_table_placeholder(generated_fixtures: Path):
    prs = load_template(generated_fixtures / "template.pptx")
    slide = prs.slides[1]  # content（含表格）
    replace_in_slide(slide, {"姓名": "张三", "部门": "华东", "销售额": "100万", "利润": "50万"})

    for shape in slide.shapes:
        if shape.has_table:
            table = shape.table
            assert table.cell(1, 1).text == "100万"
            assert table.cell(2, 1).text == "50万"


def test_replace_missing_placeholder_unchanged(generated_fixtures: Path):
    prs = load_template(generated_fixtures / "template.pptx")
    slide = prs.slides[0]  # cover
    replace_in_slide(slide, {"标题": "测试标题"})
    # author 没有提供数据，应保留原文
    for shape in slide.shapes:
        if shape.has_text_frame:
            if "作者" in shape.text_frame.text:
                assert "{{作者}}" in shape.text_frame.text


def test_fixed_text_preserved(generated_fixtures: Path):
    prs = load_template(generated_fixtures / "template.pptx")
    slide = prs.slides[1]  # content
    replace_in_slide(slide, {"姓名": "张三", "部门": "华东", "销售额": "100万", "利润": "50万"})

    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            texts.append(shape.text_frame.text)
    assert "公司名称" in texts
