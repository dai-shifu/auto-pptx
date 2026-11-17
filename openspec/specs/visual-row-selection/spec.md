# visual-row-selection Specification

## Purpose
Define GUI preview, selection, and bulk-selection behavior for choosing Excel rows to generate.
## Requirements
### Requirement: Treeview 数据预览

系统 SHALL 在 GUI 中使用 ttk.Treeview 展示 Excel 当前 Sheet 的勾选列、前五个数据列，以及必要时追加的模板列，遵循 `data-preview-columns` 的列选择规则。预览 SHALL 不显示横向滚动条，所有预览列宽度 SHALL 适配可见宽度；右侧竖向滚动条 SHALL 拥有独立空间，不因列宽或数据行数增加而被挤掉。

#### Scenario: 展示关键列

- **WHEN** Sheet 标题为 `[名称, 填料, 分子量, OD600, 备注, 其他]`，模板列为 `填料`
- **THEN** Treeview 显示 `[#, 名称, 填料, 分子量, OD600, 备注]`，模板列不重复展示

#### Scenario: 多列适配可见宽度

- **WHEN** 预览包含六个数据列且窗口缩小至支持的最低尺寸
- **THEN** 列宽收缩并保持所有预览列可见，不显示横向滚动条
- **AND** 被截断的内容可通过 tooltip 查看

#### Scenario: Sheet 切换刷新

- **WHEN** 用户切换到另一个 Sheet
- **THEN** Treeview 清空并加载新 Sheet 的数据，沿用既有 Sheet 切换时的勾选状态初始化行为

#### Scenario: 300 行数据的竖向滚动

- **WHEN** 当前 Sheet 有 300 条数据且行数超过预览区可见行数
- **THEN** 右侧竖向滚动条可见并允许滚动到最后一条数据
- **AND** 用户可以勾选最后一条数据，仍以其 Excel 实际行号参与生成

### Requirement: 行复选框勾选

系统 SHALL 为 Treeview 的每行提供复选框，默认全不选，用户可逐行勾选/取消。

#### Scenario: 默认全不选

- **WHEN** 用户首次加载 Excel
- **THEN** 所有数据行复选框默认不勾选

#### Scenario: 逐行勾选取消

- **WHEN** 用户点击某行的复选框
- **THEN** 该行勾选状态切换

#### Scenario: 全选按钮

- **WHEN** 用户点击 "全选" 按钮
- **THEN** 所有数据行被勾选

#### Scenario: 取消全选按钮

- **WHEN** 用户点击 "取消全选" 按钮
- **THEN** 所有数据行被取消勾选

### Requirement: 生成使用勾选行

系统 SHALL 在生成 PPT 时仅使用用户勾选的行，行号从当前标题行之后开始按 Excel 实际行号计数。

#### Scenario: 传入勾选行号

- **WHEN** 当前标题行为第 2 行，用户勾选 Treeview 中第 2 和第 4 个数据行（对应 Excel 第 4 和第 6 行）
- **THEN** generate() 收到 selected_rows = [4, 6]

#### Scenario: 未勾选任何行

- **WHEN** 用户点击生成但所有行均未勾选
- **THEN** 系统弹窗报错 "请至少勾选一行数据"
