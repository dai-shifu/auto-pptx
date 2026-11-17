## ADDED Requirements

### Requirement: TOML 配置读取
系统 SHALL 支持从 `config.toml` 文件读取配置，替代原有的 YAML 格式。

#### Scenario: 读取有效 TOML 配置
- **WHEN** config.toml 包含 `template_column` 和 `[mapping]` 节
- **THEN** 系统成功加载并返回 Config 对象

#### Scenario: TOML 语法错误
- **WHEN** config.toml 格式不符 TOML 规范
- **THEN** 系统抛出 ValueError 并提示具体错误信息

#### Scenario: 缺少必填字段
- **WHEN** config.toml 缺少 `template_column` 或 `[mapping]` 节
- **THEN** 系统抛出 ValueError 并提示缺少哪个字段

### Requirement: TOML 配置写入
系统 SHALL 支持将当前配置写入 `config.toml` 文件。

#### Scenario: 保存配置
- **WHEN** 用户配置好映射关系
- **THEN** 系统将 `template_column` 和 `mapping` 写入 config.toml
- **THEN** 文件符合 TOML 规范，可直接用文本编辑器打开修改
