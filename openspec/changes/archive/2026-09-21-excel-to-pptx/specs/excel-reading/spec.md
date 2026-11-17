## ADDED Requirements

### Requirement: 读取 Excel 文件
系统 SHALL 支持读取 `.xlsx` 格式的 Excel 文件，返回结构化行数据。

#### Scenario: 正常读取
- **WHEN** 用户提供一个包含表头和数据的 `.xlsx` 文件
- **THEN** 系统读取第一行作为列名，后续每行作为一条记录，返回列表结构

#### Scenario: 文件不存在
- **WHEN** 用户提供的 Excel 文件路径不存在
- **THEN** 系统输出明确错误信息并退出

#### Scenario: 空文件
- **WHEN** Excel 文件只有表头没有数据行
- **THEN** 系统输出提示信息并正常退出，不生成 PPT

### Requirement: 支持中文表头
系统 SHALL 支持 Excel 表头为中文字符，通过映射表转换为占位符名。

#### Scenario: 中文表头映射
- **WHEN** Excel 表头为 ["姓名", "部门", "销售额"]，config.yaml 中定义映射 姓名→name, 部门→dept
- **THEN** 系统正确读取数据并按映射关系转换键名

### Requirement: 处理空单元格
系统 SHALL 处理 Excel 中的空单元格，将其替换为空字符串。

#### Scenario: 部分单元格为空
- **WHEN** 某行数据中部分单元格为空
- **THEN** 对应占位符被替换为空字符串，不报错
