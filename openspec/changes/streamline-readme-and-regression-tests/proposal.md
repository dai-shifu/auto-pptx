## Why

README 的示例入口和勾选说明重复。非 GUI 回归测试也重复执行相同的生成、配置读取和 Excel 读取场景；合并这些用例可减少维护成本，同时保留关键断言。

## What Changes

- 合并中文 README 中的日报示例入口和生成前勾选说明，保留快速开始所需信息。
- 合并重复的生成用例，明确检查输出页数、顺序、替换内容、模板标记和失败时不写文件。
- 合并配置文件缺失和 Excel 空单元格的重复用例，配置测试只在临时目录写文件。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `reproducible-test-fixtures`：明确共享样本必须验证哪些生成结果和失败分支。应用行为不变。

## Impact

仅修改 `README.md` 和生成、集成、配置、Excel 读取测试。保留 `run.py`、应用代码、工作流、GUI 测试、样本构造器和已提交样本。
