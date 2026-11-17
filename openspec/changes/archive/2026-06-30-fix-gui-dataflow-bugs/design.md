## Context

当前 gui.py 中存在 6 个数据流 bug，它们相互叠加导致 config.toml 的 `[mapping]` 段形同虚设。上一个 change（`fix-mapping-direction-restore-config`）恢复了 config.toml 的保存和加载机制，但 `_auto_detect()` 在每次 `_refresh_all()` 中无条件覆盖 `_auto_mapping`，使得加载的值立即被丢弃。

其他 bug（B2-B6）进一步恶化了用户体验：加载失败静默吞掉、切换模板列丢勾选、CWD 相关路径、空映射边缘情况、重复代码。

所有修改集中在 `src/gui.py`，不涉及数据模型变更或外部依赖。

## Goals / Non-Goals

**Goals:**
- 修复 config.toml `[mapping]` 在运行时被覆盖的核心 bug (B1)
- 提供配置加载成功/失败的用户可见反馈 (B2)
- 消除 `_collect_placeholders` 重复代码 (B3)
- 切换模板列时保留 Treeview 勾选状态 (B4)
- 使用文件系统绝对路径替代 CWD 相对路径 (B5)
- 空映射 `{}` 原样传递，不转为 `None` (B6)

**Non-Goals:**
- 不改变 config.toml 的文件格式
- 不改变 `generate()` / `detect_and_suggest()` 的 API
- 不增加新的外部依赖
- 不改动 `src/config.py`

## Decisions

### D1: 映射优先级 — 来源标记 (改)

**旧方案（已废弃）**: `if not self._auto_mapping:` 守卫，仅在映射为空时填充自动检测结果。

**废弃理由**: 无法区分"config 加载的空字典"和"尚未自动检测的空字典"；更严重的是，一旦自动检测填入了值，该值就被永久冻结，切换文件后无法被新自动检测结果覆盖。

**新方案**: 来源标记 — 给 `_auto_mapping` 和 `tcol_var` 配布尔 flag 记录"是否来自 config.toml"。

```python
# __init__
self._mapping_from_config = False
self._tcol_from_config = False

# _auto_load_config — 设值同时打标
if config.mapping:
    self._auto_mapping = config.mapping
    self._mapping_from_config = True
if config.template_column:
    self.tcol_var.set(config.template_column)
    self._tcol_from_config = True

# _auto_detect — 仅覆盖"非 config 来源"的值
if not self._mapping_from_config:
    self._auto_mapping = mapping
if not self._tcol_from_config and template_col:
    self.tcol_var.set(template_col)
```

**行为矩阵**:

| `from_config` | 当前值来源 | 换文件时 | 原因 |
|---|---|---|---|
| `True` | config.toml | 不覆盖 | 用户持久化偏好优先 |
| `False` | 自动检测 | 覆盖 | 自动检测值可过期 |

**替代方案 B**: 文件指纹比对 — 记录上次自动检测的文件路径，路径变了就覆盖。**拒绝理由**: 切回旧文件会重新检测丢失用户微调；config 值需要特殊处理。

**替代方案 C**: config 只做种子，auto_detect 永远覆盖。**拒绝理由**: spec 要求 config > auto_detect，此方案违背优先级链。

### D2: 复用 auto_detect._collect_placeholders

`auto_detect._collect_placeholders` 改为公开函数（去掉下划线前缀），GUI 直接 `from .auto_detect import collect_placeholders` 调用。删除 `App._collect_placeholders_from_ppt`。

**替代方案**: 让 `detect_and_suggest` 返回第三个元素（placeholder list）。**拒绝理由**: 改变现有 API，增加调用方适配成本。

### D3: _rebuild_treeview 添加 preserve_checks 参数

`_rebuild_treeview(preserve_checks=False)`:
- `preserve_checks=False`（默认）: 清空 `_checked` 再全部添加（现有行为）
- `preserve_checks=True`: 仅更新 Treeview 结构，不清空 `_checked`

调用方:
- `_refresh_all()` → `_rebuild_treeview(preserve_checks=False)` — 数据变了，全选合理
- `_on_tcol_change()` → `_rebuild_treeview(preserve_checks=True)` — 数据没变，保留勾选

**替代方案**: 在 `_rebuild_treeview` 内部判断调用来源。**拒绝理由**: 隐式逻辑难以推理。

### D4: CONFIG_PATH 改为文件系统路径

```python
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"
```

`__file__` 指向 `src/gui.py`，`.parent.parent` 指向项目根目录。

**替代方案**: 用户配置目录 `~/.config/auto-pptx/config.toml`。**拒绝理由**: 当前 config 本质是"项目级"（与脚本同目录），与用户名无关。

### D5: 空映射传参修复

```python
# Before: mapping=mapping if mapping else None  (BUG: {} → None)
# After:  mapping=mapping or None
```

`or` 在空字典时保持 `{}`（falsy），但这里我们想要的是：**永远传递 mapping 本身，不转换为 None**。`generate()` 已经有了 `if mapping is None: auto_detect` 的逻辑，空映射 `{}` 表示"没有映射任何占位符"的用户意图，不应触发重新检测。

## Risks / Trade-offs

- **[低风险] 守卫过于保守**: 如果用户删除 config.toml 的 `[mapping]` 段但保留了模板列，切换到新 PPT 时映射不会自动更新。**缓解**: 用户可通过删除 config.toml 整体或切换到不同 PPT 后手动触发重新检测。自动更新是过度设计，保守比激进好。

- **[低风险] preserve_checks=True 时行数不一致**: 如果数据行数在两次调用之间变化，保留的 `_checked` 可能包含不存在的行号。**缓解**: `_rebuild_treeview` 在 `preserve_checks=True` 时过滤掉超出范围的 row_idx。

## Open Questions

- 无
