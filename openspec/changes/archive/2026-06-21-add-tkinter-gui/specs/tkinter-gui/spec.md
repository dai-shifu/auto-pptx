## ADDED Requirements

### Requirement: GUI 文件选择
系统 SHALL 提供 tkinter 窗口，包含"模板 PPT"和"Excel 数据"两个文件选择按钮，用户点击按钮后弹出系统原生文件对话框。

#### Scenario: 选择 Excel 文件
- **WHEN** 用户点击 Excel 行的"浏览"按钮
- **THEN** 系统弹出文件选择对话框，过滤显示 `.xlsx` 文件
- **THEN** 用户选择文件后，路径显示在对应输入框中

#### Scenario: 选择模板 PPT 文件
- **WHEN** 用户点击模板 PPT 行的"浏览"按钮
- **THEN** 系统弹出文件选择对话框，过滤显示 `.pptx` 文件
- **THEN** 用户选择文件后，路径显示在对应输入框中

### Requirement: 生成按钮
系统 SHALL 提供"生成 PPT"按钮，点击后调用现有生成流水线，并在状态栏显示结果。

#### Scenario: 生成成功
- **WHEN** 用户选择好模板和 Excel 后点击"生成 PPT"
- **THEN** 系统读取 config.toml（或自动检测映射），调用 generate()，输出 output.pptx 到 Excel 同目录
- **THEN** 状态栏显示"生成完成: output.pptx"

#### Scenario: 生成失败
- **WHEN** 生成过程中发生错误
- **THEN** 状态栏显示错误信息（红色文字）

### Requirement: 映射下拉配置
系统 SHALL 为每个 PPT 占位符提供下拉选择框，列出所有可用 Excel 列名，用户可手动调整映射关系。

#### Scenario: 自动匹配后手动调整
- **WHEN** 自动检测完成映射建议
- **THEN** 每个占位符旁显示下拉框，默认选中自动匹配的 Excel 列
- **THEN** 用户可下拉选择其他 Excel 列或"不映射"

### Requirement: 配置自动加载
系统启动时 SHALL 检查启动目录或 exe 同目录下的 `config.toml`，若存在则自动填充模板路径和映射关系。

#### Scenario: config.toml 存在
- **WHEN** 启动目录存在 config.toml
- **THEN** 自动加载其中的 template 路径和 mapping
- **THEN** 用户只需选择 Excel 即可生成

#### Scenario: config.toml 不存在
- **WHEN** 启动目录不存在 config.toml
- **THEN** 用户需手动选择模板 PPT
- **THEN** 选择模板和 Excel 后自动检测映射
