import copy
import re
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.slide import Slide

# 匹配 {{xxx}} 占位符，不匹配 {{tpl::xxx}}
PLACEHOLDER_RE = re.compile(r"\{\{(?!tpl::)(.+?)\}\}")

# Slide 的 p: namespace
_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def load_template(path: str | Path) -> Presentation:
    """加载 PPT 模板到内存。"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"模板文件不存在: {path}")
    return Presentation(str(path))


def clone_slide(prs: Presentation, source_slide: Slide) -> Slide:
    """克隆 Slide 并追加到演示文稿末尾。

    通过 add_slide 建立结构骨架，再深度复制源 Slide 的 spTree 并
    复制图片等关系引用到新 Slide，实现完整克隆。
    """
    slide_layout = source_slide.slide_layout
    new_slide = prs.slides.add_slide(slide_layout)

    # 复制源 Slide 的非布局、非 tag 关系到新 Slide，建立 rId 映射
    rId_map: dict[str, str] = {}
    skipped_rids: set[str] = set()
    for rel in source_slide.part.rels.values():
        if rel.reltype in (RT.SLIDE_LAYOUT, RT.TAGS):
            skipped_rids.add(rel.rId)
            continue
        new_rId = new_slide.part.relate_to(
            rel.target_part if not rel.is_external else rel.target_ref,
            rel.reltype,
            rel.is_external,
        )
        rId_map[rel.rId] = new_rId

    # 深度复制源 spTree 并清理 skip 引用、重映射 rId
    source_spTree = source_slide._element.find(f"{{{_NS}}}cSld").find(f"{{{_NS}}}spTree")
    cloned_spTree = copy.deepcopy(source_spTree)
    if skipped_rids:
        _remove_skipped_refs(cloned_spTree, skipped_rids)
    _remap_rIds(cloned_spTree, rId_map)

    # 替换新 Slide 的 spTree
    new_cSld = new_slide._element.find(f"{{{_NS}}}cSld")
    new_spTree = new_cSld.find(f"{{{_NS}}}spTree")
    new_cSld.replace(new_spTree, cloned_spTree)

    # 清除 shapes 缓存，让 python-pptx 从更新后的 XML 重新读取
    if "shapes" in new_slide.__dict__:
        del new_slide.__dict__["shapes"]

    return new_slide


def _remap_rIds(element: etree._Element, rId_map: dict[str, str]) -> None:
    """递归更新 XML 元素中的 rId 属性引用。"""
    r_namespace = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    rId_attr = f"{{{r_namespace}}}id"
    embed_attr = f"{{{r_namespace}}}embed"
    link_attr = f"{{{r_namespace}}}link"

    for el in element.iter():
        for attr in (rId_attr, embed_attr, link_attr):
            val = el.get(attr)
            if val and val in rId_map:
                el.set(attr, rId_map[val])


def _remove_skipped_refs(element: etree._Element, skipped_rids: set[str]) -> None:
    """移除 XML 元素树中引用被跳过 rId 的子元素。

    遍历整个子树，找到 r:id / r:embed / r:link 属性值在 skipped_rids
    集合中的元素，从其父元素中移除。避免克隆 Slide 后残留对不存在或
    类型不匹配关系的引用。
    """
    r_namespace = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    rId_attr = f"{{{r_namespace}}}id"
    embed_attr = f"{{{r_namespace}}}embed"
    link_attr = f"{{{r_namespace}}}link"

    # 先收集要移除的元素，再统一移除（避免修改迭代器）
    to_remove: list[etree._Element] = []
    for el in element.iter():
        for attr in (rId_attr, embed_attr, link_attr):
            if el.get(attr) in skipped_rids:
                to_remove.append(el)
                break
    for el in to_remove:
        parent = el.getparent()
        if parent is not None:
            parent.remove(el)


def replace_in_slide(slide: Slide, data: dict[str, str]) -> None:
    """替换单个 Slide 中的所有占位符（文本框 + 表格单元格）。"""
    for shape in slide.shapes:
        # 文本框
        if shape.has_text_frame:
            _replace_in_text_frame(shape.text_frame, data)
        # 表格
        if shape.has_table:
            for cell in shape.table.iter_cells():
                _replace_in_text_frame(cell.text_frame, data)


def _replace_in_text_frame(text_frame, data: dict[str, str]) -> None:
    """替换文本框中所有段落的占位符。"""
    for paragraph in text_frame.paragraphs:
        _replace_in_paragraph(paragraph, data)


def _replace_in_paragraph(paragraph, data: dict[str, str]) -> None:
    """替换单个段落中的占位符。

    处理跨 Run 拆分的占位符：拼接所有 Run 文本 → 替换 → 写回第一个 Run → 清空其余。
    """
    runs = paragraph.runs
    if not runs:
        return

    # 拼接所有 Run 的文本
    full_text = "".join(run.text for run in runs)

    # 检查是否有占位符需要替换
    if not PLACEHOLDER_RE.search(full_text):
        return

    # 替换占位符（不存在的 key 保留原文）
    def replacer(match):
        key = match.group(1)
        return data.get(key, match.group(0))

    new_text = PLACEHOLDER_RE.sub(replacer, full_text)

    # 写回：第一个 Run 设为替换后的文本，其余清空
    runs[0].text = new_text
    for run in runs[1:]:
        run.text = ""


def prune_slides(prs: Presentation, count: int) -> None:
    """删除演示文稿前 count 个 Slide。

    通过反向遍历 _sldIdLst 删除前 count 个 Slide 条目，并同步清除
    presentation.xml.rels 中的关系引用，避免保存时写入孤立文件。
    封装对 python-pptx 私有 API 的依赖。
    """
    if count <= 0:
        return
    r_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    sldIdLst = prs.slides._sldIdLst
    to_remove = list(sldIdLst)[:count]
    for sldId in reversed(to_remove):
        rId = sldId.get(f"{{{r_ns}}}id")
        sldIdLst.remove(sldId)
        if rId and rId in prs.part.rels:
            prs.part.drop_rel(rId)
