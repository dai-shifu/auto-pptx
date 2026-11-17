## Context

当前系统为双 Excel 联查架构，用户需准备三个文件（源头 Excel、数据 Excel、模板 PPT）和一份 config.toml。每行按项目编号跨文件查找数据，通过 filler_map 映射填料值到 tpl 名，再通过 mapping 替换占位符。

实际业务中，Excel 模板列的值与 PPT `{{tpl::name}}` 名完全一致，filler_map 是多余的。跨文件查找增加了冗余的 Excel 列（项目编号列）和文件。config.toml 的三个字段（template_column、mapping、filler_map）均可自动检测。

## Goals / Non-Goals

**Goals:**
- 用户只需选择 1 个 PPT 和 1 个 Excel，勾选行，点生成
- 模板列由 `detect_template_column()` 自动检测，映射由 `suggest_mapping()` 自动匹配
- Excel 模板列的值直接等于 `{{tpl::name}}` 名，`"/"` 分割后直接匹配模板
- 可视化行选择替代手动输入起止行号
- 支持同一个 Excel 中有多个 Sheet
- 删除 config.toml 机制和 Config 类

**Non-Goals:**
- 不改变 PPT 引擎（clone_slide / replace_in_slide）逻辑
- 不改变模板匹配（build_template_index / {{tpl::name}} 标识）逻辑
- 不支持跨文件查找（如有需要，后续作为独立功能添加）
- 不增加 filler_map 的 GUI 编辑器（已不需要 filler_map）

## Decisions

### 1. 单 Excel 管线：同行即数据源

**选择**: 将双 Excel 联查简化为单 Excel 逐行处理。选中行的每一行既是迭代驱动（模板列值），也是数据源（mapping 列值）。

**数据流**:
```
Excel (指定 Sheet)
  ↓ read_sheet_rows → (headers, all_rows)
  ↓ 用户勾选 → selected_rows: list[int]
  ↓ 自动检测 template_column, mapping
  ↓
逐行: selected_rows:
    读 filler_raw = row[template_column]
    "/" 分割 → tpl_names
    读 row → 按 mapping 转换为 {placeholder: value}
    每个 tpl_name → clone_slide → replace_in_slide
  ↓
删除原始模板页 → 保存
```

**理由**: 砍掉 `extract_project_ids` 和 `find_row_by_project_id` 两个最复杂的函数调用，管线逻辑减半。项目编号列不再有特殊意义，只是一列普通数据。

**替代方案**: 保留双 Excel 但合并为一个文件两个 Sheet → 仍然需要跨 Sheet 查找，复杂度不减。

### 2. 全自动配置：运行时检测替代 config.toml

**选择**: 删除 `src/config.py` 模块。`template_column` 和 `mapping` 在生成时实时检测。GUI 中 mapping 下拉框保留作为手动覆盖/纠正手段，但不持久化到文件。

**检测时机**:
- PPT 加载后：`build_template_index(prs)` → tpl_names 集合
- Excel 加载后：`_collect_headers_and_rows()` → headers + rows
- 调用 `detect_template_column(headers, rows, tpl_names)` → template_column
- 调用 `suggest_mapping(headers, placeholders)` → mapping

**理由**: 三个字段均可 100% 自动检测。`detect_template_column` 用集合交集比，`suggest_mapping` 用大小写不敏感 + 编辑距离。用户无需理解"模板列"或"映射"概念。

**fallback**: 检测不到时（交集比 0 或无可匹配列），生成时报错提示用户检查模板列的 `/` 分割值是否与 `{{tpl::name}}` 一致。

### 3. "/" 分割直接匹配：删除 filler_map

**选择**: `"/"` 分割后的每个部分直接作为 tpl 名称匹配 `tpl_index`，不经过任何映射表。

```python
def _resolve_tpl_names(filler_raw: str) -> list[str]:
    return [p.strip() for p in filler_raw.split("/") if p.strip()]
```

**理由**: Excel 模板列的值与 PPT `{{tpl::name}}` 名完全一致，不需要翻译层。

### 4. Treeview 行选择

**选择**: 用 `ttk.Treeview` 替换起止行号输入框。展示关键列：行号 + 模板列 + mapping 引用的数据列。每行带复选框。

**Treeview 列定义**:
```
基础列: # (行号, 自动生成)
系统列: template_column (如 "填料")
数据列: mapping 中引用的所有 Excel 列 (如 "分子量", "OD600")
```

**交互**:
- 全选 / 取消全选按钮
- 默认全选（方便最常见场景）
- 生成时传入 `selected_rows: list[int]`

**理由**: 替代手动输入行号，用户直接看到数据后勾选，避免选错行。ttk.Treeview 虚拟渲染，几百行无明显性能问题。

**替代方案**: 保留起止行号 + 新增 Treeview 并存 → 两个选择机制互相冲突。

### 5. 不持久化配置

**选择**: 删除 `save_config()` 和 `load_config()`，不自动保存也不自动加载 config.toml。

**理由**: 配置可自动检测，持久化价值为零。减少文件操作和用户困惑（"这个 config.toml 是哪来的"）。

**例外**: 未计划在本次变更中实现配置保存/加载的替代方案。如后续用户反馈需要"记住上次调整的 mapping"，可在另一 change 中实现。

### 6. Sheet 选择

**选择**: `ttk.Combobox` 下拉列出 Excel 所有 Sheet 名。单 Sheet 自动选中，多 Sheet 用户选择。Sheet 切换时刷新 Treeview 数据。

## Risks / Trade-offs

- **[自动检测不准]** → `detect_template_column` 依赖集合交集，若 Excel 模板列值与 `{{tpl::name}}` 不完全一致（如有多余空格），检测可能失败。缓解：strip 处理、前端报错提示用户手动匹配。
- **[Treeview 大数据量]** → 上千行时 `iter_rows` 加载慢。缓解：openpyxl read_only 模式 + data_only=True，只读不写，性能可接受。500 行以内实测 <1 秒。
- **[删除 config.py 影响]** → 现有代码中有多个 import 引用。缓解：tasks 中逐一清理。
- **[测试适配]** → 现有测试（test_generator.py 等）依赖双 Excel + Config 参数。缓解：同步更新测试。
