# 参与贡献

欢迎在 GitHub 提交 Issue 和 PR。反馈问题时，提供版本、复现步骤、预期结果和实际结果。示例使用合成或脱敏数据。

## 准备环境

macOS、Linux 和 Windows 均可从源码运行。需要 Python 3.11+、uv 和可用的 tkinter。CI 使用 Python 3.12；Windows 命令示例使用 Git Bash。源码开发不需要 Windows 打包工具链。

克隆自己的 fork 后，在项目根目录运行：

```bash
uv sync --locked --group dev
uv run run.py
```

首次启动会尝试在项目根目录创建空的 `config.toml`，请勿提交。Linux 需安装 Tk；无桌面环境运行 GUI 测试还需 Xvfb 和 xauth。

## 修改与测试

保持改动集中。沿用四空格缩进、公开接口类型注解和 `pathlib.Path`。避免顺带重构或调整无关格式。

开发时先运行相关测试，例如：

```bash
uv run --group dev pytest tests/test_generator.py
```

提交前运行全量测试。使用 `--require-gui`，让 Tk 不可用时的必要 GUI 测试报错而不是跳过：

```bash
uv run --group dev pytest --require-gui
```

Linux 无桌面时，在命令前加 `xvfb-run -a`；Windows 加 `--capture=sys`。GUI 用例跳过不算通过，请在 PR 中注明未验证的部分。模块与构建方法见[开发文档](docs/开发.md)。

## 规格与测试资源

[现行规格](openspec/specs/)记录功能约束，[活动变更](openspec/changes/)记录提案、设计和任务，[归档](openspec/changes/archive/)保留历史决策。确认当前行为时，对照代码和已实现的活动变更。

较大的行为变更先讨论范围，并同步更新提案、设计、规格和任务。简单修正可直接提交 PR，说明影响和验证结果。

测试输出写入临时目录。用 `tests/create_fixtures.py` 构造测试资源；资源格式变更时，同步提交二进制文件。修改展示示例时，同步脚本、模板、数据、成品和预览，见[示例说明](examples/bio-daily/README.md)。分发数据和图片须为合成或可公开内容。

## 提交 PR

使用简短明确的标题，如 `fix: preserve row selection`。说明用户可见的变化、关联 Issue 或 OpenSpec 变更，以及验证命令和结果。

GUI 修改附截图。生成行为修改说明合成输入、输出页数和警告。注明配置格式或测试资源是否变化。分支与 PR 会静态检查所有 workflow，并在 Linux 和 Windows 运行完整源码测试。
