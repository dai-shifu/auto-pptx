## Why

`prune_slides` 只从 `sldIdLst` 中删除模板 slide，但没有清理 `presentation.xml.rels` 中的关系引用。Python-pptx 保存时仍会将未引用的 slide 部件写入 ZIP，导致 PPTX 内部结构不一致（`[Content_Types].xml` 和 `.rels` 声明了 slide 文件，但 `presentation.xml` 的 `sldIdLst` 未引用它们）。PowerPoint 打开时检测到不一致，触发修复对话框，修复后内容丢失变为空白 PPT。

## What Changes

- **修改 `prune_slides`**: 删除 slide 时同步调用 `prs.part.drop_rel(rId)` 清除 `presentation.xml.rels` 中的关系引用，让 Python-pptx 保存时不再写入孤立文件

## Capabilities

### New Capabilities

- `slide-pruning`: `prune_slides` 删除模板页后，生成的 PPTX 文件结构一致、无孤立部件，可直接在 PowerPoint 中正常打开

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- `src/pptx_engine.py`: `prune_slides` 函数增加 rId 解析和 `drop_rel` 调用（3 行代码变更）
- `src/generator.py`: 无需修改（调用 `prune_slides` 的接口不变）
