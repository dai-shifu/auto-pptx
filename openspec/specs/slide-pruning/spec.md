# Slide Pruning

## Purpose

Ensure removing template slides also removes their package relationships and
parts so generated presentations remain structurally valid in PowerPoint.

## Requirements

### Requirement: Pruned PPTX has no orphaned slide parts
`prune_slides` 从 `sldIdLst` 删除模板 slide 后，生成的 PPTX 文件内部结构 MUST 一致：`[Content_Types].xml`、`presentation.xml.rels`、和 ZIP 内的 slide 文件集合 MUST 仅包含 `sldIdLst` 中实际引用的 slides。

#### Scenario: Single template slide removed after clone
- **WHEN** `prune_slides(prs, 1)` 从含 1 个模板 slide 和 1 个克隆 slide 的 presentation 中删除模板
- **THEN** 保存后的 PPTX 中 `[Content_Types].xml` 只包含 1 个 `/ppt/slides/slide*.xml` 条目
- **AND** `presentation.xml.rels` 只包含 1 个指向 slide 的 Relationship
- **AND** ZIP 中没有未被 `sldIdLst` 引用的 orphan slide 文件

#### Scenario: Multiple template slides removed
- **WHEN** `prune_slides(prs, 3)` 从含 3 个模板 slide 和 5 个克隆 slide 的 presentation 中删除前 3 个
- **THEN** 保存后的 PPTX 中 slide 部件总数等于 5（仅克隆 slides）
- **AND** 所有 orphan 文件均不存在

#### Scenario: Zero count is no-op
- **WHEN** `prune_slides(prs, 0)` 被调用
- **THEN** presentation 没有任何变化

### Requirement: Generated PPTX opens in PowerPoint without repair
`generate()` 生成的 PPTX 文件 MUST 能在 Microsoft PowerPoint 中直接打开，不触发"文件需要修复"对话框。

#### Scenario: Single-row generation produces valid PPTX
- **WHEN** 使用 `generate()` 处理 1 个 Excel 行与 1 个模板 slide
- **THEN** 输出的 `.pptx` 文件可在 PowerPoint 中正常打开，无修复对话框
- **AND** 生成的 slide 包含来自 Excel 的替换数据
