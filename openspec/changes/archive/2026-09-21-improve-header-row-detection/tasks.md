## 1. 标题行检测算法升级 (`src/auto_detect.py`)

- [x] 1.1 重写 `detect_header_row()` 签名：从 `(tpl_names, row1, row2) -> int` 改为 `(tpl_names, rows) -> int`
- [x] 1.2 实现多行扫描逻辑：遍历 rows 前 5 行，计算每行模板名交集占比，跳过非空值 <2 的行，返回得分最低的行索引
- [x] 1.3 所有行得分为 0 时默认返回第 1 行

## 2. GUI 适配 (`src/gui.py`)

- [x] 2.1 UI 重排：标题行 Spinbox 移到模板列 Combobox 之前（Sheet → 标题行 → 模板列）
- [x] 2.2 Spinbox 上限从 `to=10` 改为 `to=15`
- [x] 2.3 更新 `_detect_header_row` 调用处：传入前 5 行数据而非 row1/row2
- [x] 2.4 Treeview 列逻辑简化：去掉 `key_columns` 动态计算，严格取 headers 前 5 列
- [x] 2.5 列宽计算改为 `max(120, min(280, len(h)*20))`
- [x] 2.6 窗口尺寸设置：`geometry("1100x720")` + `minsize(900, 550)`

## 2c. 映射区列数 & 窗口尺寸调整 (`src/gui.py`)

- [x] 2c.1 映射区 `COLUMNS` 从 3 改为 4
- [x] 2c.2 窗口 `geometry("1100x720")` → `geometry("1400x850")`，`minsize(900, 550)` → `minsize(1000, 600)`

## 2b. `_from_config` flag 一致性修复 (`src/gui.py`)

- [x] 2b.1 `_on_header_row_change` 添加 `self._hrow_from_config = True`，阻止 auto-detect 覆盖用户手动选择的标题行
- [x] 2b.2 `_on_tcol_change` 添加 `self._tcol_from_config = True`，阻止 auto-detect 覆盖用户手动选择的模板列
- [x] 2b.3 `_on_sheet_change` 添加 `self._last_tpl_path = ""`，切换 Sheet 后强制 auto-detect 重新运行

## 3. 验证

- [x] 3.1 验证标题在 Row 2/3 的情况，确认检测正确
- [x] 3.2 确认 Treeview 仅展示前 5 列
- [x] 3.3 确认标题行变更后 Treeview 和映射区正确刷新
- [x] 3.4 确认 config.toml 中 header_row 字段正确加载和保存
- [x] 3.5 Run `uv run --group dev pytest` 确保完整测试通过
