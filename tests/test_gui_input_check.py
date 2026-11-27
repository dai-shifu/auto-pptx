import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import pytest
from openpyxl import load_workbook

from src import gui
from tests.create_fixtures import DATA_SHEET, build_template_pptx, build_test_xlsx


@pytest.fixture
def app_with_files(tmp_path, monkeypatch, request):
    try:
        root = tk.Tk()
    except tk.TclError as error:
        if request.config.getoption("--require-gui"):
            pytest.fail(f"Required Tk display unavailable: {error}")
        pytest.skip(f"Tk display unavailable: {error}")
    root.geometry("1000x600")
    root.minsize(1000, 600)
    try:
        config = tmp_path / "config.toml"
        config.write_text(
            'template_column = "模板"\nheader_row = 1\n[mapping]\n"标题" = "作者"\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(gui, "CONFIG_PATH", config)
        template = build_template_pptx(tmp_path / "private-template.pptx")
        excel = build_test_xlsx(tmp_path / "private-workbook.xlsx")
        workbook = load_workbook(excel)
        try:
            workbook[DATA_SHEET]["A2"] = "cover / private-template-token"
            workbook[DATA_SHEET]["B2"] = "private-cell-text"
            workbook.save(excel)
        finally:
            workbook.close()

        app = gui.App(root)
        app.tpl_var.set(str(template))
        app.excel_var.set(str(excel))
        app._update_sheets(str(excel))
        root.update()
        yield app, template, excel, config
    finally:
        root.destroy()


def _children(widget):
    for child in widget.winfo_children():
        yield child
        yield from _children(child)


def _press(window, label):
    button = next(
        widget for widget in _children(window)
        if isinstance(widget, ttk.Button) and widget.cget("text") == label
    )
    button.invoke()


def _content(widget):
    return widget.get("1.0", "end-1c")


def test_check_and_share_preserve_active_selections_and_files(app_with_files):
    app, template, excel, config = app_with_files
    snapshots = {path: path.read_bytes() for path in (template, excel, config)}
    for widget in (app.check_btn, app.generate_btn, app.sheet_combo, app.tree, app.mapping_pane):
        assert widget.winfo_viewable()
        assert widget.winfo_rooty() + widget.winfo_height() <= app.root.winfo_rooty() + 600

    author = next(var for name, var in app.mapping_widgets if name == "作者")
    combo = next(
        widget for widget in _children(app.mapping_frame)
        if isinstance(widget, ttk.Combobox) and str(widget.cget("textvariable")) == str(author)
    )
    combo.current(0)  # Explicitly choose "(不映射)" instead of the automatic suggestion.
    combo.event_generate("<<ComboboxSelected>>")
    x, y, width, height = app.tree.bbox("2", "#")
    app.tree.event_generate("<Button-1>", x=x + width // 2, y=y + height // 2)
    app.root.update()
    assert app._checked == {2}
    assert app._explicit_mapping["作者"] is None

    app.root.clipboard_clear()
    app.root.clipboard_append("existing clipboard")
    settings = app._current_settings()
    app.check_btn.invoke()
    dialog = app._check_window
    text = _content(dialog.report_text)
    assert "预计 1 页" in text
    assert "Excel 第 2 行：部分匹配" in text
    assert "找不到模板：private-template-token" in text
    assert "当前映射（Excel 列 → PPT 占位符）：标题 → {{作者}}" in text
    assert "明确不映射：作者" in text
    assert _content(dialog.report_text) == text

    _press(dialog, "预览分享摘要")
    preview = dialog.preview_window
    summary = next(widget for widget in _children(preview) if isinstance(widget, ScrolledText))
    for sensitive in (str(excel.parent), excel.name, template.name, "private-cell-text", "private-template-token"):
        assert sensitive not in _content(summary)
    assert "Excel 第 2 行：部分匹配" in _content(summary)
    assert "找不到模板：1 项" in _content(summary)
    _press(preview, "取消")
    assert app.root.clipboard_get() == "existing clipboard"

    _press(dialog, "预览分享摘要")
    preview = dialog.preview_window
    summary = next(widget for widget in _children(preview) if isinstance(widget, ScrolledText))
    summary.delete("1.0", "end")
    summary.insert("1.0", "经审阅的摘要\n")
    _press(preview, "复制摘要")
    assert app.root.clipboard_get() == "经审阅的摘要\n"
    assert app._current_settings() == settings
    assert app.tree.set("2", "#") == "☑"
    assert {path: path.read_bytes() for path in snapshots} == snapshots
    assert set(excel.parent.iterdir()) == snapshots.keys()


def test_check_without_rows_and_read_failure_do_not_show_previous_result(app_with_files):
    app, _, excel, config = app_with_files
    original_config = config.read_bytes()
    app.check_btn.invoke()
    original = app._check_window
    assert "未勾选数据行" in _content(original.report_text)
    assert "预计 1 页" not in _content(original.report_text)
    assert "Excel 列名：" in _content(original.report_text)

    excel.write_text("deliberately corrupted test fixture", encoding="utf-8")
    app.check_btn.invoke()
    assert not original.winfo_exists()
    dialog = app._check_window
    report = _content(dialog.report_text)
    assert "无法读取 Excel" in report
    assert "Excel 列名：" not in report
    assert "当前映射" not in report
    assert "本机读取详情" in report
    _press(dialog, "预览分享摘要")
    preview = dialog.preview_window
    summary = next(widget for widget in _children(preview) if isinstance(widget, ScrolledText))
    assert "无法读取 Excel" in _content(summary)
    assert "本机读取详情" not in _content(summary)
    assert config.read_bytes() == original_config
