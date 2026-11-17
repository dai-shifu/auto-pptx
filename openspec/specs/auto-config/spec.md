# auto-config Specification

## Purpose
Define automatic template-column and placeholder-mapping suggestions together with GUI controls that let users override those suggestions.
## Requirements
### Requirement: 模板列自动检测

系统 SHALL 在加载 Excel 后自动检测模板列并通过自动检测结果填充下拉框默认值，同时允许用户手动在下拉框中切换选择。

#### Scenario: 自动检测成功

- **WHEN** Excel "填料" 列包含值 "Ni-NTA", "GST", "Co-NTA"，PPT 有对应的 3 个 tpl 标识
- **THEN** 模板列下拉框默认选中 "填料"，用户可手动切换

#### Scenario: 自动检测失败

- **WHEN** Excel 中没有列的值与 `{{tpl::name}}` 名有交集
- **THEN** 模板列下拉框保持未选中状态，用户可手动从 Excel 列名中选择

#### Scenario: 用户手动指定

- **WHEN** 用户在下拉框中从 "填料" 切换到 "标签"
- **THEN** 生成时使用 "标签" 列做 "/" 分割匹配模板

### Requirement: 映射自动匹配

系统 SHALL 在生成前自动匹配 Excel 列名到 PPT 占位符名的映射：大小写不敏感精确匹配优先，编辑距离 ≤2 模糊匹配次之，返回格式为 `{excel_col: placeholder}`。

#### Scenario: 精确匹配

- **WHEN** Excel 列名为 "标题"，PPT 有占位符 `{{标题}}`
- **THEN** mapping 为 `{"标题": "标题"}`

#### Scenario: 模糊匹配

- **WHEN** Excel 列名为 "诱导温度"，PPT 有占位符 `{{诱导温度(℃）}}`
- **THEN** mapping 为 `{"诱导温度": "诱导温度(℃）"}`

### Requirement: 自动检测与手动覆盖并存

系统 SHALL 在 GUI 中以 Excel 列名为每个映射项的来源，将自动检测结果展示为可调整的占位符下拉框，用户可手动覆盖每个 Excel 列的目标占位符。

#### Scenario: 自动检测结果展示

- **WHEN** 自动检测建议 Excel 列 "分子量" 映射到占位符 "mw"
- **THEN** GUI 中 "分子量" 对应的下拉框选中 "mw"

#### Scenario: 用户手动修改

- **WHEN** 用户将 "分子量" 列的目标占位符从 "mw" 改为 "mass"
- **THEN** 生成时使用 "分子量" 列的值填充 {{mass}} 占位符

#### Scenario: 用户手动取消

- **WHEN** 用户将 "分子量" 列的目标占位符设为 "(不映射)"
- **THEN** 该 Excel 列不参与占位符替换

### Requirement: GUI 映射手动覆盖

系统 SHALL 在 GUI 中以 Excel列→占位符 的格式展示映射：每行显示一个 Excel 列名，下拉框选择对应映射到的 PPT 占位符名。

#### Scenario: 显示格式

- **WHEN** mapping 为 `{"标题": "title", "作者": "author"}`
- **THEN** GUI 显示 "标题 → title"、"作者 → author"，下拉框可选 "(不映射)"

#### Scenario: 手动修改

- **WHEN** 用户将 "标题" 的映射从 "title" 改为 "(不映射)"
- **THEN** "标题" 从 mapping 中移除，生成时不参与替换
