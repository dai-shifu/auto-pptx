## 1. Implementation

- [x] 1.1 修改 `prune_slides` 函数：遍历 `to_remove` 时提取 `rId` 属性，从 `sldIdLst` 删除后调用 `prs.part.drop_rel(rId)` 清除 `.rels` 中的关系引用
- [x] 1.2 确认生成的 PPTX 内部结构一致：使用 ZIP + lxml 检查 `[Content_Types].xml`、`presentation.xml.rels`、和 slide 文件无 orphan

## 2. Testing

- [x] 2.1 端到端测试：用 `template_demo.pptx` 和 示例 Excel 生成 PPTX，验证无 orphan 文件
- [x] 2.2 边界测试：零 slide 删除（count=0）、全部删除（count=len(slides)）
- [x] 2.3 运行现有测试套件确认无回归
