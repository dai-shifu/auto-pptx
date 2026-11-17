## Why

Nuitka `--onefile` 打包后，`__compiled__.containing_dir` 似乎没有正确返回 EXE 所在目录（可能回退到了临时解压目录 `/tmp/_MEI*`），导致：

1. **config.toml 不被创建**：启动时文件不存在就走 `_auto_load_config()` 的 `return` 静默分支，从不自动创建
2. **手动放 config.toml 无效**：生成 PPT 后也没有更新，说明 `save_config()` 写到了别的位置（可能是 temp 目录）
3. **`load_config()` 抛异常**：不在启动时兜底创建，整个加载流程过于脆弱

用户实际测试：EXE 换目录 + 手动创建 config.toml + 生成 PPT，config 仍然不被更新。

## What Changes

- **简化 `_get_config_path()`**：放弃 `__compiled__.containing_dir`，改用 `sys.argv[0].resolve().parent`。开发和打包模式自动适配，不需要区分。
- **`load_config()` 容错**：文件不存在时返回默认 `Config()`，不再抛 `FileNotFoundError`
- **`_auto_load_config()` 加创建逻辑**：启动时如果 config.toml 不存在，写入一份默认配置到磁盘
- **`_generate()` 加目录防御**：`mkdir(parents=True, exist_ok=True)` 保证写入目录一定存在

## Capabilities

### Modified Capabilities

- `config-file-location`: 更新配置文件路径解析逻辑，从 `__compiled__` 改为 `sys.argv[0]`

### New Capabilities

- `config-auto-creation`: 配置文件在缺失时自动生成，不依赖"生成 PPT"操作触发

## Impact

- **Affected code**: `src/config.py` — `load_config()` 容错；新增 `load_or_create_config()`
- **Affected code**: `src/gui.py` — `_get_config_path()` 简化；`_auto_load_config()` 自动创建；`_generate()` 加防御
- **No API/schema changes**: `Config` dataclass 字段不变
- **No dependency changes**
- **No build script changes**
