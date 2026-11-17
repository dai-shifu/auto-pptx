## Context

需要构建一个 Excel → PPT 的批量生成工具。用户提供一个 PPT 模板（包含多种布局）和一个 Excel 数据文件，工具自动生成一个包含多页 PPT 的文件。

技术约束：
- Python 生态是唯一成熟选择（openpyxl + python-pptx）
- 需要打包为独立可执行文件
- 单次生成 ~20 页，Excel 可能随时间膨胀
- Excel 每一行对应不同的模板页，不存在多行复用同一模板的情况

## Goals / Non-Goals

**Goals:**
- 从 Excel 读取结构化数据，每行生成一页 PPT
- 支持文本框和表格单元格中的占位符替换（`{{xxx}}` 格式）
- 支持多个模板布局共存于同一个模板 PPT 文件中
- 通过标识占位符（`{{tpl::名称}}`）识别模板页身份
- 通过 config.yaml 定义映射关系
- 整文件加载模板，原地替换占位符，保留所有元素（图片、样式、排版）
- 输出为单个 PPT 文件
- 可打包为独立可执行文件

**Non-Goals:**
- 不支持图表数据替换（后续扩展）
- 不支持图片动态替换（模板已有固定图片保留）
- 不处理 Excel 中的公式、样式等非数据内容
- 不支持增量更新（每次全量生成）

## Decisions

### 1. 技术栈选择：Python (openpyxl + python-pptx)

**选择**: Python 3.11+，openpyxl 读取 Excel，python-pptx 操作 PPT，PyYAML 读取配置。

**理由**: Rust 和 Go 均无成熟 PPTX 操作库（Rust 唯一全链路库仅 7 颗星 v0.1.0；Go unioffice 不支持表格操作和删除 Slide，且 AGPL 协议限制商用）。python-pptx 是唯一支持原地替换文本框/表格占位符 + 删除 Slide 的成熟方案。20 页的生成量，Python 性能完全足够。

**替代方案**: Rust (calamine + office_oxide) - office_oxide 仅 23 星且只支持读取；Go (excelize + unioffice) - unioffice 商业授权且不支持表格单元格。

### 2. Slide 处理策略：整文件复制 + 原地替换 + 删除未用页

**选择**: `Presentation(template.pptx)` 加载完整模板到内存，建立 `{tpl_name: slide}` 索引，对每行 Excel 数据在对应模板页上原地替换占位符，最后删除未被匹配的模板页，按模板原始顺序保存。

**前提约束**: Excel 每一行对应不同的模板页，不存在多行复用同一模板的情况。

**理由**: 无需任何 Slide 复制操作（无论是 ZIP 层面还是 XML deepcopy）。python-pptx 的 `Presentation(path)` 本身就是内存中的完整副本，直接在上面操作即可。删除未用页通过底层 `_sldIdLst` 操作实现（python-pptx 无公开删除 API）。整个流程零 deep copy，技术风险最低。

**流程**:
1. `Presentation(template.pptx)` — 整文件加载到内存
2. 扫描所有 Slide，建立 `{tpl_name: slide}` 索引
3. 遍历 Excel 每一行，找到对应模板页，原地替换占位符
4. 从后往前删除未被任何 Excel 行匹配到的模板页（`prs.slides._sldIdLst.remove(sldId)`）
5. 保存，输出页按模板原始顺序排列

**替代方案**: ZIP 层面复制（复杂度高，需手动处理 .rels 和媒体引用）；Deep copy 单页到新 Presentation（可行但不必要，增加复杂度）。

### 3. 模板匹配机制：标识占位符

**选择**: 模板 PPT 中通过隐藏文本框放置 `{{tpl::名称}}` 标识，放在页面负坐标区域（x < 0, y < 0）。启动时扫描所有 Slide 建立索引。

**理由**: 视觉直观，用户在 PPT 编辑器中可看到标识（拖动可见），不影响正常内容展示。O(1) 查找。

**替代方案**: 按页码匹配（不直观，调整模板顺序就乱了）；备注区匹配（用户操作门槛高）。

### 4. 配置方式：独立 config.yaml

**选择**: 使用独立的 YAML 配置文件，包含模板标记列名和映射表。Excel 中模板标记列的值直接作为模板标识名称（对应 `{{tpl::名称}}`），无需额外的映射层。

**理由**: 配置与数据分离，可复用，用户友好。

**替代方案**: Excel 中单独 Sheet 存配置（与数据混在一起）。

**config.yaml 格式**:
```yaml
# Excel 中标识使用哪个模板的列名
template_column: "模板"

# Excel 列名 → PPT 占位符名 的映射
mapping:
  姓名: name
  部门: dept
  销售额: sales
```

### 5. 打包方案：Nuitka

**选择**: 使用 Nuitka 编译 Python 为独立可执行文件。

**理由**: 相比 PyInstaller，Nuitka 体积更小（20-80MB vs 50-200MB），启动更快，性能更好，且能保护源码。

## Risks / Trade-offs

- **[占位符跨 Run 拆分]** → python-pptx 中，一个段落的文本可能被拆分到多个 Run 中（如 `{{` 在一个 Run，`name}}` 在另一个），导致逐 Run 替换失败。缓解：先拼接段落所有 Run 的文本，替换后写回第一个 Run，清空其余 Run。代价是丢失后续 Run 的格式（保留第一个 Run 的格式）。这是 python-pptx 社区的标准做法。
- **[占位符格式冲突]** → `{{xxx}}` 可能与模板中已有的双花括号文本冲突。缓解：使用 `{{` + 具体前缀（如 `{{tpl::` 标识，`{{` 数据），且占位符格式可在 config 中自定义。
- **[中文编码]** → Excel 中文表头、PPT 中文内容的编码处理。缓解：openpyxl 和 python-pptx 原生支持 UTF-8，无需特殊处理。
- **[大型模板内存占用]** → 模板含大量高清图片时全量加载内存较高。当前版本不做 ZIP 裁剪优化，后续可按需添加。
- **[删除 Slide 的索引稳定性]** → python-pptx 无公开 Slide 删除 API，需操作 `_sldIdLst` 底层属性。删除时索引会变化，必须从后往前删。缓解：收集待删除索引后逆序处理。

## Open Questions

- 占位符前缀是否需要可配置（如从 `{{` 改为 `${}`）
