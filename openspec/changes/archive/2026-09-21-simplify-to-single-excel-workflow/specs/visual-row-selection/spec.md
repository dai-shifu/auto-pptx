## ADDED Requirements

### Requirement: Treeview 数据预览

系统 SHALL 在 GUI 中使用 ttk.Treeview 展示 Excel 当前 Sheet 的关键列数据：行号 + 模板列 + 映射引用的数据列。

#### Scenario: 展示关键列

- **WHEN** 模板列检测为 "填料"，映射列包括 "分子量" 和 "OD600"
- **THEN** Treeview 列依次为：#（行号）、填料、分子量、OD600

#### Scenario: 多列横向滚动

- **WHEN** 映射列超过可见宽度
- **THEN** Treeview 显示水平滚动条

#### Scenario: Sheet 切换刷新

- **WHEN** 用户切换到另一个 Sheet
- **THEN** Treeview 清空并加载新 Sheet 的数据，默认全选

### Requirement: 行复选框勾选

系统 SHALL 为 Treeview 的每行提供复选框，默认全选，用户可逐行勾选/取消。

#### Scenario: 默认全选

- **WHEN** 用户首次加载 Excel
- **THEN** 所有数据行复选框默认勾选

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

系统 SHALL 在生成 PPT 时仅使用用户勾选的行，行号从标题行（第 1 行）之后开始计数。

#### Scenario: 传入勾选行号

- **WHEN** 用户勾选 Treeview 中第 2 和第 4 个数据行（对应 Excel 第 3 和第 5 行）
- **THEN** generate() 收到 selected_rows = [3, 5]

#### Scenario: 未勾选任何行

- **WHEN** 用户点击生成但所有行均未勾选
- **THEN** 系统弹窗报错 "请至少勾选一行数据"
