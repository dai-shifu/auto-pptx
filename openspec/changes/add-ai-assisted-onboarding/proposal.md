## Why

新用户需要先看懂模板如何选页、数据如何填入占位符，再判断自己的 Excel 和 PPT 能否配合。现有示例可用于演练，但遇到新文件时，用户缺少一份能定位问题、可交给常用 AI 帮忙解读的检查结果。

## What Changes

- 用现有公开样例演示「只选一行，生成一页」，再引导用户检查自己的文件。解释选页和填值是两种不同的关系，并给出可直接复制的 AI 提问示例。
- 在 GUI 增加只读的「检查当前设置」。按模板页和已选 Excel 行解释匹配与映射，区分当前设置、自动建议、需要确认的问题。用户可以预览、编辑并复制精简摘要；程序不自动发送。
- 随入门指南发布可选的轻量 `auto-pptx-onboarding` Skill。它使用同一份规则和公开样例，帮助用户理解摘要并回到 GUI 操作。没有 Skill 也能走完整流程。
- 保留「本机 AI 可直接调用程序」作为后续独立需求。首版不新增 CLI、MCP、AI API、任务文件或第二个 exe。

## Capabilities

### New Capabilities

- `ai-assisted-onboarding`：一页样例入门、可复制的 AI 提问示例和可选引导 Skill。
- `input-compatibility-check`：使用当前 GUI 设置执行只读检查，并提供可预览、可编辑的分享摘要。

### Modified Capabilities

无。现有生成、配置优先级及 GUI 日常操作规则保持不变。

## Impact

影响中英文 README、使用指南、公开 Skill、GUI 和只读检查测试。检查复用 Excel 读取、模板索引、占位符扫描和自动检测规则。无需新增运行依赖，不改 `config.toml` 格式、既有生成行为或 Windows 发布附件结构。
