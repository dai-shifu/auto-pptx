import re
import sys

from pptx import Presentation
from pptx.slide import Slide

# 匹配 {{tpl::名称}} 标识占位符（支持中文、英文、数字、连字符）
TPL_RE = re.compile(r"\{\{tpl::([\w\-一-鿿]+)\}\}")


def build_template_index(prs: Presentation) -> dict[str, Slide]:
    """扫描所有 Slide，建立 {模板名称: Slide} 索引。

    通过查找 {{tpl::名称}} 标识占位符识别模板页身份。

    Args:
        prs: 已加载的 Presentation 对象

    Returns:
        模板名称到 Slide 对象的映射
    """
    index: dict[str, Slide] = {}

    for slide in prs.slides:
        tpl_name = _extract_tpl_name(slide)
        if tpl_name is None:
            continue

        if tpl_name in index:
            print(f"警告: 模板标识 '{{{{tpl::{tpl_name}}}}}' 重复，使用第一个匹配的 Slide", file=sys.stderr)
            continue

        index[tpl_name] = slide

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
