## ADDED Requirements

### Requirement: 运行时映射优先级

系统 SHALL 在运行时按以下优先级确定映射和模板列: **用户手动调整 > config.toml 加载值 > 自动检测结果**。

实现方式: 当 `_auto_load_config()` 从 config.toml 读入 `mapping` 或 `template_column` 时，SHALL 设置对应的来源标记（`_mapping_from_config = True` / `_tcol_from_config = True`）。`_auto_detect()` 仅当来源标记为 `False` 时才覆盖对应值，从而允许同一个 session 内切换文件时自动检测替换上轮自动检测的旧值，但永不覆盖 config 加载的持久值。

#### Scenario: config 映射不会被 auto_detect 覆盖

- **WHEN** config.toml 中 `[mapping]` 定义了 `{"标题": "title"}`，用户浏览到 Excel 和 PPT
- **THEN** `_auto_detect()` 执行后 `_auto_mapping` 仍保留 `{"标题": "title"}`（`_mapping_from_config=True` 阻止覆盖）

#### Scenario: 无 config 时自动检测填充

- **WHEN** 没有 config.toml 或 `[mapping]` 为空，用户浏览到 Excel 和 PPT
- **THEN** `_auto_detect()` 用自动检测结果填充 `_auto_mapping`（`_mapping_from_config=False` 允许覆盖）

#### Scenario: 无 config 时切换文件自动检测更新

- **WHEN** 没有 config.toml，用户先浏览 PPT-A + Excel-A（自动检测填入映射 A），再切换到 PPT-B + Excel-B
- **THEN** `_auto_detect()` 用 PPT-B 的检测结果覆盖映射 A（`_mapping_from_config=False` 允许覆盖）

#### Scenario: config 加载的模板列不被 auto_detect 覆盖

- **WHEN** config.toml 中 `template_column = "标签"`，用户浏览到 PPT（自动检测到模板列为 "填料"）
- **THEN** `tcol_var` 保持 "标签"（`_tcol_from_config=True` 阻止覆盖）

#### Scenario: 无 config 时切换文件模板列自动检测更新

- **WHEN** 没有 config.toml，用户先浏览 PPT-A + Excel-A（检测到模板列 A），再切换到 PPT-B + Excel-B
- **THEN** `tcol_var` 更新为 PPT-B 的自动检测结果

### Requirement: 配置加载显式反馈

`_auto_load_config()` SHALL 在加载成功或失败时通过状态栏（`status_var`）告知用户。

#### Scenario: 加载成功

- **WHEN** config.toml 存在且格式正确
- **THEN** 状态栏显示 "已从 config.toml 加载配置"，`_auto_mapping` 和 `tcol_var` 更新为配置文件中的值，同时 `_mapping_from_config` 和 `_tcol_from_config` 设为 `True`

#### Scenario: 加载失败

- **WHEN** config.toml 存在但格式错误（如 TOML 语法错误）
- **THEN** 状态栏显示 "配置加载失败: <具体错误>"，异常不再被静默吞掉

### Requirement: 配置路径独立于 CWD

`CONFIG_PATH` SHALL 基于脚本所在目录解析，而非进程当前工作目录。

#### Scenario: 换目录启动仍找到配置

- **WHEN** 用户在 `/home/user/` 启动 `python /opt/auto-pptx/run.py gui`，且 `/opt/auto-pptx/config.toml` 存在
- **THEN** 系统加载 `/opt/auto-pptx/config.toml`，而非 `/home/user/config.toml`

### Requirement: 空映射传参不触发重新检测

`_generate()` 在构建映射后 SHALL 将映射原样传递给 `generate()`，包括空字典 `{}`。空映射 `{}` MUST 不转换为 `None`。

#### Scenario: 用户全选"(不映射)"后生成

- **WHEN** 用户在映射区将所有列选为 "(不映射)"，点击生成
- **THEN** `generate()` 收到 `mapping={}`，不触发内部自动检测覆盖用户意图
