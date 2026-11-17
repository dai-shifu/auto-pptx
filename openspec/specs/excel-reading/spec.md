# excel-reading Specification

## Purpose
Define reliable reading of XLSX sheets, headers, rows, and empty cells for presentation generation.
## Requirements
### Requirement: 读取 Excel 文件
系统 SHALL 支持读取 `.xlsx` 格式的 Excel 文件，返回结构化行数据。

#### Scenario: 正常读取
- **WHEN** 用户提供一个包含表头和数据的 `.xlsx` 文件
- **THEN** 系统读取标题行作为列名，后续每行作为一条记录，返回列表结构

#### Scenario: 文件不存在
- **WHEN** 用户提供的 Excel 文件路径不存在
- **THEN** GUI 显示明确的读取错误信息，本次读取失败，应用窗口保持可用

#### Scenario: 空文件
- **WHEN** Excel 文件只有表头没有数据行
- **THEN** GUI 预览不显示数据行，未选择数据时不得生成 PPT，应用窗口保持可用

### Requirement: 支持中文表头
系统 SHALL 支持 Excel 表头为中文字符，通过映射表转换为占位符名。

#### Scenario: 中文表头映射
- **WHEN** Excel 表头为 ["温度", "时间"]，config.toml [mapping] 中定义 温度→温度、时间→反应时间
- **THEN** 系统正确读取数据并按映射关系转换键名

### Requirement: 处理空单元格
系统 SHALL 处理 Excel 中的空单元格，将其替换为空字符串。

#### Scenario: 部分单元格为空
- **WHEN** 某行数据中部分单元格为空
- **THEN** 对应占位符被替换为空字符串，不报错
