# 参与贡献

欢迎在 GitHub 提交 Issue 和 PR。反馈问题时，提供版本、复现步骤、预期结果和实际结果。示例使用合成或脱敏数据。

## 准备环境

macOS、Linux 和 Windows 开发者均直接从源码运行和测试，需要 Python 3.11+、uv 和可用的 tkinter。CI 和 Windows 发布构建使用 Python 3.12。Windows 命令在 Git Bash 中执行。正式 Windows exe 由 Windows CI 构建，也可在 Windows 上本地试打包。日常开发无需安装 Visual Studio 或 Build Tools。

克隆自己的 fork 后，在项目根目录运行：

```bash
uv sync --locked --group dev
uv run run.py
```

首次启动会创建 `config.toml`，请勿提交。Linux 需安装 Tk；无桌面环境运行 GUI 测试还需 Xvfb 和 xauth。

## 修改与测试

保持改动集中。沿用四空格缩进、公开接口类型注解和 `pathlib.Path`。避免顺带重构或调整无关格式。

先运行相关测试，提交前运行完整测试：

```bash
uv run --group dev pytest tests/test_generator.py
uv run --group dev pytest
```

Linux 无桌面环境时运行：

```bash
xvfb-run -a uv run --group dev pytest
```

GUI 测试跳过不代表验证通过。请在 PR 中说明未验证的部分。模块与构建方法见[开发文档](docs/开发.md)。

## 文档写作

所有项目文档参考 Scott Adams 的《The Day You Became A Better Writer》：

- 先写结论、用途或操作，再补必要背景。
- 使用短句和常用词。一句话说明一件事。
- 用主动表达，写清谁做什么。删除空话、重复说明和多余修饰。
- 步骤按操作顺序写；并列信息用列表，需要比较时用表格。
- 保留必要条件、例外、命令和示例。规格保留约束强度，历史记录保留当时的决策和验证结果。

此约定适用于中英文 README、指南、示例、协作说明，以及 OpenSpec 提案、设计、规格、任务和验证记录。

新写或因需求修改文档时遵循此约定。不为统一文风单独改写已有规格或历史记录。

## 规格与测试资源

[现行规格](openspec/specs/)记录功能约束，[活动变更](openspec/changes/)记录提案、设计和任务，`changes/archive/` 保留历史决策。历史记录与当前行为不一致时，核对现行规格、代码和活动变更。

较大的行为变更先讨论范围，并同步更新提案、设计、规格和任务。简单修正可直接提交 PR，说明影响和验证结果。

测试输出写入临时目录。用 `tests/create_fixtures.py` 构造测试资源；资源格式变更时，同步提交二进制文件。修改展示示例时，同步脚本、模板、数据、成品和预览，见[示例说明](examples/bio-daily/README.md)。分发数据和图片须为合成或可公开内容。

## 提交 PR

使用简短明确的标题，如 `fix: preserve row selection`。说明用户可见的变化、关联 Issue 或 OpenSpec 变更，以及验证命令和结果。

GUI 修改附截图。生成行为修改说明合成输入、输出页数和警告。注明配置格式或测试资源是否变化。分支与 PR 会静态检查所有 workflow，并在 Linux 和 Windows 运行完整源码测试。
