## Why

当前系统使用双 Excel 联查（源头 Excel + 数据 Excel）+ config.toml 配置驱动，用户需要准备三个文件、填写配置、输入起止行号，操作繁琐。实际业务中，Excel 模板列的值与 PPT `{{tpl::name}}` 名完全一致，filler_map 是多余的。简化后用户只需选择 PPT 和 Excel，勾选行，点生成。

## What Changes

- **BREAKING**: 移除双 Excel 联查架构，源头 Excel + 数据 Excel → 单个 Excel
- **BREAKING**: 删除 `config.toml` 机制，`template_column` 由 `detect_template_column()` 自动检测，`mapping` 由 `suggest_mapping()` 自动匹配
- **BREAKING**: 删除 `filler_map`，Excel 模板列的值直接等于 `{{tpl::name}}` 名，`"/"` 分割后直接匹配
- **BREAKING**: 删除 `src/config.py` 模块（Config dataclass、load_config、save_config）
- **BREAKING**: 删除 `project_id_column`、`data_header_row` 等跨文件查找概念
- 行选择从"手动输入起止行号"改为 `ttk.Treeview` 可视化预览 + 勾选
- Sheet 选择：单 Sheet 自动使用，多 Sheet 时用户选择
- `_resolve_tpl_names` 简化为一行 `split("/")`
- `generate()` 签名从 8 参数精简到 5 参数

## Capabilities

### New Capabilities

- `single-excel-pipeline`: 单 Excel 管线 — 用户选择一个 Excel 文件，勾选行后直接从该行读取模板列和数据列生成 PPT
- `visual-row-selection`: 可视化行选择 — ttk.Treeview 展示关键列（行号 + 模板列 + 映射列），用户通过复选框勾选要生成的行
- `auto-config`: 全自动配置 — 模板列和映射在运行时自动检测，无需用户编写配置文件

### Modified Capabilities

- `batch-generation`: 管线从"双 Excel 联查"改为"单 Excel 逐行"，移除 `extract_project_ids` 和 `find_row_by_project_id` 调用，标题行固定第 1 行
- `template-matching`: filler_map 移除后，`"/"` 分割值直接作为 tpl 名称匹配 `{{tpl::name}}`
- `config-mapping`: config.toml 机制整体删除，映射由 `auto_detect.py` 自动完成

## Impact

- `src/config.py` — 删除
- `src/generator.py` — 重写（单 Excel 管线，约 80 行）
- `src/gui.py` — 重写（Treeview + Sheet 选择 + 移除 config 相关调用）
- `src/excel_reader.py` — 新增 `read_sheet_rows()`，保留旧函数不动
- `src/auto_detect.py` — 小幅适配
- `src/main.py` — 不变
- `src/pptx_engine.py` — 不变
- `src/template_matching.py` — 不变
- `config.toml` — 从仓库移除
