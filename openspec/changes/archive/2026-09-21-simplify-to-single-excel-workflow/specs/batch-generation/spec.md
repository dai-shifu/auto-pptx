## MODIFIED Requirements

### Requirement: 逐行生成 PPT 页面

系统 SHALL 遍历用户勾选的 Excel 行，对每行读取模板列值（支持 "/" 分割直接匹配）、同行数据按自动检测的 mapping 转换后替换占位符，生成对应 PPT 页面。

#### Scenario: 多行数据生成多页

- **WHEN** 用户勾选 3 行数据
- **THEN** 系统生成 3 组新 Slide（含 "/" 分割产生的多页），按生成顺序排列

#### Scenario: 不同行使用不同模板

- **WHEN** 勾选的行中，部分行模板列值为 "Ni-NTA"，部分行模板列值为 "GST"
- **THEN** 各行使用对应模板生成 Slide，输出 PPT 中包含两种布局

### Requirement: 合并输出单个文件

系统 SHALL 将所有生成的新 Slide 输出为单个 `.pptx` 文件。

#### Scenario: 输出文件生成

- **WHEN** 处理完成所有勾选行
- **THEN** 在源头 Excel 同目录下生成 `output_<时间戳>.pptx` 文件

#### Scenario: 删除未用模板页

- **WHEN** 模板有 10 页，仅匹配到了 2 个模板标识
- **THEN** 输出 PPT 仅包含生成的新 Slide 页，原始 10 个模板页被删除

### Requirement: 模板标记缺失处理

系统 SHALL 处理 Excel 行中模板列值为空或不匹配的情况。

#### Scenario: 模板列值为空

- **WHEN** 勾选的某行模板列值为空
- **THEN** 系统跳过该行并输出警告

#### Scenario: 模板列值不匹配

- **WHEN** 模板列值 `"/"` 分割后的某部分在 PPT 中未找到对应的 `{{tpl::name}}` 标识
- **THEN** 系统输出警告跳过该部分，其余正常生成
