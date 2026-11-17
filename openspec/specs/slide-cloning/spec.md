# slide-cloning Specification

## Purpose
Define relationship-safe slide cloning that produces PowerPoint files without stale references or repair prompts.
## Requirements
### Requirement: Cloned slide has no stale relationship references
`clone_slide` 创建的 slide XML MUST 不包含对不存在或类型不匹配的关系的引用。当源 slide 的关系被跳过复制时（TAG、SLIDE_LAYOUT），对应的 spTree 中的 XML 元素 MUST 被一并移除。

#### Scenario: Tags references removed after clone
- **WHEN** 模板 slide 包含 `<tags>` 元素，其 `r:id` 指向 custom XML tag part
- **AND** `clone_slide` 跳过 TAG 关系类型
- **THEN** 克隆 slide 的 spTree 中不存在任何 `r:id` 属性值等于被跳过 rId 的 `<tags>` 元素

#### Scenario: Non-skipped references still remapped correctly
- **WHEN** 模板 slide 包含 `<blip r:embed="rId4">` 指向 image part
- **AND** `clone_slide` 复制 image 关系（rId4 → rId2）
- **THEN** 克隆 slide 的 spTree 中 `r:embed` 属性已被重映射为 `rId2`
- **AND** 克隆 slide 的 `.rels` 中 `rId2` 指向正确的 image target

#### Scenario: Slide layout reference not leaked into spTree
- **WHEN** 模板 slide 的 `.rels` 包含 `rId3` 指向 slideLayout
- **AND** clone_slide 跳过 SLIDE_LAYOUT 关系类型
- **THEN** 克隆 slide 的 spTree 中不存在对 `rId3` 的引用

### Requirement: Generated PPTX opens without repair dialog
`generate()` 生成的 PPTX 文件 MUST 能在 Microsoft PowerPoint 中直接打开，不触发修复对话框，且内容完整可见。

#### Scenario: Output with tag-bearing template opens cleanly
- **WHEN** 使用 `generate()` 处理含有 custom XML tags 的模板 slide 生成 PPTX
- **THEN** 输出的 `.pptx` 文件在 PowerPoint 中打开时不触发修复对话框
- **AND** 生成的 slide 中所有形状和图片完整可见
