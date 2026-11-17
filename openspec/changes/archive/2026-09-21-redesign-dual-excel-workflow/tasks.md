## 1. 删除旧代码

- [x] 1.1 删除 `src/generator.py`（单Excel管线）
- [x] 1.2 删除 `src/sheet_routing.py`（Sheet路由）
- [x] 1.3 删除 `src/filler_mapping.py`（硬编码填料映射）

## 2. 重写配置模块

- [x] 2.1 重写 `src/config.py`: 新增 `project_id_column`、`filler_map`、`data_header_row` 字段
- [x] 2.2 实现 `load_config()` 支持新字段加载
- [x] 2.3 实现 `save_config()` 支持 `[filler_map]` 段序列化
- [x] 2.4 更新 `src/gui.py` 中 `Config` 的导入和构造为新的 dataclass 结构

## 3. 重写双Excel管线

- [x] 3.1 重写 `src/generator.py`: 改用 Config 对象传递参数
- [x] 3.2 实现 `"/"` 分割逻辑：填料值按 `"/"` split → 每个子值经 `filler_map` 映射 → 各自匹配 Slide
- [x] 3.3 实现项目编号匹配：使用可配置的 `project_id_column` 和 `data_header_row`
- [x] 3.4 移除 sheet_routing 调用，改用 filler_map 直接匹配

## 4. 更新 excel_reader

- [x] 4.1 `extract_project_ids()` 的 `col_name` 改为从 Config 读取
- [x] 4.2 `find_row_by_project_id()` 的 `header_row` 改为从 Config 读取
- [x] 4.3 确保 `col_name` 参数默认值仍然可用（向后兼容）

## 5. 重写 GUI

- [x] 5.1 移除上部单Excel工作流区域（模板PPT、Excel选择、映射配置、模板列、生成按钮）
- [x] 5.2 移除专用 LabelFrame 框架（标题 "批量生成工作流（双 Excel 联查）"）
- [x] 5.3 移除去重逻辑（`ph_tpl_var` 与 `tpl_var` 的同步）
- [x] 5.4 将双Excel控件提升为窗口主控件（模板PPT、源头Excel、数据Excel均直接布局）
- [x] 5.5 实现源头Excel选择后自动检测 project_id_column 和 template_column（利用 `detect_template_column`）
- [x] 5.6 实现数据Excel选择后自动读取Sheet列表
- [x] 5.7 实现模板PPT+数据Excel选择后自动检测映射（利用 `suggest_mapping`）
- [x] 5.8 实现输出文件时间戳命名（复用之前 `datetime.now().strftime`）
- [x] 5.9 实现生成完成后自动保存 config.toml（含 `project_id_column`、`template_column`、`filler_map`、`mapping`）

## 6. 更新 CLI 入口

- [x] 6.1 移除 `main()` 中对 `generator`、`read_excel`（旧版）的引用
- [x] 6.2 CLI 模式简化为直接启动 GUI（或保留 `-t -e -o` 批处理模式但使用新管线）
- [x] 6.3 确保 `python run.py`（无参数）和双击 exe 启动 GUI

## 7. 验证

- [x] 7.1 测试新管线：准备双Excel测试场景
- [x] 7.2 测试 `"/"` 分割：填料值含 "/" 时生成多个Slide
- [x] 7.3 测试 filler_map 未覆盖时的警告行为
- [x] 7.4 测试 config.toml 持久化和重新加载
- [x] 7.5 运行现有测试确保不引入回归（跳过已删除模块的测试）
