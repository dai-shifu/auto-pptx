## 1. 恢复 Config 模块

- [x] 1.1 创建 `src/config.py`：2 字段 Config（template_column + mapping，方向 excel_col→placeholder）
- [x] 1.2 实现 `load_config()` 和 `save_config()`

## 2. 映射方向统一

- [x] 2.1 在 `detect_and_suggest()` 中翻转 mapping 方向为 `{excel_col: placeholder}`
- [x] 2.2 移除 `generate()` 中 `_detect()` 的翻转逻辑（mapping 方向已统一）
- [x] 2.3 更新 `auto_detect.py` 中 `detect_and_suggest` 的 docstring 说明返回方向

## 3. GUI 映射方向 + 显示 + 模板列下拉框

- [x] 3.1 修改 `_auto_mapping` 存储方向为 `{excel_col: placeholder}`
- [x] 3.2 修改 `_rebuild_mapping`：遍历 excel_col 作为 key，显示 "Excel列→占位符" 格式，横向3列排列
- [x] 3.3 修改 `_generate`：移除 mapping 方向翻转，直接使用
- [x] 3.4 添加 config.toml 的 `_auto_load_config()` 调用（启动时加载 template_column 和 mapping）
- [x] 3.5 添加 `save_config()` 调用（生成完成后保存）
- [x] 3.6 模板列改为 `ttk.Combobox` 下拉框，自动检测填充默认值，用户可手动选择

## 4. 测试更新

- [x] 4.1 创建 `tests/test_config.py`：测试 load_config / save_config（excel_col→placeholder 方向）
- [x] 4.2 更新 `tests/test_auto_detect.py`：新增 TestDetectAndSuggest 验证返回方向
- [x] 4.3 test_generator.py 和 test_integration.py 测试通过，mapping 方向自动检测，无需手动修改
- [x] 4.4 运行全部测试确保通过（45/45 passed）
