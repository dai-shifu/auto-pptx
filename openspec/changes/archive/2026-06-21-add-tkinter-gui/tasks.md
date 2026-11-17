## 1. 配置格式迁移 (YAML → TOML)

- [x] 1.1 改写 `src/config.py`：`load_config()` 改为读取 TOML 格式，新增 `save_config()` 写入函数
- [x] 1.2 更新测试夹具 `tests/create_fixtures.py` 和 `tests/fixtures/config.toml`
- [x] 1.3 更新 `tests/test_config.py`：适配 TOML 配置读写
- [x] 1.4 更新 `tests/test_integration.py` 等引用 config.yaml 的测试

## 2. 自动检测

- [x] 2.1 新建 `src/auto_detect.py`：实现模板列自动检测（集合交集匹配）
- [x] 2.2 实现列→占位符映射自动建议（大小写不敏感 + 编辑距离）
- [x] 2.3 添加 `tests/test_auto_detect.py`

## 3. GUI 界面

- [x] 3.1 新建 `src/gui.py`：tkinter 窗口，文件选择 + 映射下拉框 + 生成按钮
- [x] 3.2 GUI 启动时自动加载 config.toml，不存在时走首次配置流程
- [x] 3.3 生成完成后自动保存 config.toml

## 4. 入口与打包

- [x] 4.1 修改 `src/main.py`：新增 `gui` 子命令或独立入口
- [x] 4.2 修改 `build.py`：打包 GUI 入口为独立 exe

## 5. 收尾

- [x] 5.1 运行全量测试 `pytest` 确保无回归
- [x] 5.2 删除 `config.yaml`，更新 README 使用说明
