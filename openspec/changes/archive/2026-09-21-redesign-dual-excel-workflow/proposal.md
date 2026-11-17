## Why

归档说明：本文仅保留旧双 Excel 方案的历史背景，该方案已被单 Excel 工作流替代。本变更下的六份旧增量规格已按公开前复核结果移除；当前需求以 `openspec/specs/` 为准。

批量生成业务需要双Excel联查工作流（源头Excel→模板选择+项目编号，数据Excel→填充数据），单Excel管线不适用。需要移除旧的单Excel管线，将批量生成工作流从"附加功能"升级为应用核心。

## What Changes

- **BREAKING** 移除单Excel管线: 删除 `src/generator.py`（旧的单Excel批量生成管线）
- **BREAKING** 移除 `src/sheet_routing.py`: Sheet→模板组路由改为由填料值直接匹配模板
- **BREAKING** 移除 `src/filler_mapping.py`: 填料到模板的映射改为在 `config.toml` 中配置
- 重写 `src/config.py`: 新增 `project_id_column`、`filler_map`、`data_header_row` 字段
- 重写 `src/generator.py`: 支持 `"/"` 分割填料值生成多个 Slide、可配置 `filler_map`
- 重写 GUI 为单一双Excel工作流界面，移除旧的单Excel区域和txt行号加载
- 简化 CLI: 默认启动 GUI

## Capabilities

### New Capabilities

- `dual-excel-pipeline`: 双Excel联查生成管线 — 源头Excel读取项目编号和模板列，数据Excel按项目编号匹配行数据并替换占位符
- `filler-config`: 填料可配置映射 — 填料值到模板名称的映射在 `config.toml` `[filler_map]` 段中定义
- `template-column-config`: 模板列可配置 — 源头Excel中用于匹配 `{{tpl::}}` 标识的列名可配置
- `multi-slide-generation`: 多Slide生成 — 填料值含 `"/"` 时分别匹配模板并生成多个Slide，共享同一行填充数据

### Modified Capabilities

- `config-mapping`: 新增 `project_id_column`、`filler_map`、`data_header_row` 字段，移除 `template_column` 的旧语义
- `excel-reading`: 新增按指定标题行读取数据Excel、`find_row_by_project_id` 的 `header_row` 可配置

## Impact

- `src/generator.py` — 删除
- `src/sheet_routing.py` — 删除
- `src/filler_mapping.py` — 删除
- `src/config.py` — 重写
- `src/generator.py` — 重写
- `src/gui.py` — 重写
- `src/excel_reader.py` — `find_row_by_project_id` 的 `header_row` 改为可配置
- `src/main.py` — CLI 简化，移除单Excel管线引用
