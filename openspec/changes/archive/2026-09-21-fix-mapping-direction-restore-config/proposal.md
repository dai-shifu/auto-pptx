## Why

当前映射方向在整条链路中不一致：`suggest_mapping()` 返回 `{placeholder: excel_col}`，但用户心智模型是 "Excel列 → 占位符"。generate() 内部做了翻转，GUI 显示也不符合直觉。同时 config.toml 被删除后，用户无法手动指定模板列和保存映射偏好。

## What Changes

- **BREAKING**: 映射方向统一为 `{excel_col: placeholder}`（Excel列名 → PPT占位符名），全局一致
- `suggest_mapping()` 保持返回 `{placeholder: excel_col}`，在 `detect_and_suggest` 中翻转
- GUI `_auto_mapping` 和 `_rebuild_mapping` 方向改为 `{excel_col: placeholder}`
- GUI 映射显示格式改为 "Excel列 → 占位符"
- `_generate`、`generate()`、`_detect` 均不再翻转映射方向
- 恢复 `src/config.py`：Config 含 `template_column` 和 `mapping`（excel_col→placeholder）
- 恢复 config.toml 自动加载和保存
- 模板列从只读提示改为下拉框，自动检测填充默认值，用户可手动选择

## Capabilities

### New Capabilities

- `mapping-direction`: 映射方向规范 — 全局统一使用 `{excel_col: placeholder}` 方向（Excel列→占位符），所有模块的 mapping 参数和存储均遵循此方向

### Modified Capabilities

- `auto-config`: 模板列从"只读自动检测提示"改为"下拉框手动选择 + 自动检测填充默认值"
- `config-mapping`: config.toml 恢复作为配置持久化机制，支持 `template_column` 和 `[mapping]` 段

## Impact

- `src/config.py` — 恢复（2 字段 Config：template_column + mapping）
- `src/auto_detect.py` — `detect_and_suggest` 中翻转 mapping 方向
- `src/generator.py` — `_detect` 移除翻转逻辑
- `src/gui.py` — 映射方向统一 + 模板列下拉框 + config 加载/保存
- config.toml — 恢复生成
- 测试文件 — 适配新方向
