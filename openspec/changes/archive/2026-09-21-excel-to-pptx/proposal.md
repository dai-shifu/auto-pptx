## Why

归档说明：本文保留最初方案的历史背景，其中的 YAML 配置及原地替换策略已被后续方案替代。旧 YAML 映射增量规格已按公开前复核结果移除；当前需求以 `openspec/specs/` 为准。

需要一个工具将 Excel 表格中的结构化数据批量填充到 PowerPoint 模板中，自动生成多页 PPT。目前没有现成工具能支持"一个 Excel 多行数据 + 一个 PPT 模板(含多种布局) → 一个多页 PPT"的场景。

## What Changes

- 新增 Excel 读取模块：支持 `.xlsx` 文件读取，每行作为一条独立记录
- 新增 PPT 模板引擎：整文件加载模板，原地替换文本框和表格单元格中的占位符（`{{xxx}}` 格式），删除未使用的模板页
- 新增模板匹配机制：模板 PPT 中通过隐藏标识占位符（`{{tpl::名称}}`）标识每页模板身份，Excel 中通过标记列指定使用哪个模板
- 新增映射配置：通过 `config.yaml` 定义 Excel 列名到 PPT 占位符的映射关系
- 支持多个模板布局共存于同一个模板 PPT 文件中
- 输出为单个 PPT 文件，按模板原始顺序排列
- 支持打包为独立可执行文件

## Capabilities

### New Capabilities

- `excel-reading`: 从 `.xlsx` 文件读取数据，支持 openpyxl 引擎，处理中文表头，返回结构化行数据
- `pptx-template-engine`: 整文件加载模板，原地替换文本框和表格单元格中的 `{{xxx}}` 占位符为实际数据，保留模板中的图片、样式、排版，删除未使用的模板页
- `template-matching`: 通过 `{{tpl::名称}}` 标识占位符识别模板页身份，建立模板索引，支持 O(1) 查找
- `config-mapping`: 通过 `config.yaml` 定义 Excel 列名 → 占位符名的映射、模板标记列名（该列值直接对应 `{{tpl::名称}}` 标识）
- `batch-generation`: 遍历 Excel 所有行，逐行匹配模板、原地替换占位符，删除未用模板页，按模板原始顺序输出到单个 PPT 文件

### Modified Capabilities

（无，这是全新项目）

## Impact

- **新增依赖**: openpyxl, python-pptx, PyYAML
- **文件结构**: 新增 `src/` 目录（main.py, excel_reader.py, pptx_engine.py, config.py）
- **用户交互**: 用户需准备三份输入文件（模板 PPT、数据 Excel、config.yaml）
- **打包**: 使用 Nuitka 编译为独立可执行文件
