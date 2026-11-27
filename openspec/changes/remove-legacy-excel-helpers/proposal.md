## Why

软件已改用单 Excel 工作流，不再按项目编号联查工作簿。旧兼容函数在仓库内只由测试调用，继续保留会增加维护成本，也容易让文档误示仍支持旧流程。

## What Changes

- **BREAKING（源码调用方）**：删除 `src.excel_reader` 的 `extract_project_ids()`、`find_row_by_project_id()` 和旧 `read_excel()`，不保留兼容别名。桌面软件的单 Excel 流程不变。
- 删除只覆盖退役函数的测试。保留现行 Excel 读取、映射和生成的回归覆盖。
- 清除现行文档中关于旧工作流或兼容接口仍受支持的说明。OpenSpec 归档和已完成的验证记录保留历史事实，不作为现行功能说明。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `single-excel-pipeline`：明确生成仅使用选定工作簿和工作表，不要求项目编号，也不按编号联查或去重。

## Impact

涉及 `src/excel_reader.py`、对应测试及现行文档。直接导入退役函数的外部脚本需迁移。GUI、配置格式、示例、依赖及发布方式不变。
