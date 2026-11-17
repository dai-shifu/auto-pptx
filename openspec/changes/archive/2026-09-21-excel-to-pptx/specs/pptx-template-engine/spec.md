## ADDED Requirements

### Requirement: 加载模板 PPT
系统 SHALL 支持通过 `Presentation(path)` 整文件加载模板 PPT 到内存，作为操作副本。

#### Scenario: 加载模板
- **WHEN** 用户提供一个 `.pptx` 模板文件
- **THEN** 系统将完整模板加载到内存，保留所有元素（文本框、表格、图片、样式、排版）

### Requirement: 替换文本框中的占位符
系统 SHALL 扫描 Slide 中所有文本框，查找 `{{xxx}}` 格式的占位符并替换为实际数据。

#### Scenario: 单个占位符替换
- **WHEN** 文本框内容为 "姓名: {{name}}"，数据中 name="张三"
- **THEN** 文本框内容变为 "姓名: 张三"

#### Scenario: 多个占位符替换
- **WHEN** 文本框内容为 "{{name}} - {{dept}}"，数据中 name="张三", dept="华东"
- **THEN** 文本框内容变为 "张三 - 华东"

#### Scenario: 占位符不存在于数据中
- **WHEN** 文本框中包含 `{{unknown}}`，但数据中没有 unknown 字段
- **THEN** 系统保留该占位符原文不变

### Requirement: 替换表格单元格中的占位符
系统 SHALL 扫描 Slide 中所有表格单元格，查找 `{{xxx}}` 格式的占位符并替换为实际数据。

#### Scenario: 表格单元格替换
- **WHEN** 表格某单元格内容为 "{{sales}}"，数据中 sales="120万"
- **THEN** 单元格内容变为 "120万"

### Requirement: 保留非占位符内容
系统 SHALL 保留模板中不包含占位符的所有内容不变，包括固定文本、图片、图表占位等。

#### Scenario: 固定文本不变
- **WHEN** 文本框内容为 "公司名称"（无占位符）
- **THEN** 替换后内容仍为 "公司名称"

#### Scenario: 含图片的 Slide 不受影响
- **WHEN** 模板 Slide 中包含图片元素
- **THEN** 替换后图片及其位置、大小保持不变

#### Scenario: 含表格的 Slide 不受影响
- **WHEN** 模板 Slide 中包含表格
- **THEN** 替换后表格结构、样式、边框保持不变

### Requirement: 删除未使用的模板页
系统 SHALL 删除未被任何 Excel 行匹配到的模板页。

#### Scenario: 删除未用页
- **WHEN** 模板有 10 页，Excel 只匹配了 3 页
- **THEN** 输出 PPT 仅包含被匹配的 3 页，其余 7 页被删除

#### Scenario: 保留模板原始顺序
- **WHEN** 多个模板页被匹配
- **THEN** 输出页按模板中的原始顺序排列
