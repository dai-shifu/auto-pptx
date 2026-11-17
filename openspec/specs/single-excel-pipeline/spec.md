# single-excel-pipeline Specification

## Purpose
Define the primary single-Excel workflow from sheet and row selection through slide generation.
## Requirements
### Requirement: 单 Excel 加载

系统 SHALL 加载用户指定的 Excel 文件及其选定 Sheet，按自动检测或用户选择的标题行读取列名和后续数据行。

#### Scenario: 正常加载

- **WHEN** Excel 文件存在且包含多个 Sheet，用户选择 "Sheet1"
- **THEN** 系统从选定标题行读取列名，并从下一行起读取数据

#### Scenario: 单 Sheet 自动选择

- **WHEN** Excel 文件仅包含一个 Sheet
- **THEN** 系统自动使用该 Sheet，无需用户选择

#### Scenario: Sheet 不存在

- **WHEN** 用户指定的 Sheet 名在当前 Excel 中不存在
- **THEN** 系统输出错误信息并终止生成

### Requirement: 可视化行选择

系统 SHALL 在 Treeview 中展示勾选列、前五个数据列，以及必要时追加的模板列，遵循 `data-preview-columns` 的列选择规则。用户通过复选框勾选要生成的行，勾选状态按 Excel 实际行号记录。

#### Scenario: 默认全不选

- **WHEN** 用户加载 Excel 后首次展示数据
- **THEN** 所有数据行默认不勾选，用户必须勾选数据行或点击“全选”后才能生成

#### Scenario: 勾选行

- **WHEN** 用户勾选第 2 和第 5 行，取消勾选其他行
- **THEN** 生成时仅使用第 2 和第 5 行的数据

#### Scenario: 全选/取消全选

- **WHEN** 用户点击 "全选" 或 "取消全选" 按钮
- **THEN** 所有数据行被统一勾选或取消勾选

#### Scenario: 空数据

- **WHEN** Excel 的指定 Sheet 没有数据行（仅标题行）
- **THEN** Treeview 为空，状态栏提示无数据

### Requirement: 逐行生成 PPT

系统 SHALL 遍历用户勾选的行，对每行读取模板列值（支持 "/" 分割）、直接匹配 `{{tpl::name}}` 标识的 Slide、将同行数据按 mapping 转换后替换占位符。

#### Scenario: 单模板生成

- **WHEN** 用户勾选第 2 行，模板列值为 "Ni-NTA"，PPT 有 `{{tpl::Ni-NTA}}` 标识的 Slide
- **THEN** 系统克隆该 Slide 并替换占位符，生成 1 页

#### Scenario: "/" 分割生成多页

- **WHEN** 用户勾选第 2 行，模板列值为 "Ni-NTA/GST"，PPT 有对应标识的两个 Slide
- **THEN** 系统生成 2 页，分别基于两个模板 Slide，使用相同的行数据替换

#### Scenario: 输出顺序遵循所选 Excel 行和模板列

- **WHEN** 用户勾选多个 Excel 行，且某行模板列以 "/" 指定多个模板
- **THEN** 输出页按所选 Excel 实际行号升序排列，同一行按模板列从左到右的名称顺序生成
- **AND** 输出顺序不依赖模板页在输入 PPT 中的原始排列

#### Scenario: 模板列值无匹配

- **WHEN** 模板列值为 "ABC"，PPT 中没有 `{{tpl::ABC}}` 标识的 Slide
- **THEN** 系统输出警告并跳过该模板

#### Scenario: 空模板列

- **WHEN** 某行模板列值为空
- **THEN** 系统输出警告并跳过该行

#### Scenario: 未勾选任何行

- **WHEN** 用户点击生成但未勾选任何数据行
- **THEN** 系统报错提示至少勾选一行

### Requirement: 删除原始模板页

系统 SHALL 在生成完成后删除所有原始模板 Slide，仅保留通过 clone_slide 生成的新 Slide。

#### Scenario: 模板页删除

- **WHEN** 模板 PPT 有 5 个 Slide，生成了 3 个新 Slide
- **THEN** 最终输出包含 3 个 Slide，原始 5 个模板页全部删除
