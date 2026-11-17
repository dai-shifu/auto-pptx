## Why

config.toml 的 `[mapping]` 写入后下次启动不生效，因为 `_auto_detect()` 无条件地将 `_auto_mapping` 覆盖为自动检测结果。同时还有配置静默加载失败、切换模板列/Sheet 后勾选丢失等问题，导致用户对配置系统的信任崩溃。

## What Changes

- **_auto_detect() 来源标记**: 用 `_mapping_from_config` / `_tcol_from_config` 标记区分"来自 config.toml 的持久值"和"来自自动检测的临时值"。`_auto_detect()` 仅覆盖后者，解决旧 `if not self._auto_mapping:` 守卫导致的 one-shot 冻结问题（换文件后映射和模板列不更新）
- **配置加载显式反馈**: `_auto_load_config()` 不再吞掉异常，加载成功/失败均通过状态栏告知用户
- **切换模板列时保留勾选 + 默认全不选**: `_rebuild_treeview()` 分场景处理 — 首次加载和 Sheet 变化时默认为全不选（☐），仅模板列变化时保留现有勾选状态。点击事件改用 `<Button-1>` 避免漂移，并 `return "break"` 阻止 Treeview 默认选中行为
- **消除重复的占位符收集代码**: GUI 复用 `auto_detect._collect_placeholders`，删除 `App._collect_placeholders_from_ppt`
- **config.toml 路径固定**: 使用脚本所在目录而非进程工作目录，换目录启动也能找到
- **空映射传参修复**: `_generate()` 中空映射 `{}` 不再转为 `None`，避免触发 `generate()` 内部重新自动检测覆盖用户意图

## Capabilities

### New Capabilities
- `config-persistence`: config.toml 中 `[mapping]` 真正持久化 — 加载后不被 auto_detect 覆盖，加载失败有用户可见的错误提示，配置路径与 CWD 无关
- `selection-preservation`: 首次加载和切换 Sheet 默认为全不选；切换模板列时保留 Treeview 行勾选状态；点击事件使用 `<Button-1>` 避免漂移

### Modified Capabilities
- `config-mapping`: config.toml 的 `[mapping]` 在运行时不再被 auto_detect 无条件覆盖

## Impact

- `src/gui.py` — 主要修改：`_auto_detect`、`_auto_load_config`、`_rebuild_treeview`、`_generate`、删除 `_collect_placeholders_from_ppt`、`CONFIG_PATH`
- `src/auto_detect.py` — `_collect_placeholders` 改为公开函数供 GUI 复用（或通过 `detect_and_suggest` 返回）
- `CONFIG_PATH` 常量 — 从 `Path("config.toml")` 改为 `Path(__file__).resolve().parent.parent / "config.toml"`（项目根目录）
