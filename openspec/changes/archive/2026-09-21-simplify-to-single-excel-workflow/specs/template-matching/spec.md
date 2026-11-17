## MODIFIED Requirements

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

### Requirement: 隐藏标识占位符

标识占位符文本框 SHALL 位于页面可见区域外（负坐标），不干扰正常内容展示。

#### Scenario: 标识不干扰可见内容

- **WHEN** 用户打开模板 PPT 正常查看
- **THEN** 标识占位符不可见，不影响页面布局

## ADDED Requirements

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
