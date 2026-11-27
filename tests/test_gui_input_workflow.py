"""Real Tk regressions for browsing, row selection and the generation guard."""

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from unittest.mock import Mock

import pytest
from openpyxl import load_workbook

from src import gui
from tests.create_fixtures import DATA_ROWS, DATA_SHEET


@pytest.fixture
def app(tmp_path, generated_fixtures, monkeypatch, request):
    try:
        root = tk.Tk()
    except tk.TclError as error:
        if request.config.getoption("--require-gui"):
            pytest.fail(f"Required Tk display unavailable: {error}")
        pytest.skip(f"Tk display unavailable: {error}")
    try:
        root.geometry("1000x600")
        monkeypatch.setattr(gui, "CONFIG_PATH", tmp_path / "config.toml")
        monkeypatch.setattr(gui.messagebox, "showerror", Mock())
        monkeypatch.setattr(gui.messagebox, "showinfo", Mock())
        window = gui.App(root)
        excel = generated_fixtures / "test_data.xlsx"
        workbook = load_workbook(excel)
        try:
            sheet = workbook[DATA_SHEET]
            sheet.insert_rows(1)
            sheet["A1"] = "说明：标题在下一行"
            workbook.copy_worksheet(sheet).title = "另一张表"
            workbook.save(excel)
        finally:
            workbook.close()
        _browse(window, monkeypatch, window.tpl_var, generated_fixtures / "template.pptx")
        _browse(window, monkeypatch, window.excel_var, excel)
        assert window.hrow_var.get() == 2
        assert window.tree.get_children() == ("3", "4", "5")
        yield window
    finally:
        root.destroy()


def _descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from _descendants(child)


def _path_entry(app, variable):
    return next(
        widget for widget in _descendants(app.root)
        if isinstance(widget, ttk.Entry) and str(widget.cget("textvariable")) == str(variable)
    )


def _browse(app, monkeypatch, variable, path):
    entry = _path_entry(app, variable)
    row = entry.grid_info()["row"]
    button = next(
        widget for widget in entry.master.winfo_children()
        if isinstance(widget, ttk.Button) and widget.cget("text") == "浏览"
        and widget.grid_info()["row"] == row
    )
    chooser = Mock(return_value=str(path))
    monkeypatch.setattr(gui.filedialog, "askopenfilename", chooser)
    button.invoke()
    chooser.assert_called_once()
    app.root.update()


def _choose(app, combo, value):
    combo.current(combo["values"].index(value))
    combo.event_generate("<<ComboboxSelected>>")
    app.root.update()


def _check_row(app, row):
    x, y, width, height = app.tree.bbox(str(row), "#")
    app.tree.event_generate("<Button-1>", x=x + width // 2, y=y + height // 2)
    assert _visible_checks(app) == (row,)
    assert app._current_settings().selected_rows == (row,)


def _visible_checks(app):
    return tuple(int(row) for row in app.tree.get_children() if app.tree.set(row, "#") == "☑")


def test_readonly_paths_and_browse_cancel_keep_preview_and_selection(app, monkeypatch):
    _check_row(app, 4)
    rows = {row: app.tree.item(row, "values") for row in app.tree.get_children()}
    paths = app.tpl_var.get(), app.excel_var.get()
    for variable, path in zip((app.tpl_var, app.excel_var), paths):
        entry = _path_entry(app, variable)
        assert entry.instate(("readonly",))
        assert entry.get() == path
        _browse(app, monkeypatch, variable, "")
        assert (app.tpl_var.get(), app.excel_var.get()) == paths
        assert app.tree.get_children() == tuple(rows)
        assert all(app.tree.item(row, "values") == values for row, values in rows.items())
        assert app._current_settings().selected_rows == (4,)


def test_editing_mapping_and_swapping_template_preserve_actual_excel_row(app, monkeypatch, tmp_path):
    _check_row(app, 4)
    title = dict(app.mapping_widgets)["标题"]
    combo = next(
        widget for widget in _descendants(app.mapping_frame)
        if isinstance(widget, ttk.Combobox) and str(widget.cget("textvariable")) == str(title)
    )
    assert combo.get() == "标题"
    _choose(app, combo, "(不映射)")
    assert _visible_checks(app) == app._current_settings().selected_rows == (4,)

    replacement = tmp_path / "replacement.pptx"
    replacement.write_bytes(Path(app.tpl_var.get()).read_bytes())
    _browse(app, monkeypatch, app.tpl_var, replacement)
    assert app.tpl_var.get() == str(replacement)
    assert _visible_checks(app) == app._current_settings().selected_rows == (4,)
    assert app._explicit_mapping["标题"] is None
    assert "标题" not in app._current_settings().mapping


@pytest.mark.parametrize("change", ["excel", "sheet", "header"])
def test_switching_data_context_resets_checks_even_if_same_row_ids(app, monkeypatch, tmp_path, change):
    _check_row(app, 4)
    if change == "excel":
        replacement = tmp_path / "replacement.xlsx"
        replacement.write_bytes(Path(app.excel_var.get()).read_bytes())
        _browse(app, monkeypatch, app.excel_var, replacement)
        assert app.excel_var.get() == str(replacement)
    elif change == "sheet":
        _choose(app, app.sheet_combo, "另一张表")
        assert app._current_settings().sheet_name == "另一张表"
    else:
        app.hrow_var.set(1)
        app._on_header_row_change()
        assert app._current_settings().header_row == 1

    assert app.tree.exists("4")
    assert _visible_checks(app) == app._current_settings().selected_rows == ()


def test_unreadable_excel_clears_stale_data_and_cannot_generate(app, monkeypatch, tmp_path):
    _check_row(app, 4)
    assert app.sheet_combo["values"] and app.tcol_combo["values"] and app.mapping_widgets
    broken = tmp_path / "unreadable.xlsx"
    broken.write_text("not an Excel workbook", encoding="utf-8")
    _browse(app, monkeypatch, app.excel_var, broken)

    assert app.excel_var.get() == str(broken)
    assert "失败" in app.status_var.get()
    assert not app.tree.get_children()
    assert not app.sheet_var.get() and not app.sheet_combo["values"]
    assert not app.tcol_var.get() and not app.tcol_combo["values"]
    assert not app.mapping_frame.winfo_children()
    assert app._current_settings().selected_rows == ()
    generate = Mock()
    monkeypatch.setattr(gui, "generate", generate)
    app.generate_btn.invoke()
    generate.assert_not_called()


@pytest.mark.parametrize("template_column", ["", "不在标题行中的列"], ids=["missing", "invalid"])
def test_invalid_template_column_prevents_generation_and_config_save(app, monkeypatch, template_column):
    _check_row(app, 3)
    assert app.tcol_var.get() == "模板"
    # Simulate an unset or stale selection without invalidating the loaded inputs.
    app.tcol_var.set(template_column)
    before = gui.CONFIG_PATH.read_bytes()
    generate, save_config = Mock(), Mock()
    monkeypatch.setattr(gui, "generate", generate)
    monkeypatch.setattr(gui, "save_config", save_config)

    app.generate_btn.invoke()

    gui.messagebox.showerror.assert_called_once()
    message = gui.messagebox.showerror.call_args.args[1]
    assert all(word in message for word in ("模板列", "下拉框", "选择"))
    generate.assert_not_called()
    save_config.assert_not_called()
    assert gui.CONFIG_PATH.read_bytes() == before
    assert not list(Path(app.excel_var.get()).parent.glob("output_*.pptx"))


def test_automatically_selected_template_column_generates_directly(app):
    actions = [
        widget for widget in app.generate_btn.master.winfo_children()
        if isinstance(widget, ttk.Button)
    ]
    assert actions == [app.generate_btn]
    assert app.tcol_combo.get() == "模板"
    _check_row(app, 3)

    app.generate_btn.invoke()

    gui.messagebox.showerror.assert_not_called()
    gui.messagebox.showinfo.assert_called_once()
    (output,) = Path(app.excel_var.get()).parent.glob("output_*.pptx")
    slides = gui.load_template(output).slides
    assert len(slides) == 1
    assert any(shape.has_text_frame and shape.text == DATA_ROWS[0][1] for shape in slides[0].shapes)
    assert gui.load_config(gui.CONFIG_PATH).template_column == "模板"


def test_template_column_changes_only_rebuild_when_visible_columns_change(app, monkeypatch):
    excel = Path(app.excel_var.get())
    workbook = load_workbook(excel)
    try:
        for _ in range(60):
            workbook[DATA_SHEET].append(DATA_ROWS[0])
        workbook.save(excel)
    finally:
        workbook.close()
    _browse(app, monkeypatch, app.excel_var, excel)
    _check_row(app, 3)
    original_columns = app.tree["columns"]
    original_rows = app.tree.get_children()
    app.tree.focus("3")  # Deleting and reinserting the row would discard its focus.
    app.tree.yview_moveto(0.5)
    app.root.update()
    original_view = app.tree.yview()
    assert original_view[0] > 0

    _choose(app, app.tcol_combo, "标题")
    assert app.tree["columns"] == original_columns
    assert app.tree.get_children() == original_rows
    assert app.tree.focus() == "3"
    assert app.tree.yview() == original_view
    assert _visible_checks(app) == app._current_settings().selected_rows == (3,)

    _choose(app, app.tcol_combo, "销售额")
    assert app.tree["columns"] == (*original_columns, "销售额")
    assert app.tree.set("4", "销售额") == "500万"
    assert _visible_checks(app) == app._current_settings().selected_rows == (3,)
