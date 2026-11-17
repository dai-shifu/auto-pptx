## Context

当前映射方向在整条链路中有多层翻转：
```
suggest_mapping → {placeholder: excel_col}
detect_and_suggest → 直接透传 {placeholder: excel_col}
GUI _auto_mapping → {placeholder: excel_col}
GUI _rebuild_mapping → 遍历 placeholder 作为 key
GUI _generate → 再次翻转成 {excel_col: placeholder}
generate / _detect → 又翻转一次 {excel_col: placeholder}
```

导致：
1. 用户看到的映射顺序是"占位符→Excel列"，与心智模型相反
2. 全局有两处翻转逻辑，容易出错
3. config.toml 被误删，用户无法手动指定模板列

## Goals / Non-Goals

**Goals:**
- 全局统一映射方向为 `{excel_col: placeholder}`（Excel列→占位符）
- 翻转点集中在一处（`detect_and_suggest` 内部），其余模块直接使用
- GUI 映射显示改为 "Excel列 → 占位符"
- 恢复 config.toml 自动加载/保存
- 模板列改为下拉框，自动检测填充默认值但允许手动选择

**Non-Goals:**
- 不恢复 filler_map、project_id_column、data_header_row
- 不改变 `suggest_mapping` 的签名（调用处太多）

## Decisions

### 1. 翻转点：集中在 `detect_and_suggest`

**选择**: `suggest_mapping()` 内部逻辑不变（`{placeholder: excel_col | None}`），但 `detect_and_suggest()` 返回前翻转方向：

```python
def detect_and_suggest(prs, headers, rows):
    tpl_col = ...
    mapping_suggest = suggest_mapping(headers, placeholders)
    # 翻转方向
    mapping = {}
    for ph, col in mapping_suggest.items():
        if col is not None:
            mapping[col] = ph
    return tpl_col, mapping  # {excel_col: placeholder}
```

**理由**: `suggest_mapping` 的调用方不止一处（还有 auto_detect 测试），不改其签名可减少改动波及面。

### 2. GUI `_auto_mapping` 方向

**选择**: 存储 `{excel_col: placeholder}`，与 `detect_and_suggest` 返回一致。

### 3. GUI 映射显示

**选择**: 显示为 `Excel列 → 占位符`：
```
── 映射配置 ──
  标题  →  title
  作者  →  author
  OD600 →  od
```

遍历 `_auto_mapping` 的 key（excel_col），value 是 placeholder。下拉框选择映射到哪个占位符。

### 4. Config 类恢复

```python
@dataclass
class Config:
    template_column: str = "填料"
    mapping: dict[str, str] = field(default_factory=dict)  # excel_col → placeholder
```

只有 2 字段，不恢复 filler_map 等已删除字段。

### 5. config.toml 加载/保存

**加载**: GUI 启动时检查 `config.toml`，存在则加载 `template_column` 和 `[mapping]`。
**保存**: 生成按钮点击后自动保存当前的 `template_column` 和 `mapping`。

### 6. 模板列下拉框

**选择**: 将模板列从只读 Label 改为 `ttk.Combobox`，值来自 Excel headers。自动检测结果填充为默认值，用户可手动切换。

**理由**: 用户需要指定用哪一列做 `"/"` 分割匹配模板，自动检测可能不准。

### 7. 映射参数变化

```python
# generate() 签名不变
def generate(prs, excel_path, sheet_name, selected_rows, output_path):
    # 内部 _detect 返回的 mapping 已经是 {excel_col: placeholder}
    # 不再翻转
```

```python
# GUI _generate 不再翻转
def _generate(self):
    mapping = {}
    for excel_col, var in self.mapping_widgets:
        val = var.get()
        if val and val != "(不映射)":
            mapping[excel_col] = val  # 不再翻转
```

## Risks / Trade-offs

- **[config.toml 迁移]** → 之前删除 config.toml 后用户没有此文件。缓解：首次启动自动生成默认 config.toml。
- **[mapping 方向混乱遗留]** → 其他未改的代码可能仍用旧方向。缓解：全局搜索 `mapping\[` 使用处逐一验证。
