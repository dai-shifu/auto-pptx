## ADDED Requirements

### Requirement: 标识占位符识别
系统 SHALL 扫描模板 PPT 中所有 Slide，查找 `{{tpl::名称}}` 格式的标识占位符，建立模板索引。

#### Scenario: 建立索引
- **WHEN** 模板 PPT 包含 3 页，分别有 `{{tpl::绩效报告}}`, `{{tpl::项目汇报}}`, `{{tpl::季度总结}}`
- **THEN** 系统建立索引 {"绩效报告": Slide1, "项目汇报": Slide2, "季度总结": Slide3}

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
