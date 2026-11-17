## 1. 核心管线简化

- [x] 1.1 重写 `src/generator.py`：双 Excel 联查 → 单 Excel 逐行管线
  - `generate()` 签名改为 `(prs, excel_path, sheet_name, selected_rows, output_path)`
  - 移除 `extract_project_ids()` 调用，直接迭代 selected_rows
  - 移除 `find_row_by_project_id()` 调用，同行直接读数据
  - 标题行固定第 1 行
  - `_resolve_tpl_names()` 简化为 `split("/")` inline，不使用 filler_map
  - 自动检测 template_column 和 mapping（调用 auto_detect 函数）
  - 保留 clone_slide / replace_in_slide / 删除原始模板页逻辑不变
- [x] 1.2 修正 `src/gui.py` 中 `generate()` 的调用方，传入新参数

## 2. 删除 Config 模块

- [x] 2.1 删除 `src/config.py`
- [x] 2.2 清理所有 `from .config import ...` 引用（gui.py、generator.py）
  - gui.py 移除 `load_config`、`save_config`、`Config` 引用
  - gui.py 移除 `_auto_load_config()` 方法和 `save_config()` 调用
- [x] 2.3 删除仓库根目录的 `config.toml`

## 3. GUI 重写

- [x] 3.1 简化布局：移除"源头 Excel"和"数据 Excel"两个选择器，合并为一个"Excel 文件"选择器
- [x] 3.2 新增 Excel Sheet 选择器（紧跟在 Excel 文件选择下方）
  - 单 Sheet 自动选中，多 Sheet 下拉选择
  - Sheet 切换时刷新 Treeview 和映射
- [x] 3.3 移除起始行/结束行输入框
- [x] 3.4 移除项目编号列下拉框
- [x] 3.5 新增 ttk.Treeview 数据预览 + 行选择
  - 列：行号 + 模板列 + 映射引用的数据列
  - 复选框勾选（默认全选）
  - 全选/取消全选按钮
  - 横向滚动条
- [x] 3.6 映射区保留但改为纯手动覆盖（自动检测结果 + 下拉框调整）
- [x] 3.7 生成按钮处理逻辑适配新 `generate()` 签名
- [x] 3.8 状态栏提示优化（显示已选行数）

## 4. excel_reader 适配

- [x] 4.1 新增 `read_sheet_rows(excel_path, sheet_name)` 函数
  - 读取指定 Sheet 返回 (headers: list[str], rows: list[list[str]])
  - headers 从第 1 行读取
  - 保留 `read_excel`、`extract_project_ids`、`find_row_by_project_id` 不动（向后兼容）
- [x] 4.2 GUI 和 generate 使用 `read_sheet_rows` 替代 `_collect_headers_and_rows`

## 5. auto_detect 适配

- [x] 5.1 移除 `detect_and_suggest` 中对 template_column 的排除逻辑（不再需要排除模板列再映射）
- [x] 5.2 确认 `detect_template_column` 和 `suggest_mapping` 可直接被 generate() 调用

## 6. 测试更新

- [x] 6.1 更新 `tests/test_generator.py`：适配新 `generate()` 签名，移除 Config 参数
- [x] 6.2 更新 `tests/test_integration.py`：适配新签名
- [x] 6.3 删除 `tests/test_config.py`（config.py 已删除）
- [x] 6.4 更新 `tests/create_fixtures.py`：移除 config.toml 生成，更新 placeholder 名称为中文
- [x] 6.5 运行全部测试确保通过（38/38 passed）

## 7. 整理收尾

- [x] 7.1 更新 `CLAUDE.md`：反映新架构（单 Excel、无 config.toml、自动检测）
- [x] 7.2 从 `.gitignore` 移除 `config.toml`（不再生成，不再需要忽略）
- [x] 7.3 确认 Nuitka 打包不受影响（config.py 不在 include-package 中，build.py 无 config 引用）
- [x] 7.4 手动端到端测试：PPT + Excel → 勾选行 → 生成 → 验证输出
