## ADDED Requirements

### Requirement: 逐行生成 PPT 页面
系统 SHALL 遍历 Excel 每一行数据，匹配模板页、原地替换占位符，生成对应 PPT 页面。

#### Scenario: 多行数据生成多页
- **WHEN** Excel 有 20 行数据
- **THEN** 输出 PPT 包含 20 页，每页对应一行数据

#### Scenario: 不同行使用不同模板
- **WHEN** Excel 中部分行标记为 "绩效报告"，部分行标记为 "项目汇报"
- **THEN** 各行使用对应模板生成页面，输出 PPT 中包含两种布局

### Requirement: 合并输出单个文件
系统 SHALL 将所有处理后的页面输出为单个 `.pptx` 文件，按模板原始顺序排列。

#### Scenario: 输出文件生成
- **WHEN** 处理完成所有行
- **THEN** 在指定路径生成一个 `.pptx` 文件，包含匹配到的页面，按模板原始顺序排列

#### Scenario: 删除未用模板页
- **WHEN** 模板有 10 页，Excel 只匹配了 3 页
- **THEN** 输出 PPT 仅包含被匹配的 3 页，其余 7 页被删除

### Requirement: 模板标记缺失处理
系统 SHALL 处理 Excel 行中模板标记为空或不匹配的情况。

#### Scenario: 模板标记为空
- **WHEN** 某行的模板标记列为空
- **THEN** 系统跳过该行并输出警告

#### Scenario: 模板标记不匹配
- **WHEN** 某行的模板标记在模板 PPT 中未找到对应的 `{{tpl::名称}}` 标识
- **THEN** 系统输出错误信息并退出
