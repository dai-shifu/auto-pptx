## Context

`prune_slides` 通过操作 `prs.slides._sldIdLst` 移除生成的 PPTX 中的模板 slide。当前实现只从 `_sldIdLst` XML 元素移除 `sldId`，但未清理 `presentation.xml.rels` 中的对应 `Relationship`。Python-pptx 的 `save()` 遍历 part 图确定输出部件 — 即使 `sldIdLst` 不再引用某个 slide，只要 `.rels` 文件仍然包含该关系，`[Content_Types].xml` 就会包含该条目，ZIP 中也会写入该 slide 文件。这造成内部不一致，PowerPoint 打开时触发修复。

## Goals / Non-Goals

**Goals:**
- 确保 `prune_slides` 后生成的 PPTX 内部结构完全一致
- 最小化代码变更，只修改 `prune_slides` 函数
- 不改变 `prune_slides` 的函数签名和调用接口

**Non-Goals:**
- 不修改 `clone_slide`、`replace_in_slide`、`generate` 等其他函数
- 不改变 PPTX 的 slide 内容或占位符替换逻辑
- 不处理 Excel 列映射或模板匹配的问题

## Decisions

### 决策：在 `prune_slides` 中调用 `prs.part.drop_rel(rId)`

**方案**：遍历要删除的 `sldId` 时，提取其 `rId` 属性，从 `sldIdLst` 移除后同步调用 `prs.part.drop_rel(rId)`。

```python
r_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
rId = sldId.get(f"{{{r_ns}}}id")
if rId and rId in prs.part.rels:
    prs.part.drop_rel(rId)
```

**备选方案**：
- **重建 Presentation**：克隆到新 `Presentation` 对象。干净但需复制所有 slide master、layout、主题，复杂度高。
- **手动清理 ZIP**：save 后解压 → 清理 → 重新打包。过于复杂且易出错。
- **`prs.part.package.drop_rel`**：在更底层操作。`prs.part.drop_rel` 是 pptx 提供的更封装的 API，直接操作 presentation 部件的关系。

**选择理由**：`drop_rel` 方法已经存在于 python-pptx API 中，是最简单、最安全的修复方式。3 行代码，无需额外依赖或复杂的 XML 操作。

### 决策：不同时清理 orphaned slide parts 自身

`prs.part.drop_rel(rId)` 只删除关系引用（从 `.rels` XML 中移除），不删除 slide 文件本身。但 Python-pptx 的 `save()` 通过遍历 part 图确定要写入的内容 — 一旦关系被移除，slide part 不再可达，`save()` 就不会写入它。经过实测验证：调用 `drop_rel` 后保存，ZIP 中不再包含 orphan 文件。

## Risks / Trade-offs

- **`rId` 属性名空间可能变化** — `sldId` XML 元素的 `rId` 属性使用 `http://schemas.openxmlformats.org/officeDocument/2006/relationships` 命名空间，这是 OOXML 标准规范，不会变化。
- **反向遍历顺序** — 当前实现用 `reversed(to_remove)` 反向遍历删除。从 `sldIdLst` 移除时顺序不影响结果；`drop_rel` 按 `rId` 键名删除，同样与顺序无关。
