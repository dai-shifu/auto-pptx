## ADDED Requirements

### Requirement: 加载配置文件

系统 SHALL 支持从 `config.toml` 文件加载配置（`template_column` 和 `[mapping]`）。

#### Scenario: 正常加载

- **WHEN** config.toml 存在且格式正确
- **THEN** 系统加载 `template_column` 和 `[mapping]` 段

#### Scenario: 配置文件不存在

- **WHEN** config.toml 文件不存在
- **THEN** 系统使用自动检测结果，不报错

### Requirement: 列名到占位符映射

config.toml SHALL 定义 `[mapping]` 段，格式为 `"Excel列名" = "PPT占位符名"`（excel_col → placeholder 方向）。

#### Scenario: 映射生效

- **WHEN** mapping 定义 `"标题" = "title"`，Excel 列为 "标题"
- **THEN** 该列数据填入 PPT 的 `{{title}}` 占位符

### Requirement: 模板标记列名

config.toml SHALL 定义 `template_column` 字段，指定 Excel 中标识模板的列名。该列的值经 `"/"` 分割后直接作为模板标识名称匹配 `{{tpl::name}}`。

#### Scenario: 指定模板列

- **WHEN** template_column 为 "填料"，Excel 该列值为 "Ni-NTA / GST"
- **THEN** 系统分割后查找 `{{tpl::Ni-NTA}}` 和 `{{tpl::GST}}` 标识的 Slide

### Requirement: 配置持久化

系统 SHALL 在生成完成后将当前 `template_column` 和 `mapping` 写入 `config.toml` 文件，下次启动自动加载。

#### Scenario: 保存配置

- **WHEN** 用户在 GUI 中设置模板列为 "标签"，映射为 `{"标题": "title"}`，点击生成
- **THEN** 系统将 `template_column = "标签"` 和 `[mapping]` 段写入 config.toml
