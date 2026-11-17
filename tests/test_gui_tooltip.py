"""Actual Tk checks for overflow hints; run with Xvfb on headless hosts."""

import tkinter as tk
from tkinter import font as tkfont, ttk
from types import SimpleNamespace

import pytest

from src.gui_tooltip import TreeviewTooltip


@pytest.fixture
def preview():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk display unavailable: {exc}; run using xvfb-run")
    root.geometry("500x250+20+20")
    tree = ttk.Treeview(root, columns=("#", "value"), show="headings")
    tree.column("#", width=40, stretch=False)
    tree.column("value", width=120, stretch=False)
    tree.heading("#", text="☑")
    tree.heading("value", text="Value")
    tree.pack(fill="both", expand=True)
    tree.insert("", "end", iid="short", values=("☐", "ok"))
    tree.insert("", "end", iid="long", values=("☐", "Complete value " * 20))
    tree.insert("", "end", iid="multiline", values=("☐", "first\nsecond"))
    root.update()
    tooltip = TreeviewTooltip(tree)
    yield root, tree, tooltip
    tooltip.destroy()
    root.destroy()


def hover(tree, tooltip, item, column="#2"):
    x, y, width, height = tree.bbox(item, column)
    tooltip._on_motion(SimpleNamespace(x=x + width // 2, y=y + height // 2))
    return tooltip._target


def show(tree, tooltip, item):
    target = hover(tree, tooltip, item)
    tooltip._cancel("_pending")
    tooltip._show(target)


def test_only_clipped_and_multiline_values_show_and_remain_complete(preview):
    root, tree, tooltip = preview
    show(tree, tooltip, "short")
    assert tooltip._window is None
    show(tree, tooltip, "long")
    root.update_idletasks()
    window = tooltip._window
    assert window.winfo_ismapped()
    assert tooltip._text.get("1.0", "end-1c") == tree.set("long", "value")
    tooltip.hide()
    show(tree, tooltip, "multiline")
    assert tooltip._window is window
    assert tooltip._text.get("1.0", "end-1c") == "first\nsecond"
    assert tree.set("multiline", "value") == "first\nsecond"
    tooltip.hide()
    assert hover(tree, tooltip, "long", "#1") is None
    assert tooltip._pending is None


def test_same_target_motion_retains_timer_and_old_target_cannot_show(preview):
    root, tree, tooltip = preview
    first = hover(tree, tooltip, "long")
    pending = tooltip._pending
    for _ in range(20):
        hover(tree, tooltip, "long")
    assert tooltip._pending == pending
    next_target = hover(tree, tooltip, "multiline")
    assert next_target != first
    assert tooltip._pending != pending
    tooltip._show(first)
    assert tooltip._window is None
    tooltip.hide()
    tooltip._show(next_target)
    assert tooltip._window is None
    assert tooltip._pending is None


def test_heading_font_and_row_tag_font_measure_real_display(preview):
    root, tree, tooltip = preview
    style = ttk.Style(root)
    large = tkfont.Font(root, size=24)
    style.configure("HintTest.Treeview.Heading", font=large)
    tree.configure(style="HintTest.Treeview")
    tree.heading("value", text="WIDE WIDE WIDE")
    tree.column("value", width=50)
    root.update()
    heading_y = next(
        y for y in range(100) if tree.identify_region(70, y) == "heading"
    )
    tooltip._on_motion(SimpleNamespace(x=70, y=heading_y))
    content = tooltip._content(tooltip._target)
    assert content[1].actual("size") == large.actual("size")
    assert tooltip._overflows(*content)
    tooltip._cancel("_pending")
    tooltip._show(tooltip._target)
    assert tooltip._text.get("1.0", "end-1c") == "WIDE WIDE WIDE"
    tooltip.hide()
    tree.tag_configure("large", font=large)
    tree.item("short", values=("☐", "W" * 20), tags=("large",))
    target = hover(tree, tooltip, "short")
    assert tooltip._content(target)[1].actual("size") == large.actual("size")
    tooltip._cancel("_pending")
    tooltip._show(target)
    assert tooltip._text.get("1.0", "end-1c") == "W" * 20


def test_deleted_row_and_explicit_hide_clear_pending_callback(preview):
    root, tree, tooltip = preview
    target = hover(tree, tooltip, "long")
    tree.delete("long")
    tooltip._cancel("_pending")
    tooltip._show(target)
    assert tooltip._window is None
    assert tooltip._target is None
    hover(tree, tooltip, "multiline")
    callback_id = tooltip._pending
    assert callback_id in root.tk.call("after", "info")
    tooltip.hide()
    assert callback_id not in root.tk.call("after", "info")


def test_long_hint_fits_screen_and_can_scroll_without_truncation(preview):
    root, tree, tooltip = preview
    value = "很长的内容 " * 3000
    tree.set("long", "value", value)
    root.geometry("500x250+700+450")
    root.update()
    show(tree, tooltip, "long")
    root.update()
    window = tooltip._window
    assert tooltip._text.get("1.0", "end-1c") == value
    assert window.winfo_x() >= 0
    assert window.winfo_y() >= 0
    assert window.winfo_x() + window.winfo_width() <= root.winfo_screenwidth()
    assert window.winfo_y() + window.winfo_height() <= root.winfo_screenheight()
    assert tooltip._scrollbar.winfo_ismapped()
    tooltip._text.yview_moveto(1)
    root.update_idletasks()
    assert tooltip._text.yview()[0] > 0
    # Moving from the source into the hint must cancel dismissal.
    tooltip._on_leave(SimpleNamespace())
    assert tooltip._leave_pending is not None
    tooltip._on_enter(SimpleNamespace())
    assert tooltip._leave_pending is None


def test_click_binding_preserved_and_destruction_cancels_timers(preview):
    root, tree, tooltip = preview
    tooltip.destroy()
    clicks = []
    tree.bind("<Button-1>", lambda event: clicks.append(event.x))
    replacement = TreeviewTooltip(tree)
    hover(tree, replacement, "long")
    tree.event_generate("<Button-1>", x=60, y=50)
    root.update()
    assert clicks == [60]
    assert replacement._pending is None
    show(tree, replacement, "long")
    window = replacement._window
    replacement.hide()
    hover(tree, replacement, "multiline")
    callback = replacement._pending
    tree.destroy()
    root.update()
    assert replacement._destroyed
    assert callback not in root.tk.call("after", "info")
    assert not window.winfo_exists()
    replacement.destroy()


def test_hover_delay_completes_under_repeated_motion_in_300_rows(preview):
    root, tree, tooltip = preview
    for row in range(297):
        tree.insert("", "end", values=("☐", f"row {row}"))
    tooltip.delay_ms = 20
    hover(tree, tooltip, "long")
    for delay in (3, 6, 9, 12, 15):
        root.after(delay, lambda: hover(tree, tooltip, "long"))
    root.after(50, root.quit)
    root.mainloop()
    assert tooltip._pending is None
    assert tooltip._window.winfo_ismapped()
    assert len(tree.get_children()) == 300


def test_full_heading_empty_value_and_leaving_before_delay_show_nothing(preview):
    root, tree, tooltip = preview
    y = next(y for y in range(100) if tree.identify_region(70, y) == "heading")
    tooltip._on_motion(SimpleNamespace(x=70, y=y))
    tooltip._cancel("_pending")
    tooltip._show(tooltip._target)
    assert tooltip._window is None
    tree.set("short", "value", "")
    show(tree, tooltip, "short")
    assert tooltip._window is None
    hover(tree, tooltip, "long")
    callback = tooltip._pending
    tooltip._on_leave(SimpleNamespace())
    assert tooltip._pending is None
    assert callback not in root.tk.call("after", "info")


def test_real_pointer_can_cross_from_cell_into_hint_and_leave_both(preview):
    root, tree, tooltip = preview
    x, y, width, height = tree.bbox("long", "#2")
    pointer_x = x + width // 2
    tree.event_generate("<Motion>", x=pointer_x, y=y + height // 2, warp=True)
    root.update()
    tooltip._cancel("_pending")
    tooltip._show(tooltip._target)
    root.update()
    window = tooltip._window
    # Move in single-pixel steps so the source-to-popup boundary is exercised.
    for pointer_y in range(y + height // 2, y + height + 10):
        tree.event_generate("<Motion>", x=pointer_x, y=pointer_y, warp=True)
        root.update()
    root.after(180, root.quit)
    root.mainloop()
    assert window.winfo_ismapped()
    pointer_widget = tree.winfo_containing(*tree.winfo_pointerxy())
    assert str(pointer_widget).startswith(str(window) + ".")
    tree.event_generate("<Motion>", x=5, y=5, warp=True)
    root.update()
    root.after(180, root.quit)
    root.mainloop()
    assert not window.winfo_ismapped()


def test_short_clipped_hint_has_compact_height_after_initial_show_and_reuse(preview):
    root, tree, tooltip = preview
    short = "Complete explanation " * 5
    tree.set("long", "value", short)
    show(tree, tooltip, "long")
    root.update_idletasks()
    window = tooltip._window

    def assert_compact():
        lines = tooltip._text.count("1.0", "end", "displaylines")[0]
        line_height = tooltip._font.metrics("linespace")
        expected = lines * line_height + 12
        assert expected < 200
        assert window.winfo_height() <= expected + line_height
        assert not tooltip._scrollbar.winfo_ismapped()
        assert tooltip._text.get("1.0", "end-1c") == short

    assert_compact()
    tooltip.hide()
    tree.set("long", "value", "Very long explanation " * 3000)
    show(tree, tooltip, "long")
    root.update_idletasks()
    assert window.winfo_height() == 400
    assert tooltip._scrollbar.winfo_ismapped()
    tooltip.hide()
    tree.set("long", "value", short)
    show(tree, tooltip, "long")
    root.update_idletasks()
    assert tooltip._window is window
    assert_compact()
