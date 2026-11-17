## 1. 简化 `_get_config_path()` 并加强容错

- [x] 1.1 将 `_get_config_path()` 从 `__compiled__.containing_dir` 方案改为 `sys.argv[0].resolve().parent` 一行方案
- [x] 1.2 测试开发模式：`python run.py gui` 验证 config.toml 路径指向项目根目录

## 2. `load_config()` 容错

- [x] 2.1 `load_config()` 文件不存在时返回 `Config()` 默认值（不再抛 `FileNotFoundError`）
- [x] 2.2 更新 `tests/test_config.py` 中 `test_load_config_file_not_found` 测试用例：验证返回默认值而非抛异常
- [x] 2.3 运行 `uv run --group dev pytest tests/test_config.py` 确保所有测试通过

## 3. 启动时自动创建 config.toml

- [x] 3.1 `_auto_load_config()` 中：`load_config()` 后若文件不存在，调用 `save_config()` 写入默认配置
- [x] 3.2 测试开发模式：删除项目根 config.toml，启动 GUI，验证自动生成且内容正确

## 4. `_generate()` 防御性写入

- [x] 4.1 在 `save_config()` 前加 `CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)`
- [x] 4.2 打包并测试：把 EXE 放到任意目录，启动 → 生成 PPT，验证同目录出现 config.toml
- [x] 4.3 再次启动同一 EXE，验证自动加载上次保存的 config.toml 配置
