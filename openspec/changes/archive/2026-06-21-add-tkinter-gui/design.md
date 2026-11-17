## Context

当前 auto-pptx 是纯 CLI 工具，用户需在命令行输入参数 + 手写 YAML 配置。目标用户是业务人员（非技术背景），需要极简图形界面。目标是 ~60 行代码，零新增依赖。

## Goals / Non-Goals

**Goals:**
- 提供 tkinter 图形窗口，用户选择 Excel 文件即可生成 PPT
- 模板路径和映射关系持久化在 `config.toml`，首次配置后无需重复
- 自动检测模板列和列→占位符映射，减少用户配置负担
- 零新增第三方依赖（tkinter + tomllib 均为标准库）

**Non-Goals:**
- 不支持预览、拖拽、多步骤向导
- 不做跨平台 UI 美化（tkinter 原生控件即可）
- 不重写现有 src/ 核心逻辑

## Decisions

### 映射关系不展示在 UI 中，改为首次自动检测 + config.toml 持久化

日常使用流程：选 Excel → 点生成。config.toml 已在同目录，模板路径和映射都写好了。

首次使用流程：UI 打开时检测 config.toml 不存在 → 提示用户选择模板和 Excel → 自动检测模板列和映射 → 保存 config.toml → 此后只需选 Excel。

这样 UI 始终只暴露一个文件选择框 + 一个按钮，最大化简化。

### 配置格式: YAML → TOML

Python 3.11+ 自带 `tomllib` 读取，写入用简单的字符串拼接（dict 深度 1 层，无需第三方库）。TOML 无缩进要求，非技术用户用记事本改也不容易出错。

### tkinter 文件对话框

`filedialog.askopenfilename()` 弹出系统原生文件选择器，用户无需手动输入路径。

### 入口分离

`src/main.py` 保持 CLI 入口不变，新增 `src/gui.py` 作为 GUI 入口。`build.py` 和 `run.py` 新增对应的启动方式。

## Risks / Trade-offs

- [Risk] tkinter 在部分 Linux 环境未默认安装 → Mitigation: 打包时 Nuitka 将 tkinter 静态链接
- [Risk] 自动检测可能匹配不准（列名和占位符名差异大） → Mitigation: 检测失败时弹出提示，引导用户手动编辑 config.toml
- [Trade-off] GUI 入口和 CLI 入口并存,增加维护面 → 可接受,两者共用 src/ 核心逻辑
