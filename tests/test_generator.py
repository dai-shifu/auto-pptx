from pathlib import Path

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
