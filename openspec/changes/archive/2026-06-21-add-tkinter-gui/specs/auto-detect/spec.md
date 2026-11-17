## ADDED Requirements

### Requirement: 模板列自动检测
系统 SHALL 自动识别 Excel 中哪一列是"模板列"（其值对应 PPT 中的 `{{tpl::名称}}` 标识）。

#### Scenario: 唯一匹配
- **WHEN** Excel 仅有一列的值能全部在 PPT 模板名集合中找到匹配
- **THEN** 该列被自动识别为模板列

#### Scenario: 多列候选
- **WHEN** 多列都能匹配模板名集合
- **THEN** 选择匹配率最高的列作为模板列
- **THEN** 匹配率 = 该列唯一值 ∩ 模板名集合 / 该列唯一值总数

#### Scenario: 无法匹配
- **WHEN** 所有 Excel 列与 PPT 模板名集合的交集均为空
- **THEN** 界面显示警告，要求用户手动选择模板列

### Requirement: 映射自动建议
系统 SHALL 根据 Excel 列名和 PPT 占位符名自动建议映射关系。

#### Scenario: 大小写不敏感匹配
- **WHEN** Excel 列名 `Name` 与占位符名 `name` 仅大小写不同
- **THEN** 系统自动建议将 `Name` 映射到 `name`

#### Scenario: 编辑距离匹配
- **WHEN** Excel 列名与占位符名编辑距离 ≤2（单个汉字或英文字符差异）
- **THEN** 系统自动建议将最接近的配对进行映射

#### Scenario: 无匹配
- **WHEN** Excel 列名与所有占位符名的编辑距离均 >2
- **THEN** 映射默认为"不映射"，由用户手动选择
