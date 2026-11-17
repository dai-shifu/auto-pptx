# template-matching Specification

## Purpose
Define discovery and matching of `{{tpl::name}}` slide markers, including slash-separated template values.
## Requirements
### Requirement: 标识占位符识别

系统 SHALL 扫描模板 PPT 中所有 Slide，查找 `{{tpl::名称}}` 格式的标识占位符，建立模板索引。

#### Scenario: 建立索引

- **WHEN** 模板 PPT 包含 3 页，分别有 `{{tpl::Ni-NTA}}`, `{{tpl::GST}}`, `{{tpl::Co-NTA}}`
- **THEN** 系统建立索引 {"Ni-NTA": Slide1, "GST": Slide2, "Co-NTA": Slide3}

#### Scenario: 无标识的 Slide

- **WHEN** 某 Slide 中没有 `{{tpl::` 标识
- **THEN** 该 Slide 不纳入模板索引，生成时不会被使用

#### Scenario: 重复标识

- **WHEN** 多个 Slide 包含相同的 `{{tpl::名称}}` 标识
- **THEN** 系统输出警告，使用第一个匹配的 Slide

### Requirement: 模板标识匹配不限制位置

系统 SHALL 识别文本框中的模板标识，无论其位于页面可见区域内还是画布外，不强制文本框使用负坐标。

模板制作建议：将标识文本框放到画布外，避免保留在生成页中的标识干扰内容展示。标识的位置由模板维护者设置。

#### Scenario: 标识位于页面内

- **WHEN** 模板页可见区域内的文本框包含 `{{tpl::报告}}`
- **THEN** 系统将该页纳入模板索引，不因坐标位置拒绝匹配

#### Scenario: 标识位于画布外

- **WHEN** 模板页画布外的文本框包含 `{{tpl::报告}}`
- **THEN** 系统同样识别该标识，标识不出现在页面可见内容中

### Requirement: 模板列值 "/" 分割直接匹配

系统 SHALL 将 Excel 模板列的值按 `"/"` 分割为多个子值，每个子值直接作为 tpl 名称匹配 `{{tpl::name}}` 标识的 Slide，不使用中间映射表。

#### Scenario: "/" 分割生成两个 Slide

- **WHEN** 模板列值为 "Ni-NTA/GST"，PPT 有 `{{tpl::Ni-NTA}}` 和 `{{tpl::GST}}` 标识
- **THEN** 系统为 "Ni-NTA" 和 "GST" 各生成 1 个 Slide，使用相同的行数据替换占位符

#### Scenario: 部分子值无匹配

- **WHEN** 模板列值为 "Ni-NTA/Unknown"，"Unknown" 在 PPT 中无对应标识
- **THEN** 系统为 "Ni-NTA" 生成 Slide，为 "Unknown" 输出警告并跳过

#### Scenario: 单值不分割

- **WHEN** 模板列值为 "Ni-NTA"，不含 "/" 字符
- **THEN** 系统不进行分割，直接匹配并生成 1 个 Slide

#### Scenario: 空分割部分

- **WHEN** 模板列值为 "Ni-NTA / / GST"，含多余 "/"
- **THEN** 系统忽略空部分，仅对 "Ni-NTA" 和 "GST" 进行匹配
