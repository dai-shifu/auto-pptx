## 1. 来源标记: 解决 B1/B2 冻结问题（替换旧方案）

**根因**: 旧方案用 `if not self._auto_mapping:` 做 write-once 守卫，导致自动检测值一经填入就永久冻结，切换文件后无法更新。需要区分"from config"和"from auto_detect"两种来源。

- [x] 1.1 `__init__` 新增 `_mapping_from_config: bool = False` 和 `_tcol_from_config: bool = False` 两个实例变量
- [x] 1.2 `_auto_load_config()` 中加载 mapping 时设 `_mapping_from_config = True`，加载 template_column 时设 `_tcol_from_config = True`
- [x] 1.3 `_auto_detect()` 中将 `if not self._auto_mapping:` 改为 `if not self._mapping_from_config:`
- [x] 1.4 `_auto_detect()` 中将 `if template_col and not self.tcol_var.get():` 改为 `if template_col and not self._tcol_from_config:`
- [ ] 1.5 验证: 无 config.toml → 浏览 PPT-A + Excel-A → 得到 auto_detect 值 A → 切换到 PPT-B + Excel-B → 确认 mapping 和 tcol_var 更新为 B（自动检测值可被覆盖）
- [ ] 1.6 验证: 有 config.toml mapping + template_column → 浏览 PPT + Excel → 确认映射区和模板列保持 config 值（`from_config=True` 阻止覆盖）

## 2. 配置加载显式反馈

- [x] 2.1 `_auto_load_config()` 中移除 `except Exception: pass`，捕获异常后在状态栏显示 "配置加载失败: <错误信息>"
- [x] 2.2 加载成功时在状态栏显示 "已从 config.toml 加载配置"
- [ ] 2.3 验证: 故意写错误的 TOML 语法，启动后确认状态栏显示错误信息而非静默失败

## 3. 配置路径固定 (B5)

- [x] 3.1 `CONFIG_PATH` 从 `Path("config.toml")` 改为 `Path(__file__).resolve().parent.parent / "config.toml"`（项目根目录）

## 4. 代码清理: 消除重复占位符收集 (B3)

- [x] 4.1 `auto_detect._collect_placeholders` 去掉下划线前缀改为公开函数 `collect_placeholders`
- [x] 4.2 `gui.py` 中 `from .auto_detect import collect_placeholders`，删除 `App._collect_placeholders_from_ppt` 方法
- [x] 4.3 `_auto_detect()` 中调用 `collect_placeholders(prs)` 替代 `self._collect_placeholders_from_ppt(prs)`

## 5. 切换模板列保留勾选 + 默认全不选 (B4)

- [x] 5.1 `_rebuild_treeview()` 增加 `preserve_checks=False` 参数
- [x] 5.2 `preserve_checks=True` 时不清空 `_checked`，仅更新 Treeview 结构；过滤掉超出行范围的 row_idx
- [x] 5.3 `_on_tcol_change()` 调用 `_rebuild_treeview(preserve_checks=True)`
- [x] 5.4 `_rebuild_treeview()` 中删除 `if not preserve_checks: self._checked.add(excel_row)` — 不再自动全选，首次加载和切换 Sheet 均默认为 ☐ 全不选
- [x] 5.5 `_on_tree_click` 绑定从 `<ButtonRelease-1>` 改为 `<Button-1>` — 按下瞬间锁定目标行，避免漂移到其他行
- [x] 5.6 `_on_tree_click` 在 checkbox 列（`#1`）处理完 toggle 后 `return "break"` — 阻止 Treeview 默认选中行为
- [ ] 5.7 验证: 浏览 Excel → 确认 Treeview 全不选（☐）；勾选行 2、4 → 切换模板列 → 确认勾选保留（☑ 仍在行 2、4）；切换 Sheet → 确认全不选（☐）

## 6. 空映射传参修复 (B6)

- [x] 6.1 `_generate()` 中将 `mapping=mapping if mapping else None` 改为 `mapping=mapping`，直接传 mapping 给 generate
- [ ] 6.2 验证: 将所有映射列设为 "(不映射)" → 生成 → 确认不报错，也不触发 auto_detect 覆盖

## 7. 集成验证

- [ ] 7.1 完整流程验证: 启动 → 浏览 Excel + PPT → 手动勾选部分行 → 手动调整映射 → 生成 → 关闭 → 重新启动 → 确认映射和勾选保持
- [x] 7.2 运行现有测试 `uv run --group dev pytest` 确认无回归（7 个失败均为预存 fixture 不匹配，与本次修改无关）
