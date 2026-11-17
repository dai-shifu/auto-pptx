## ADDED Requirements

### Requirement: 模板列自动检测

系统 SHALL 在生成前自动检测 Excel 中模板列（用于 "/" 分割匹配模板的列）：遍历每列的唯一值集合，计算与 PPT `{{tpl::name}}` 名集合的交集比例，选择比例最高且 >0 的列。

#### Scenario: 唯一交集列

- **WHEN** Excel 仅 "填料" 列的值与 `{{tpl::name}}` 名有交集
- **THEN** 系统自动选择 "填料" 为模板列

#### Scenario: 多列有交集

- **WHEN** "填料" 列交集比例 0.8，"备注" 列交集比例 0.2
- **THEN** 系统选择比例最高的 "填料" 列

#### Scenario: 无交集列

- **WHEN** Excel 中没有任何列的值与 `{{tpl::name}}` 名有交集
- **THEN** 系统报错 "无法自动检测模板列，请确认 Excel 模板列的值与 PPT {{tpl::name}} 名称一致"

### Requirement: 映射自动匹配

系统 SHALL 在生成前自动匹配 Excel 列名到 PPT 占位符名的映射：大小写不敏感精确匹配优先，编辑距离 ≤2 模糊匹配次之，无匹配则不映射。

#### Scenario: 精确匹配优先

- **WHEN** Excel 列名 "分子量"，PPT 占位符 {{分子量}}
- **THEN** 映射为 "分子量" → "分子量"

#### Scenario: 模糊匹配补充

- **WHEN** Excel 列名 "温度"，PPT 占位符 {{温度(℃)}}，编辑距离 = 2
- **THEN** 映射为 "温度" → "温度(℃)"

#### Scenario: 精确匹配优先于模糊

- **WHEN** Excel 列名 "date"，PPT 同时有占位符 {{date}} 和 {{data}}
- **THEN** 精确匹配 "date" → "date"，不模糊匹配到 "data"

#### Scenario: 编辑距离超出阈值

- **WHEN** Excel 列名 "目标浓度"，PPT 占位符 {{终浓度}}，编辑距离 >2
- **THEN** 该列不自动映射，需用户手动选择

### Requirement: 自动检测与手动覆盖并存

系统 SHALL 在 GUI 中将自动检测结果展示为可编辑的下拉框，用户可手动调整每个占位符的映射。

#### Scenario: 自动检测结果展示

- **WHEN** 自动检测为占位符 "mw" 映射到 "分子量"
- **THEN** GUI 中 "mw" 对应的下拉框选中 "分子量"

#### Scenario: 用户手动修改

- **WHEN** 用户将 "mw" 的映射从 "分子量" 改为 "OD600"
- **THEN** 生成时使用 "OD600" 列的值填充 {{mw}} 占位符

#### Scenario: 用户手动取消

- **WHEN** 用户将 "mw" 的映射设为 "(不映射)"
- **THEN** 生成时 {{mw}} 占位符保持原文不变
