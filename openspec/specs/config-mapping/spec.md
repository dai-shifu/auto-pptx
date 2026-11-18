# config-mapping Specification

## Purpose
Define persisted Excel-column-to-PowerPoint-placeholder mappings and template-column selection.
## Requirements
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

系统 SHALL 在 GUI 中为每个非空 Excel 列名提供目标占位符下拉框（PPT 占位符选项 + "(不映射)"），用户可手动调整自动检测的映射结果，保持 Excel列→占位符 的方向。

#### Scenario: 手动选择映射

- **WHEN** 自动检测将 Excel 列 "分子量" 映射到占位符 "mw"，用户将该列的目标占位符改为 "mass"
- **THEN** 生成时使用 "分子量" 列的数据填充 "mass" 占位符

#### Scenario: 取消映射

- **WHEN** 用户将某个 Excel 列的目标占位符设为 "(不映射)"
- **THEN** 该列从 mapping 中移除，不参与占位符替换

### Requirement: 加载配置文件

系统 SHALL 支持从 `config.toml` 文件加载配置（`template_column` 和 `[mapping]`）。

#### Scenario: 正常加载

- **WHEN** config.toml 存在且格式正确
- **THEN** 系统加载 `template_column` 和 `[mapping]` 段

#### Scenario: 配置文件不存在

- **WHEN** config.toml 文件不存在
- **THEN** 系统使用自动检测结果，不报错

### Requirement: 列名到占位符映射

保存映射时，`config.toml` 的 `[mapping]` 段 SHALL 使用 `"Excel列名" = "PPT占位符名"` 格式（excel_col → placeholder 方向）。没有映射时不写入该段。

#### Scenario: 映射生效

- **WHEN** mapping 定义 `"标题" = "title"`，Excel 列为 "标题"
- **THEN** 该列数据填入 PPT 的 `{{title}}` 占位符

### Requirement: 模板标记列名

`config.toml` 中的 `template_column` 字段 SHALL 记录 Excel 中标识模板的列名；未指定时不写入该字段。该列的值经 `"/"` 分割后直接作为模板标识名称匹配 `{{tpl::name}}`。

#### Scenario: 指定模板列

- **WHEN** template_column 为 "填料"，Excel 该列值为 "Ni-NTA / GST"
- **THEN** 系统分割后查找 `{{tpl::Ni-NTA}}` 和 `{{tpl::GST}}` 标识的 Slide

### Requirement: 配置持久化

系统 SHALL 在生成完成后将当前 `template_column` 和 `mapping` 写入 `config.toml` 文件，下次启动自动加载。

#### Scenario: 保存配置

- **WHEN** 用户在 GUI 中设置模板列为 "标签"，映射为 `{"标题": "title"}`，点击生成
- **THEN** 系统将 `template_column = "标签"` 和 `[mapping]` 段写入 config.toml
