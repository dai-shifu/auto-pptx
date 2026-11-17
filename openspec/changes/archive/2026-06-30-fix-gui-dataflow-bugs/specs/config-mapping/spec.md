## MODIFIED Requirements

### Requirement: 配置持久化

系统 SHALL 在生成完成后将当前 `template_column` 和 `mapping` 写入 `config.toml` 文件，下次启动自动加载。

**变更**: 加载时设置来源标记 `_mapping_from_config` / `_tcol_from_config = True`，`_auto_detect()` 据此区分"来自 config 的持久值"和"来自自动检测的临时值"。仅覆盖后者。

#### Scenario: 保存配置

- **WHEN** 用户在 GUI 中设置模板列为 "标签"，映射为 `{"标题": "title"}`，点击生成
- **THEN** 系统将 `template_column = "标签"` 和 `[mapping]` 段写入 config.toml

#### Scenario: 下次启动映射生效

- **WHEN** config.toml 中存在 `[mapping]` 段，用户下次启动并浏览 Excel/PPT
- **THEN** 映射区显示 config.toml 中保存的映射（`_mapping_from_config=True` 阻止自动检测覆盖）

#### Scenario: 无 config 时切换文件自动检测更新

- **WHEN** 无 config.toml，用户依次浏览两个不同的 PPT（自动检测值不带 `from_config` 标记）
- **THEN** 每次切换文件，`_auto_detect()` 正常覆盖上轮的自动检测结果
