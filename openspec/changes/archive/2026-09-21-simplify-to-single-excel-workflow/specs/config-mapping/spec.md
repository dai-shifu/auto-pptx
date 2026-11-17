## REMOVED Requirements

### Requirement: 加载配置文件

**Reason**: 配置（模板列和映射）由 auto_detect 在运行时自动检测，不再需要配置文件。
**Migration**: 用户选择 PPT 和 Excel 后，系统自动检测模板列和映射。如有偏差，可通过 GUI 下拉框手动调整。

### Requirement: 列名到占位符映射

**Reason**: 映射由 `suggest_mapping()` 自动匹配（大小写不敏感精确匹配 + 编辑距离模糊匹配）。config.toml 中的 `[mapping]` 段不再需要。
**Migration**: GUI 中映射下拉框保留，用户可手动调整自动检测结果。

### Requirement: 模板标记列名

**Reason**: `template_column` 由 `detect_template_column()` 自动检测（集合交集比），config.toml 中的该字段不再需要。
**Migration**: 无需用户操作，系统自动检测模板列。

### Requirement: 项目编号列配置

**Reason**: 跨文件查找被移除，项目编号不再有特殊意义，仅是普通数据列。
**Migration**: 无。该概念不再存在于系统中。

### Requirement: 填料到模板映射配置

**Reason**: Excel 模板列的值直接等于 `{{tpl::name}}` 名，不存在不一致需要映射。`filler_map` 被移除。
**Migration**: 确保 Excel 模板列的值与 PPT `{{tpl::name}}` 名称一致（当前已一致）。

### Requirement: 数据标题行配置

**Reason**: 标题行固定为第 1 行，不再需要可配置。
**Migration**: 确保 Excel 第 1 行为标题行。

### Requirement: 配置持久化

**Reason**: config.toml 机制整体删除，配置不持久化。每次运行自动检测。
**Migration**: 如有映射调整需求，后续可通过 GUI 手动调整优化。

## ADDED Requirements

### Requirement: 自动检测模板列

系统 SHALL 在运行时自动检测 Excel 中标识模板的列：遍历每列唯一值，计算与 PPT `{{tpl::name}}` 名集合的交集比例，比例最高且 >0 的列即为模板列。

#### Scenario: 检测成功

- **WHEN** Excel "填料" 列包含值 "Ni-NTA", "GST", "Co-NTA"，PPT 有对应的 3 个 tpl 标识
- **THEN** 系统自动确定 "填料" 为模板列

#### Scenario: 检测失败

- **WHEN** Excel 中没有列的值与 `{{tpl::name}}` 名有交集
- **THEN** 系统报错提示用户检查模板列值是否与 `{{tpl::name}}` 一致

### Requirement: 自动检测映射

系统 SHALL 在运行时自动检测 Excel 列名到 PPT 占位符名的映射：大小写不敏感精确匹配优先，编辑距离 ≤2 模糊匹配次之。

#### Scenario: 精确匹配

- **WHEN** Excel 列名为 "分子量"，PPT 有占位符 `{{分子量}}`
- **THEN** 系统自动映射 "分子量" → "分子量"

#### Scenario: 模糊匹配

- **WHEN** Excel 列名为 "诱导温度"，PPT 有占位符 `{{诱导温度(℃）}}`
- **THEN** 系统自动映射 "诱导温度" → "诱导温度(℃）"（编辑距离范围内）

#### Scenario: 无匹配

- **WHEN** Excel 列名与所有占位符名均无匹配（精确和模糊均不满足）
- **THEN** 该列不在映射中，其值不参与占位符替换

### Requirement: GUI 映射手动覆盖

系统 SHALL 在 GUI 中为每个占位符提供下拉框（列名选项 + "(不映射)"），用户可手动调整自动检测的映射结果。

#### Scenario: 手动选择映射

- **WHEN** 自动检测将占位符 "mw" 映射到 "分子量"，用户手动改为 "OD600"
- **THEN** 生成时使用 "OD600" 列的数据填充 "mw" 占位符

#### Scenario: 取消映射

- **WHEN** 用户将某个占位符的映射设为 "(不映射)"
- **THEN** 该占位符在生成时保留原文不替换
