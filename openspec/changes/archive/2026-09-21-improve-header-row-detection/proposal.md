## Why

Excel 第一行经常不是真正的标题行——可能被合并单元格占用作为"大标题"行，实际列名在 Row 2 甚至 Row 3。当前 GUI 把"标题行"放在"模板列"之后（Sheet → 模板列 → 标题行），逻辑顺序不对；且 `detect_header_row` 只比 Row 1 vs Row 2，无法处理标题在第 3+ 行的情况。同时 Treeview 展示列过多、窗口偏小，在大 Excel 场景体验不佳。

## What Changes

- **UI 重排**：标题行 Spinbox 移到模板列之前（Sheet → 标题行 → 模板列），反应用户应"先确定哪行是表头，再选模板列"的实际心智模型
- **标题行检测算法升级**：`detect_header_row` 从两行比较改为扫描前 5 行，找"模板名交集占比最低且非空值≥2"的行作为标题行。合并单元格残留行（大部分单元格为空）自动跳过
- **Spinbox 上限**：从 10 扩展到 15，覆盖更深层的合并单元格场景
- **Treeview 固定前 5 列**：不再动态计算关键列，始终展示前 5 列（基于指定标题行之后计算出的 headers），简化界面
- **列宽 + 窗口尺寸**：列宽增大到 `max(120, min(280, len(h)*20))`；窗口初始 `1100×720`，最小 `900×550`，适配 13 寸笔记本
- **fallback**：检测中所有行得分均为 0 时默认返回第 1 行

## Capabilities

### New Capabilities

- `header-row-detection`: 多行扫描的标题行自动检测算法，替代当前的二行比较法
- `treeview-column-limit`: Treeview 固定展示前 5 列（基于标题行计算出的 headers）

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

| 文件 | 变更 |
|------|------|
| `src/auto_detect.py` | `detect_header_row()` 签名和算法重写 |
| `src/gui.py` | UI 重排（标题行↔模板列位置互换）、Treeview 列逻辑简化、列宽/窗口尺寸调整、Spinbox 上限改为 15 |
| `src/config.py` | 无需改（已支持 `header_row` 字段，从 config 加载的逻辑已存在） |
