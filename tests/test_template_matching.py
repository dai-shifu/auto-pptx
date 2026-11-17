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
