## Context

当前 GUI 的 `detect_header_row` 只比较 Row 1 和 Row 2，无法处理标题行在第 3 行及以后的 Excel。UI 布局中"标题行"在"模板列"右侧，不符合"先定标题行再选模板列"的逻辑顺序。此设计仅涉及 `src/auto_detect.py` 和 `src/gui.py` 两个文件，无外部依赖变更。

## Goals / Non-Goals

**Goals:**
- 重排 UI：标题行 Spinbox → 模板列 Combobox（左到右顺序）
- 升级 `detect_header_row()` 算法：扫描前 5 行，返回模板名交集占比最低的行
- 合并单元格残留行（非空值 < 2）自动跳过
- Treeview 严格显示前 5 列（基于标题行计算出的 headers）
- 列宽从 `max(100, min(200, len*15))` 增大到 `max(120, min(280, len*20))`
- 窗口初始 `1400×850`，最小 `1000×600`
- 映射配置改为 4 列排列
- Spinbox 上限 `to=15`
- 检测得分全为 0 时默认返回第 1 行

**Non-Goals:**
- 不改 Treeview 的交互逻辑（勾选、全选、取消全选保持不变）
- 不改映射区逻辑
- 不改 config 持久化（`Config` dataclass 已有 `header_row` 字段）
- 不改 `read_sheet_rows`（已正确支持 `header_row` 参数）
- 不改 title/checkbox/scrollbar 等 UI 元素

## Decisions

### 1. 标题行检测算法：取"最低得分"而非"最高得分"

**选 A**：遍历前 5 行，找模板名交集占比最低的行（标题行不应匹配模板名）。

理由：标题行是"描述性文字"（如"项目名""批次号"），它们不会匹配 `{{tpl::Ni-NTA}}` 中的模板名。数据行的值（如 "Ni-NTA" "GST"）才会。因此标题行得分应当接近 0，数据行得分 > 0。

备选 B（取最高分）：如果 Excel 没有模板列，所有行得分为 0，最高分也是 0，无法区分。取最低分 + 跳过空值 <2 行更稳健。

### 2. Treeview 列数：严格前 5 列

去掉现有的 `key_columns`（模板列 + 映射列）动态计算逻辑。始终取 headers 前 5 列。映射区的 Combobox 已可完整查看和配置映射关系，Treeview 只需提供数据快照。

### 3. `detect_header_row` 签名变更

```python
# 旧
def detect_header_row(tpl_names: set[str], row1: list[str], row2: list[str]) -> int:

# 新
def detect_header_row(tpl_names: set[str], rows: list[list[str]]) -> int:
```

调用方改为传入前 5 行：`rows = temp_rows[:5]`（第 1 行是 Row 1 的 headers，之后是数据行）。

### 4. 窗口尺寸

`geometry("1400x850")` + `minsize(1000, 600)`。在 1920×1080 下占约 73%×79%，2K 屏下舒适不占满。13 寸（1280×720）会超出，但 minsize 限制已提供基本可用性。

## Risks / Trade-offs

- **前 5 列可能不是用户关心的列** → Treeview 用于快速浏览数据，精确映射在映射区完成。5 列在 1100px 窗口下每列 ~180px，足够看清中文列名
- **检测 5 行不够深** → Spinbox 上限 15 允许手动覆盖；5 行覆盖常见的合并单元格（1-3 行标题前的内容）
- **旧 `detect_header_row` 被其他代码引用** → 检查 `src/generator.py`：当前 GUI 生成时直接传 `header_row=self._header_row` 参数，不经过 `detect_header_row`。仅有 `_detect_header_row` 调用它

### 5. `_from_config` flag 一致性

`_on_header_row_change`、`_on_tcol_change` 中用户手动修改后未设置对应的 `_from_config` flag，导致 `_refresh_all` 中的 auto-detect 逻辑覆盖用户手动选择。

- `_on_header_row_change`：需加 `self._hrow_from_config = True`，阻止 `_detect_header_row` 覆盖
- `_on_tcol_change`：需加 `self._tcol_from_config = True`，阻止 `_auto_detect` 覆盖模板列

### 6. Sheet 切换后 auto-detect 缓存刷新

`_on_sheet_change` 未重置 `_last_tpl_path`，导致 `_auto_detect` 因缓存命中而跳过新 Sheet 的 headers → template_col 检测。需加 `self._last_tpl_path = ""` 强制重跑。
