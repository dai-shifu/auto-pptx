# mapping-direction Specification

## Purpose
Define Excel column to PowerPoint placeholder as the single mapping direction used across detection, configuration, GUI, and generation.
## Requirements
### Requirement: 映射方向统一为 Excel列→占位符

系统 SHALL 在全链路统一使用 `{excel_col: placeholder}` 格式的映射字典，其中 key 是 Excel 列名，value 是 PPT 占位符名。

#### Scenario: generate 直接使用

- **WHEN** mapping 为 `{"标题": "title", "作者": "author"}`
- **THEN** 行数据中 "标题" 列的值替换 PPT 中 `{{title}}` 占位符，"作者" 列的值替换 `{{author}}` 占位符

#### Scenario: GUI 构建映射

- **WHEN** 用户在 GUI 中设置 "标题 → title" 和 "作者 → (不映射)"
- **THEN** 传入 generate 的 mapping 为 `{"标题": "title"}`

#### Scenario: config.toml 存储

- **WHEN** config.toml `[mapping]` 段定义 `"标题" = "title"`
- **THEN** 加载后 mapping 为 `{"标题": "title"}`

### Requirement: 翻转点集中在 detect_and_suggest

系统 SHALL 在 `detect_and_suggest()` 中将 `suggest_mapping()` 返回的 `{placeholder: excel_col}` 翻转为 `{excel_col: placeholder}` 后返回。

#### Scenario: 翻转生效

- **WHEN** suggest_mapping 返回 `{"title": "标题", "author": "作者"}`
- **THEN** detect_and_suggest 返回 mapping 为 `{"标题": "title", "作者": "author"}`
