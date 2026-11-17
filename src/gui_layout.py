"""Resizable workspace and independently scrolling mapping controls."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk


def preview_column_widths(inner_width: int, count: int) -> list[int]:
    """Divide the viewport budget without changing the fixed 40px checkbox."""
    if count <= 0:
        return []
    budget = max(0, inner_width - 40)
    width, remainder = divmod(min(budget, count * 200), count)
    return [width + (index < remainder) for index in range(count)]


def wheel_units(event: tk.Event, window_system: str) -> int:
    """Normalize wheel events without losing macOS's small deltas."""
    if getattr(event, "num", None) in (4, 5):
        return -1 if event.num == 4 else 1
    delta = getattr(event, "delta", 0)
    if not delta:
        return 0
    if window_system == "aqua":
        return -int(delta)
    if abs(delta) >= 120:
        return -int(delta / 120)
    return -1 if delta > 0 else 1


class Workspace(ttk.Panedwindow):
    """Vertical panes with bounded sash movement and proportional resizing."""

    def __init__(
        self, master: tk.Misc, on_adjust: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master, orient="vertical")
        self._ratio = 0.7
        self._pending: str | None = None
        self._dragging = False
        self._released = False
        self._on_adjust = on_adjust
        self.bind("<Configure>", self._schedule)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._schedule)
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<Destroy>", self._destroy)

    def _press(self, event: tk.Event) -> None:
        self._dragging = self.identify(event.x, event.y) != ""
        if self._dragging and self._on_adjust:
            self._on_adjust()

    def _release(self, _event: tk.Event) -> None:
        # The class binding finishes moving the sash before this idle callback.
        self._released = True
        self._schedule()

    def _schedule(self, _event=None) -> None:
        if self._on_adjust:
            self._on_adjust()
        if self._pending is None:
            self._pending = self.after_idle(self._adjust)

    def _adjust(self) -> None:
        self._pending = None
        if len(self.panes()) != 2 or self.winfo_height() < 285:
            return
        first, second = [self.nametowidget(name) for name in self.panes()]
        sash_size = max(1, second.winfo_y() - first.winfo_height())
        available = self.winfo_height() - sash_size
        position = (
            self.sashpos(0) if self._dragging else round(available * self._ratio)
        )
        position = min(max(180, position), available - 100)
        if self.sashpos(0) != position:
            self.sashpos(0, position)
        if self._dragging:
            self._ratio = position / available
        if self._released:
            self._dragging = False
            self._released = False

    def _destroy(self, event: tk.Event) -> None:
        if event.widget is self and self._pending is not None:
            self.after_cancel(self._pending)
            self._pending = None


class MappingPane(ttk.Frame):
    """Mapping cells reflow inside a bounded, locally scrollable canvas."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=10)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(
            self, text="映射配置 (自动检测，可手动调整)", font=("", 9, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        background = ttk.Style(self).lookup("TFrame", "background") or "#f0f0f0"
        self.canvas = tk.Canvas(
            self, width=1, height=1, highlightthickness=0, background=background,
            yscrollincrement=24,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(self, command=self.canvas.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.content = ttk.Frame(self.canvas)
        self._window = self.canvas.create_window(
            0, 0, window=self.content, anchor="nw",
        )
        self._cells: list[ttk.Frame] = []
        self._columns = 0
        self._wheel_tag = f"MappingWheel{id(self)}"
        self._window_system = self.tk.call("tk", "windowingsystem")
        self.bind_class(self._wheel_tag, "<MouseWheel>", self._wheel)
        # Use the binding's direction: Tk 8/9 expose different button numbers.
        for sequence, direction in (("<Button-4>", -1), ("<Button-5>", 1)):
            self.bind_class(
                self._wheel_tag, sequence,
                lambda event, units=direction: self._wheel(event, units),
            )
        self._tag_wheel(self.canvas)
        self.canvas.bind("<Configure>", self._resize)
        self.content.bind("<Configure>", self._update_region)
        self.bind("<Destroy>", self._destroy)

    def clear(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()
        self._cells.clear()
        self._columns = 0
        self.canvas.yview_moveto(0)
        self.canvas.configure(scrollregion=(0, 0, 0, 0))

    def set_cells(self, cells: list[ttk.Frame]) -> None:
        self._cells = cells
        self._columns = 0
        for cell in cells:
            self._tag_wheel(cell)
        self._reflow(self.canvas.winfo_width())

    def _tag_wheel(self, widget: tk.Misc) -> None:
        # Comboboxes retain their own class wheel behavior.
        if not isinstance(widget, ttk.Combobox):
            tags = widget.bindtags()
            widget.bindtags((tags[0], self._wheel_tag, *tags[1:]))
        for child in widget.winfo_children():
            self._tag_wheel(child)

    def _wheel(self, event: tk.Event, direction: int | None = None) -> str:
        units = (
            wheel_units(event, self._window_system)
            if direction is None else direction
        )
        if units and self.canvas.yview() != (0.0, 1.0):
            self.canvas.yview_scroll(units, "units")
        return "break"

    def _resize(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self._window, width=event.width)
        self._reflow(event.width)

    def _reflow(self, width: int) -> None:
        if not self._cells or width <= 1:
            return
        columns = max(1, min(4, width // 300))
        if columns == self._columns:
            return
        for index in range(4):
            self.content.columnconfigure(index, weight=1 if index < columns else 0)
        for index, cell in enumerate(self._cells):
            cell.grid(
                row=index // columns, column=index % columns, sticky="ew",
                padx=(0, 10), pady=2,
            )
        self._columns = columns

    def _update_region(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox(self._window))

    def _destroy(self, event: tk.Event) -> None:
        if event.widget is self:
            for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                self.unbind_class(self._wheel_tag, sequence)
