## Why

`clone_slide` 在跳过 TAG 和 SLIDE_LAYOUT 关系时不将其加入 `rId_map`，但克隆后的 spTree XML 中仍保持对这些旧 rId 的引用。由于 `_remap_rIds` 只更新存在于 `rId_map` 中的 rId，被跳过的 rId 在原值保持不变。新 slide 的 `.rels` 会为后续关系复用这些 rId 编号，导致类型错配——例如 `<tags r:id="rId1">` 在新 slide 中实际指向了 slideLayout。PowerPoint 检测到 `<tags>` 元素的目标不是 user-defined XML part，触发"文件需要修复"对话框。

## What Changes

- **修改 `clone_slide`**: 追踪跳过的 rId，在重映射后从克隆的 spTree 中移除引用这些 rId 的 XML 元素

## Capabilities

### New Capabilities

- `slide-cloning`: `clone_slide` 克隆的 slide XML 中不包含对不存在或类型不匹配的关系的引用，生成的 PPTX 可在 PowerPoint 中直接打开无需修复

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- `src/pptx_engine.py`: `clone_slide` 函数增加跳过 rId 的追踪和 spTree 清理（约 15 行代码变更）
- 不影响 `_remap_rIds`、`prune_slides`、`replace_in_slide` 或其他模块
