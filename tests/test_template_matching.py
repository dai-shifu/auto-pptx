from pathlib import Path

from pptx import Presentation

from src.pptx_engine import load_template
from src.template_matching import build_template_index


def test_build_template_index(generated_fixtures: Path):
    prs = load_template(generated_fixtures / "template.pptx")
    index = build_template_index(prs)
    assert "cover" in index
    assert "content" in index
    assert "summary" in index
    assert len(index) == 3


def test_template_index_no_tpl():
    """无标识的 Slide 不应纳入索引。"""
    prs = Presentation()
    prs.slides.add_slide(prs.slide_layouts[6])
    index = build_template_index(prs)
    assert len(index) == 0


def test_duplicate_template_id_keeps_first_slide(generated_fixtures, capsys):
    prs = load_template(generated_fixtures / "template.pptx")
    first = prs.slides[0]
    duplicate = prs.slides.add_slide(prs.slide_layouts[6])
    duplicate.shapes.add_textbox(0, 0, 1000000, 1000000).text = "{{tpl::cover}}"

    assert build_template_index(prs)["cover"] == first
    assert "重复，使用第一个" in capsys.readouterr().err
