## Context

当前方案（`__compiled__.containing_dir`）在实际 onefile 测试中失败——EXE 启动后 config.toml 既不被创建也不被更新。Nuitka 4.1.2 源码分析显示 `getContainingDirectoryObject()` 依赖环境变量 `NUITKA_ONEFILE_DIRECTORY`，在 `--disable-console` 模式下可能未被正确设置，回退到 `getPythonProgramDirectoryObject()` → 指向临时解压目录而非 EXE 目录。

核心洞察：这是一个 **GUI 双击启动**的应用，`sys.argv[0]` 足以提供最可靠的 EXE 路径，不需要任何 Nuitka 内部机制。

## Goals / Non-Goals

**Goals:**
- onefile exe 运行时，`config.toml` 读写于 exe 同目录
- 开发模式下（`python run.py gui`），行为不变（项目根目录）
- 配置缺失时自动生成默认配置，不依赖"生成 PPT"操作
- 方案极简：一行路径解析，零 Nuitka 内部依赖

**Non-Goals:**
- 不修改配置文件的读写时机（启动加载 + 生成保存，保持不变）
- 不修改 `Config` dataclass 字段定义
- 不修改构建脚本

## Decisions

### 采用 `sys.argv[0].resolve().parent`

```python
def _get_config_path() -> Path:
    return Path(sys.argv[0]).resolve().parent / "config.toml"
```

**为什么它能工作**：

| 场景 | sys.argv[0] | resolve().parent | 结果 |
|------|-------------|------------------|------|
| `python run.py gui` | `run.py` | 项目根目录 | ✅ 项目根/config.toml |
| `./dist/auto-pptx` | `./dist/auto-pptx` | exe 所在目录 | ✅ dist/config.toml |
| 双击 EXE | `C:\app\auto-pptx.exe` | exe 所在目录 | ✅ 同目录/config.toml |

Nuitka onefile 的 bootstrap 代码保留 `sys.argv[0]` 为原始 EXE 路径，不会改成 temp 目录。

**为什么不被"PATH 执行"影响**：这是一个 GUI 应用，用户通过双击或文件管理器使用，不会出现 `cd /tmp && auto-pptx` 这种场景。即使出现，配置落在 CWD 也不算错。

### `load_config()` 容错：不存在时返回默认值

```python
def load_config(path: str | Path) -> Config:
    path = Path(path)
    if not path.exists():
        return Config()   # 不再抛异常，返回默认值
    ...
```

`Config` 的 dataclass 默认值（`template_column="填料"`, `header_row=1`, `mapping={}`）就是合理的初始状态。

### 启动时自动创建 config.toml

`_auto_load_config()` 在加载后立即调用 `save_config()` 写入磁盘——保证不管有没有点过"生成 PPT"，文件都在那里。用户可以直接编辑它。

```
_auto_load_config():
    config = load_config(CONFIG_PATH)   # 不存在也返回默认值
    if not CONFIG_PATH.exists():
        save_config(config, CONFIG_PATH) # 首次启动时写入
    # ... 恢复 GUI 状态
```

### `_generate()` 加目录防御

```python
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
save_config(config, CONFIG_PATH)
```

防止极端情况（比如目录被外部删除）下的写入失败。

## Risks / Trade-offs

- **[Risk] EXE 放在只读目录**（如 `C:\Program Files\`）→ `save_config()` 抛 `PermissionError`，被 `except` 捕获，GUI 仍正常使用（内存中的默认值），只是持久化失败
- **[Risk] `sys.argv[0]` 被篡改** → 仅在 `subprocess.Popen(args=...)` 启动时可能，正常使用不会发生
