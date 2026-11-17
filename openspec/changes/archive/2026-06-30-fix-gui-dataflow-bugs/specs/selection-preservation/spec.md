## MODIFIED Requirements

### Requirement: 切换模板列时保留勾选

`_rebuild_treeview()` SHALL 在仅模板列变化时保留当前 `_checked` 集合中的勾选状态。

#### Scenario: 模板列切换保留勾选

- **WHEN** 用户在 Treeview 中勾选了行 2、4、6，然后切换模板列下拉框
- **THEN** 行 2、4、6 的勾选保持，仅 Treeview 显示的列发生变化

#### Scenario: Sheet 切换重置全不选

- **WHEN** 用户在 Treeview 中勾选了行 2、4、6，然后切换到另一个 Sheet
- **THEN** 所有行恢复为**不勾选**状态（`_checked` 为空），用户需手动勾选想要生成的行

### Requirement: 首次加载默认为全不选

当 Excel 数据首次加载到 Treeview 时，所有行 SHALL 默认为不勾选状态。

#### Scenario: 浏览 Excel 后首次加载

- **WHEN** 用户浏览 Excel 文件并选择 Sheet
- **THEN** Treeview 中所有行显示为 ☐ 不勾选状态

## ADDED Requirements

### Requirement: 点击事件使用 Button-1 避免漂移

`_on_tree_click` SHALL 绑定 `<Button-1>` 而非 `<ButtonRelease-1>`，在鼠标按下瞬间锁定目标行，避免按下到释放之间的鼠标漂移导致选中错误的行。

#### Scenario: 点击 checkbox 精确切换

- **WHEN** 用户在第一行 checkbox 列按下鼠标
- **THEN** 仅第一行的勾选状态切换，不影响其他行

### Requirement: 点击 checkbox 后阻止 Treeview 默认选中行为

`_on_tree_click` 在 checkbox 列（`#1`）处理完 toggle 后 SHALL 返回 `"break"`，阻止事件继续传播到 Treeview 默认选中行为（避免该行被蓝色高亮选中）。

#### Scenario: 点击 checkbox 不触发行选中

- **WHEN** 用户在 checkbox 列点击
- **THEN** 勾选状态切换，但 Treeview 不将该行设为选中（蓝色高亮）状态
