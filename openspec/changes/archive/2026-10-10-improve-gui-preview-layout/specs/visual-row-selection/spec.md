## MODIFIED Requirements

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
