## MODIFIED Requirements

### Requirement: 行复选框勾选

系统 SHALL 为 Treeview 的每行提供复选框，默认全不选，用户可逐行勾选/取消。勾选 SHALL 对应已成功载入的 Excel 数据。切换 Excel、工作表或有效标题行时 SHALL 清空勾选。只换 PPT 模板或编辑映射、且当前 Excel 数据不变时 SHALL 保留勾选。当前 Excel 或工作表加载失败时，GUI SHALL 清空旧预览和勾选，报告失败，并且 SHALL NOT 使用旧行生成。

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

#### Scenario: 模板或映射变化但数据不变

- **WHEN** 用户替换 PPT 模板或编辑映射，Excel 文件、工作表、有效标题行及当前数据均未改变
- **THEN** 原先勾选的 Excel 实际行号保持勾选

#### Scenario: 数据范围变化

- **WHEN** 用户改用不同的 Excel、切换工作表，或当前有效标题行改变
- **THEN** 新预览没有勾选行，不沿用此前的行号

#### Scenario: 已勾选后载入失败

- **WHEN** 用户在有效预览中勾选了数据，再打开不可读取的 Excel 或加载失败的工作表
- **THEN** GUI 提示读取失败，不再显示旧数据行或保留旧勾选
- **AND** 生成入口不使用上一次加载的数据
