import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass

from pptx import Presentation
from pptx.slide import Slide

# 匹配 {{tpl::名称}} 标识占位符（支持中文、英文、数字、连字符）
TPL_RE = re.compile(r"\{\{tpl::([\w\-一-鿿]+)\}\}")


@dataclass(frozen=True)
class TemplatePage:
    number: int
    name: str | None
    slide: Slide
    usable: bool


def iter_template_pages(prs: Presentation) -> Iterator[TemplatePage]:
    """Scan source pages in order and mark the first occurrence of each name."""
    seen: set[str] = set()
    for number, slide in enumerate(prs.slides, start=1):
        name = _extract_tpl_name(slide)
        usable = name is not None and name not in seen
        if name is not None:
            seen.add(name)
        yield TemplatePage(number, name, slide, usable)


def build_template_index(prs: Presentation) -> dict[str, Slide]:
    """通过 {{tpl::名称}} 标识建立 {模板名称: Slide} 索引。"""
    index: dict[str, Slide] = {}
    for page in iter_template_pages(prs):
        if page.name is None:
            continue
        if not page.usable:
            print(f"警告: 模板标识 '{{{{tpl::{page.name}}}}}' 重复，使用第一个匹配的 Slide", file=sys.stderr)
            continue
        index[page.name] = page.slide
    return index


def _extract_tpl_name(slide: Slide) -> str | None:
    """从 Slide 中提取 {{tpl::名称}} 标识，返回名称或 None。"""
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for paragraph in shape.text_frame.paragraphs:
            full_text = "".join(run.text for run in paragraph.runs)
            match = TPL_RE.search(full_text)
            if match:
                return match.group(1)
    return None
