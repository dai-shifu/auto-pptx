# auto-pptx 入门：先生成一页 | Generate your first slide

简体中文 | [English](#english)

先用公开样例做一页，再换成自己的 Excel 和 PPT。Windows 用户可以直接使用[发布版 exe](https://github.com/dai-shifu/auto-pptx/releases)，不用下载项目源码或安装 Python。

## 用样例生成第一页

1. 下载日报样例的 [Excel 数据](../examples/bio-daily/data.xlsx)和 [PPT 模板](../examples/bio-daily/template.pptx)。在 GitHub 文件页点击下载按钮，不要把网页另存为文件。
2. 运行下载的 exe，分别点击「浏览」选择文件。「Sheet」选「日报数据」，标题行设为 `1`，模板列选「模板」。
3. 核对映射：「模板」列应为「(不映射)」，其他数据列应对应同名占位符，例如「今日摘要 → 今日摘要」。只调整不符的项。
4. 点击「取消全选」，只勾选 **Excel 第 2 行**（标题下第一条数据），再点击「生成 PPT」。打开 Excel 同目录下生成的文件：应只有一页「日报总览」，没有警告。可与[样例预览](../examples/bio-daily/previews/slide-01.png)对照。

想试全部五行？见[完整日报演练](../examples/bio-daily/README.md#生成日报)。

## 分清选页和填值

| 关系 | 样例 |
| --- | --- |
| **Excel 模板列的值 → PPT 模板页** | 第 2 行「模板」列的值是 `日报总览`，选中标有 `{{tpl::日报总览}}` 的页。模板名区分大小写，一行选多页用半角 `/` 分隔。 |
| **Excel 数据列 → PPT 占位符** | 「今日摘要」列的值填入选中页上的 `{{今日摘要}}`。列名不必和占位符同名，例如「项目名称」可映射到 `{{课题名称}}`。 |

`{{tpl::名称}}` 是选页标识，不是待填字段。程序只保留生成页，原始封面或目录不会自动保留。程序替换文本框和表格里的占位符，不替换图表数据。未映射的占位符保留原文并报警；已映射但单元格为空时填空文本。详见[模板规则](使用培训.md#模板页与占位符)。

## 换用自己的文件

确认工作表、标题行、模板列和映射后，先勾选一行，点击「生成 PPT」。有错误或警告时，按提示核对模板列是否选对、单元格中的模板名是否与页标识一致，以及需要填值的占位符是否已映射。打开生成文件确认版式后，再批量生成。更多情况见[使用指南](使用培训.md)。

## English

Start with one slide from the public sample. Then try your own Excel and PowerPoint files. On Windows, use the [released exe](https://github.com/dai-shifu/auto-pptx/releases) without downloading source code or installing Python. The GUI labels below are in Chinese.

### Generate one slide from the sample

1. Download the [sample workbook](../examples/bio-daily/data.xlsx) and [slide template](../examples/bio-daily/template.pptx) using the download button on each GitHub file page.
2. Run the downloaded exe and click “浏览” (Browse) to select each file. Set **Sheet** to `日报数据`, header row to `1`, and template column to `模板`.
3. Verify the mappings: `模板` should be `(不映射)` (Do not map), and the other data columns should match placeholders by name, such as `今日摘要 → 今日摘要`. Adjust only the mismatches.
4. Click “取消全选” (Clear selection), select only **Excel row 2** (the first row below the headers), and click “生成 PPT” (Generate PowerPoint). Open the output next to the workbook. It should contain one `日报总览` (Daily Overview) slide with no warnings. Compare it with the [sample preview](../examples/bio-daily/previews/slide-01.png).

To try all five rows, see the [full example (Chinese)](../examples/bio-daily/README.md#生成日报).

### Slide selection and field mapping are separate

| Relationship | Example |
| --- | --- |
| **Excel template-column value → PowerPoint template slide** | Row 2 has `日报总览` in `模板`, so it selects the slide marked `{{tpl::日报总览}}`. Template names are case-sensitive. Use `/` to select more than one slide per row. |
| **Excel data column → PowerPoint placeholder** | The value in `今日摘要` fills `{{今日摘要}}` on the selected slide. Names can differ: `项目名称` (Project name) can map to `{{课题名称}}` (Research topic name). |

`{{tpl::name}}` identifies a slide; it is not a field to fill. The output contains only generated slides, so an original cover or contents slide is not kept automatically. The app replaces placeholders in text boxes and tables, not chart data. An unmapped placeholder stays in the output and triggers a warning; a mapped cell with no value inserts empty text. See the [template rules (Chinese)](使用培训.md#模板页与占位符).

### Try your own files

Confirm the worksheet, header row, template column, and mappings. Select one row and click “生成 PPT” (Generate PowerPoint). If an error or warning appears, check the selected template column, whether the cell's value matches the template slide identifier, and whether each field you want to fill has a mapping. Open the output to review the layout before generating the full batch. See the [user guide (Chinese)](使用培训.md) for more troubleshooting.
