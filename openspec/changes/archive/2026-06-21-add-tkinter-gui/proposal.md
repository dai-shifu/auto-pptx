## Why

当前工具仅支持命令行操作，业务用户（非技术人员）难以使用。需要提供一个极简的图形界面，用户只需选择 Excel 文件，点击按钮即可完成 PPT 生成。

## What Changes

- 新增 tkinter GUI 入口：文件选择 + 映射配置 + 一键生成，~60 行
- 新增自动检测逻辑：上传模板和 Excel 后自动识别模板列和列→占位符映射
- 配置格式从 YAML 迁移为 TOML：Python 3.11+ 自带 tomllib 读取，更易手写
- **BREAKING**: `config.yaml` 不再支持，改为 `config.toml`

## Capabilities

### New Capabilities

- `tkinter-gui`: 基于 tkinter 的图形界面，包含文件浏览、映射下拉框、生成按钮和状态提示
- `auto-detect`: 上传模板 PPT 和 Excel 后自动检测模板列（集合交集匹配）和列→占位符映射建议（大小写不敏感、编辑距离）
- `config-toml`: 配置持久化为 TOML 格式，支持自动保存和加载

### Modified Capabilities

<!-- 无现有 spec 需要修改 -->
（无）

## Impact

- **新增文件**: `src/gui.py`（tkinter 窗口）、`src/auto_detect.py`（自动检测逻辑）
- **修改文件**: `src/config.py`（YAML → TOML）、`src/main.py`（新增 gui 入口）、`build.py`（打包新入口）
- **无新增依赖**：tkinter 为 Python 标准库，tomllib 为 Python 3.11+ 标准库
- **用户交互变更**：从命令行变为图形窗口，双击 exe 即可使用
