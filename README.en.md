# auto-pptx

[简体中文](README.md) | English

A desktop tool that generates a single PowerPoint presentation from selected Excel rows using slide templates.

- Replace placeholders in text boxes and tables.
- Use multiple slide templates for each data row.
- Select the rows to include and save column mappings.

![Excel data + PPT templates → one generated presentation; the daily report example uses 5 data rows and 3 template slides to produce 5 slides](docs/images/generation-overview.en.svg)

![Actual output: DEMO-001 project progress from the protein expression and purification daily report](examples/bio-daily/previews/slide-02.png)

[View the example and download templates (Chinese)](examples/bio-daily/README.md)

## Quick start

Have the application ready, along with a `.pptx` template and its matching `.xlsx` file supplied by your maintainer. For a first try, use the [daily report example (Chinese)](examples/bio-daily/README.md).

1. Start the application and select the template and Excel file.
2. Confirm the worksheet, header row, template column, and **Excel column → PowerPoint placeholder** mappings.
3. Select the rows to include and click “生成 PPT” (Generate PowerPoint).

![Actual Windows interface with the daily report example loaded; no data rows selected](docs/images/app-interface.png)

The screenshot shows the Chinese application interface on Windows. Click “全选” (Select all) or select individual rows before generating. See the [interface guide (Chinese)](docs/使用培训.md#界面说明) for a description of each area.

The output is saved **in the same folder as the Excel file**, named `output_YYYYMMDD_HHMMSS.pptx`. The “完成” (Complete) dialog and bottom status bar show the save path. The application interface is currently in Chinese.

## Documentation and contributing

- [Application users (Chinese)](docs/使用培训.md#软件使用者): fill in data, use the interface, generate reports, and troubleshoot.
- [Maintainers (Chinese)](docs/使用培训.md#维护人员): templates, Excel formats, and `config.toml`.
- [Contributing (Chinese)](CONTRIBUTING.md): run from source, test, and submit pull requests.
- [Development and build guide (Chinese)](docs/开发.md): modules, example maintenance, and packaging.

Issues and pull requests are welcome on GitHub. When reporting an issue, include the application version, reproduction steps, and a sanitized example.

## License

[MIT](LICENSE).
