## Context

auto-pptx 当前有两套生成管线：早期单Excel管线和双Excel联查管线（`generator.py`）。实际业务场景只需要双Excel联查，单Excel管线是早期版本的遗留。同时批量生成管线中有大量 hardcode（填料映射表、Sheet路由、列名），需要改为可配置。

## Goals / Non-Goals

**Goals:**
- 应用核心管线为"源头Excel + 数据Excel → 多Slide PPT"
- 源头Excel读取项目编号 + 模板列，数据Excel按项目编号匹配行数据
- 模板列、填料到模板映射、数据Excel列到占位符映射均可配置
- 填料值含 `"/"` 时自动拆分为多个模板并生成多个Slide
- GUI 仅保留双Excel工作流，默认启动GUI

**Non-Goals:**
- 不保留早期单Excel管线的任何向后兼容
- 不保留 Sheet 路由机制（`sheet_routing.py`）
- 不保留 hardcode 填料映射（`filler_mapping.py`）
- 不保留 txt 文件加载行号功能

## Decisions

### 1. Config 结构设计

选择扩展现有 `Config` dataclass，新增字段并保留 TOML 格式。

```toml
project_id_column = "项目编号"
template_column = "填料"
data_header_row = 2

[filler_map]
"Ni NTA Beads 6FF" = "Ni-NTA"
"Co-NTA" = "Co-NTA"

[mapping]
"温度" = "温度"
"时间" = "反应时间"
```

- `project_id_column`: 源头和数据Excel共用的项目编号列名
- `template_column`: 源头Excel中匹配模板的列名
- `data_header_row`: 数据Excel标题行号（1-based）
- `[filler_map]`: 填料值→tpl名称映射
- `[mapping]`: Excel列名→占位符名映射

**替代方案**: 用YAML/JSON。选择TOML因为Python 3.11+ stdlib支持且兼容已有格式。

### 2. `"/"` 分割逻辑

在 generator 中处理：读取填料值 → 按 `"/"` 分割 → 每个分段去空格 → 经 `filler_map` 查找 tpl 名 → 找到匹配的 Slide → 每个 Slide 共享同一份行数据。

### 3. 管线流程

```
config.toml 加载
    │
    ▼
源头 Excel: 按行范围读取 → 每行提取 (项目编号, 模板列值)
    ├── "/" 分割模板列值
    ├── filler_map 映射 → tpl 名称集合
    └── 数据 Excel: 按项目编号精确匹配行数据
            │
            ▼  (映射规则: mapping)
        克隆 Slide → 替换占位符
            │
            ▼
        删除原始模板页 → 保存
```

### 4. GUI 结构

单一窗口，去除旧单Excel区域和专用标签页框架。所有控件平铺在一个窗口中：

- 文件选择区: 模板PPT、源头Excel、数据Excel
- 源头配置: 项目编号列(下拉)、模板列(下拉)、起始行、结束行
- 数据配置: Sheet选择(下拉)
- 映射区: 动态生成的列→占位符下拉框（自动检测）

### 5. 删除的代码

| 文件 | 原因 |
|------|------|
| 早期单Excel生成模块 | 单Excel管线，不再需要 |
| `src/sheet_routing.py` | Sheet路由由填料值直接匹配模板替代 |
| `src/filler_mapping.py` | 硬编码映射改为 `config.toml` `[filler_map]` |

### 6. auto_detect 调整

保留 `suggest_mapping` 和 `detect_template_column` 核心逻辑。新增：
- 源头Excel调用: 检测 `project_id_column` (在源头表头中找 "项目编号" 或相近)
- 数据Excel调用: 检测映射（读PPT占位符 → match数据Excel表头）

## Risks / Trade-offs

- **配置缺失风险**: 如果 `[filler_map]` 未覆盖实际填料值，该行会跳过并输出警告。→ GUI 中显示警告摘要。
- **仅双Excel**: 如果你需要单Excel场景，需要切换回旧版 workflow。→ 单Excel场景可以由用户在一个Excel中同时放项目编号+数据来实现（把模板列用filler_map做映射即可），本设计不提供此路径。
- **`"/"` 歧义**: 如果填料值本身包含 `"/"`（如 "Ni-NTA/其它"），会被错误分割。→ filler_map可作为兜底——先精确查表，查不到再分割。后续可考虑转义字符。
