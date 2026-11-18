"""Real Tk geometry and state regressions for the bounded GUI workspace."""

from types import SimpleNamespace
import tkinter as tk
from tkinter import ttk

import pytest

from src import gui
from src.gui_layout import preview_column_widths, wheel_units


def _settle(root: tk.Tk) -> None:
    """Run geometry and idle callbacks, including callbacks scheduled by layout."""
    for _ in range(4):
        root.update_idletasks()
        root.update()


@pytest.fixture
def layout_app(monkeypatch, request):
    try:
        root = tk.Tk()
    except tk.TclError as error:
        if request.config.getoption("--require-gui"):
            pytest.fail(f"Required Tk display unavailable: {error}")
        pytest.skip(f"Real Tk layout requires a display or Xvfb: {error}")
    root.geometry("1400x850")
    root.minsize(1000, 600)
    monkeypatch.setattr(gui.App, "_auto_load_config", lambda _self: None)
    app = gui.App(root)
    app._headers = [f"数据列 {index} 很长的列名" for index in range(40)] + ["模板"]
    app._rows = [
        [f"第{row}行，第{column}列，完整文本" * 8 for column in range(40)] + ["cover"]
        for row in range(300)
    ]
    app._header_row = 3
    app.hrow_var.set(3)
    app.tcol_var.set("模板")
    app._placeholders = ["报告标题", "备注"]
    app._rebuild_treeview()
    app._rebuild_mapping()
    _settle(root)
    try:
        yield app
    finally:
        root.destroy()


@pytest.mark.parametrize("count", [0, 1, 3, 5, 6])
@pytest.mark.parametrize("width", [0, 39, 40, 41, 523, 980, 1370, 3000])
def test_preview_widths_respect_viewport_and_cap(width, count):
    widths = preview_column_widths(width, count)

    assert len(widths) == count
    assert all(0 <= value <= 200 for value in widths)
    assert sum(widths) <= max(0, width - 40)
    if widths:
        assert max(widths) - min(widths) <= 1
        assert sum(widths) == min(max(0, width - 40), 200 * count)


@pytest.mark.parametrize(
    "event,system,expected",
    [
        (SimpleNamespace(num=4), "x11", -1),
        (SimpleNamespace(num=5), "x11", 1),
        (SimpleNamespace(delta=120), "win32", -1),
        (SimpleNamespace(delta=-240), "win32", 2),
        (SimpleNamespace(delta=1), "aqua", -1),
        (SimpleNamespace(delta=-3), "aqua", 3),
        (SimpleNamespace(delta=0), "aqua", 0),
        (SimpleNamespace(delta=20), "x11", -1),
        (SimpleNamespace(), "x11", 0),
    ],
)
def test_wheel_units_cover_platform_event_formats(event, system, expected):
    assert wheel_units(event, system) == expected


def _assert_visible_inside_root(widget, root):
    assert widget.winfo_ismapped()
    assert widget.winfo_width() > 1
    assert widget.winfo_height() > 1
    left = widget.winfo_rootx() - root.winfo_rootx()
    top = widget.winfo_rooty() - root.winfo_rooty()
    assert 0 <= left < root.winfo_width()
    assert 0 <= top < root.winfo_height()
    assert left + widget.winfo_width() <= root.winfo_width()
    assert top + widget.winfo_height() <= root.winfo_height()


@pytest.mark.parametrize("geometry", ["1400x850", "1000x600"])
def test_300_rows_and_many_mappings_remain_within_window(layout_app, geometry):
    app = layout_app
    app.root.geometry(geometry)
    _settle(app.root)

    for widget in (
        app.tree, app.tree_scroll, app.mapping_pane.canvas,
        app.mapping_pane.scrollbar, app.generate_btn, app.sheet_combo,
        app.hrow_spin, app.tcol_combo,
    ):
        _assert_visible_inside_root(widget, app.root)
    assert app.preview_frame.winfo_height() >= 180
    assert app.mapping_pane.winfo_height() >= 100
    assert len(app.tree.get_children()) == 300
    assert tuple(app.tree["columns"]) == ("#", *app._headers[:5], "模板")
    assert app.tree.column("#", "width") == 40
    widths = [app.tree.column(column, "width") for column in app.tree["columns"][1:]]
    assert all(80 <= width <= 200 for width in widths)
    assert 40 + sum(widths) <= app.tree.winfo_width() - 2
    assert not app.tree.cget("xscrollcommand")
    assert app.mapping_pane.canvas.yview()[1] < 1

    app.tree.yview_moveto(1)
    _settle(app.root)
    last_id = str(app._header_row + len(app._rows))
    x, y, width, height = app.tree.bbox(last_id, "#")
    assert x + width <= app.tree.winfo_width()
    app.tree.event_generate("<Button-1>", x=x + width // 2, y=y + height // 2)
    _settle(app.root)
    assert app._checked == {303}
    assert app.tree.set(last_id, "#") == "☑"

    app.mapping_pane.canvas.yview_moveto(1)
    _settle(app.root)
    last_cell = app.mapping_frame.winfo_children()[-1]
    last_combo = next(child for child in last_cell.winfo_children() if isinstance(child, ttk.Combobox))
    _assert_visible_inside_root(last_combo, app.root)


def _drag_divider(app, target):
    workspace = app.workspace
    x = workspace.winfo_width() // 2
    start = workspace.sashpos(0) + 2
    workspace.event_generate("<ButtonPress-1>", x=x, y=start)
    workspace.event_generate("<B1-Motion>", x=x, y=target)
    _settle(app.root)
    workspace.event_generate("<ButtonRelease-1>", x=x, y=target)
    _settle(app.root)


def test_divider_limits_and_resizes_preserve_adjusted_proportion(layout_app):
    app = layout_app
    initial = app.preview_frame.winfo_height() / app.workspace.winfo_height()
    assert initial == pytest.approx(0.7, abs=0.03)

    _drag_divider(app, 1)
    assert app.preview_frame.winfo_height() >= 180
    _drag_divider(app, app.workspace.winfo_height() - 1)
    assert app.mapping_pane.winfo_height() >= 100

    _drag_divider(app, app.workspace.winfo_height() // 2)
    adjusted = app.preview_frame.winfo_height() / app.workspace.winfo_height()
    assert adjusted == pytest.approx(0.5, abs=0.04)
    app.root.geometry("1200x800")
    _settle(app.root)
    resized = app.preview_frame.winfo_height() / app.workspace.winfo_height()
    assert resized == pytest.approx(adjusted, abs=0.03)
    app.root.geometry("1000x600")
    _settle(app.root)
    assert app.preview_frame.winfo_height() >= 180
    assert app.mapping_pane.winfo_height() >= 100
    _assert_visible_inside_root(app.generate_btn, app.root)


def test_mapping_reflow_and_layout_keep_state_and_generation_arguments(layout_app, monkeypatch, tmp_path):
    app = layout_app
    header, variable = app.mapping_widgets[0]
    variable.set("报告标题")
    app._remember_mapping(header, variable.get())
    app._checked.update({4, 303})
    app.tree.set("4", "#", "☑")
    app.tree.set("303", "#", "☑")
    original_cells = tuple(app.mapping_frame.winfo_children())
    original_variables = tuple(var for _, var in app.mapping_widgets)
    original_rows = app.tree.get_children()
    wide_columns = len({int(cell.grid_info()["column"]) for cell in original_cells})
    original_values = app.tree.item("4", "values")

    for geometry in ("1000x600", "1400x850", "1000x600"):
        app.root.geometry(geometry)
        _settle(app.root)
    narrow_columns = len({int(cell.grid_info()["column"]) for cell in original_cells})
    assert 1 <= narrow_columns < wide_columns <= 4
    assert tuple(app.mapping_frame.winfo_children()) == original_cells
    assert tuple(var for _, var in app.mapping_widgets) == original_variables
    assert variable.get() == "报告标题"
    assert app._explicit_mapping == {header: "报告标题"}
    assert app._checked == {4, 303}
    assert app.tcol_var.get() == "模板"
    assert app.tree.get_children() == original_rows
    assert app.tree.item("4", "values") == original_values

    received = {}

    def fake_generate(*args, **kwargs):
        received["args"] = args
        received["kwargs"] = kwargs
        return SimpleNamespace(generated_pages=2, output_path=tmp_path / "output.pptx", warnings=())

    monkeypatch.setattr(gui, "generate", fake_generate)
    monkeypatch.setattr(gui, "load_template", lambda _path: object())
    monkeypatch.setattr(gui, "save_config", lambda *_args: None)
    monkeypatch.setattr(gui, "CONFIG_PATH", tmp_path / "config.toml")
    monkeypatch.setattr(gui.messagebox, "showinfo", lambda *_args: None)
    monkeypatch.setattr(
        gui.messagebox, "showerror", lambda _title, message: pytest.fail(message),
    )
    app.tpl_var.set(str(tmp_path / "template.pptx"))
    app.excel_var.set(str(tmp_path / "data.xlsx"))
    app.sheet_var.set("Sheet1")
    app._generate()

    assert received["args"][3] == [4, 303]
    assert received["kwargs"]["mapping"] == {header: "报告标题"}
    assert received["kwargs"]["template_column"] == "模板"
    assert received["kwargs"]["header_row"] == 3


def test_wheel_scrolls_mapping_and_tree_independently(layout_app):
    app = layout_app
    canvas = app.mapping_pane.canvas
    app.tree.yview_moveto(0)
    canvas.yview_moveto(0)
    _settle(app.root)
    first_cell = app.mapping_frame.winfo_children()[0]
    label = next(child for child in first_cell.winfo_children() if isinstance(child, ttk.Label))
    combo = next(child for child in first_cell.winfo_children() if isinstance(child, ttk.Combobox))
    assert app.mapping_pane._wheel_tag not in combo.bindtags()
    tree_before = app.tree.yview()
    mapping_before = canvas.yview()
    def scroll_down(widget):
        if app.root.tk.call("tk", "windowingsystem") == "x11":
            widget.event_generate("<Button-5>", x=2, y=2)
        else:
            widget.event_generate("<MouseWheel>", x=2, y=2, delta=-120)

    scroll_down(label)
    _settle(app.root)
    assert canvas.yview()[0] > mapping_before[0]
    assert app.tree.yview() == tree_before

    mapping_after = canvas.yview()
    scroll_down(app.tree)
    _settle(app.root)
    assert app.tree.yview()[0] > tree_before[0]
    assert canvas.yview() == mapping_after
