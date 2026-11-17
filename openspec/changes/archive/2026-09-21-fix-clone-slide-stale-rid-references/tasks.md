## 1. Implementation

- [x] 1.1 新增 `_remove_skipped_refs(element, skipped_rids)` 辅助函数：遍历 XML 元素树，移除 `r:id`/`r:embed`/`r:link` 属性值在 `skipped_rids` 集合中的元素
- [x] 1.2 修改 `clone_slide`：收集被跳过关系的 rId → 调用 `_remove_skipped_refs` 清理克隆 spTree → 移除 `_remap_rIds` 中已被清理的 rId 映射逻辑

## 2. Testing

- [x] 2.1 端到端测试：用 `template_demo.pptx`（含 custom XML tags）+ 示例 Excel 生成 PPTX，验证输出无 stale rId 引用
- [x] 2.2 端到端测试：用 fixture `template.pptx`（不含 tags）生成 PPTX 确认兼容无回归
- [x] 2.3 运行现有测试套件确保无回归
