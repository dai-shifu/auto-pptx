"""Delayed, reusable overflow hints for the preview Treeview."""

import tkinter as tk
from dataclasses import dataclass
from tkinter import font as tkfont, ttk


@dataclass(frozen=True)
class _Target:
    region: str
    item: str
    column: str


class TreeviewTooltip:
    """Reveal clipped headings and values without changing preview data."""

    def __init__(self, tree: ttk.Treeview, delay_ms: int = 400) -> None:
        self.tree = tree
        self.delay_ms = delay_ms
        self._target: _Target | None = None
        self._pending: str | None = None
        self._leave_pending: str | None = None
        self._window: tk.Toplevel | None = None
        self._text: tk.Text | None = None
        self._scrollbar: ttk.Scrollbar | None = None
        self._font: tkfont.Font | None = None
        self._destroyed = False
        self._bindings = {
            sequence: tree.bind(sequence, callback, add="+")
            for sequence, callback in (
                ("<Motion>", self._on_motion),
                ("<Leave>", self._on_leave),
                # A specific existing Button-1 binding takes precedence over
                # generic <Button> bindings on the same bindtag.
                ("<Button-1>", self._on_click),
                ("<Button-2>", self._on_click),
                ("<Button-3>", self._on_click),
                ("<Button-4>", self._on_click),
                ("<Button-5>", self._on_click),
                ("<MouseWheel>", self._on_click),
                ("<Destroy>", self._on_destroy),
            )
        }

    def _target_at(self, x: int, y: int) -> _Target | None:
        region = self.tree.identify_region(x, y)
        if region not in ("heading", "cell"):
            return None
        column = self.tree.identify_column(x)
        if column in ("", "#0"):
            return None
        # The first displayed column in this preview holds checkboxes.
        if column == "#1":
            return None
        item = self.tree.identify_row(y) if region == "cell" else ""
        if region == "cell" and not item:
            return None
        return _Target(region, item, column)

    def _on_motion(self, event: tk.Event) -> None:
        if self._destroyed:
            return
        if self._window is not None and self._window.winfo_ismapped():
            # The tooltip may touch or overlap the Treeview near screen edges.
            # Ignore source motion delivered while crossing into that window.
            px = self.tree.winfo_rootx() + event.x
            py = self.tree.winfo_rooty() + event.y
            wx = self._window.winfo_rootx()
            wy = self._window.winfo_rooty()
            if (
                wx <= px < wx + self._window.winfo_width()
                and wy <= py < wy + self._window.winfo_height()
            ):
                self._cancel("_leave_pending")
                return
        target = self._target_at(event.x, event.y)
        if target == self._target:
            self._cancel("_leave_pending")
            return
        self.hide()
        if target is not None:
            self._target = target
            self._pending = self.tree.after(
                self.delay_ms, lambda: self._show(target),
            )

    def _cancel(self, attribute: str) -> None:
        callback_id = getattr(self, attribute)
        setattr(self, attribute, None)
        if callback_id is not None:
            try:
                self.tree.after_cancel(callback_id)
            except tk.TclError:
                pass

    def hide(self) -> None:
        """Cancel pending work and hide the hint before preview changes."""
        self._cancel("_pending")
        self._cancel("_leave_pending")
        self._target = None
        if self._window is not None:
            try:
                self._window.withdraw()
            except tk.TclError:
                pass

    def destroy(self) -> None:
        """Release timers, bindings, and the reusable tooltip window."""
        if self._destroyed:
            return
        self.hide()
        self._destroyed = True
        for sequence, binding_id in self._bindings.items():
            if binding_id:
                try:
                    self.tree.unbind(sequence, binding_id)
                except tk.TclError:
                    pass
        self._bindings.clear()
        if self._window is not None:
            try:
                self._window.destroy()
            except tk.TclError:
                pass
            self._window = None

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self.tree:
            self.destroy()

    def _on_click(self, event: tk.Event) -> None:
        self.hide()

    def _on_leave(self, event: tk.Event) -> None:
        if self._window is None or not self._window.winfo_ismapped():
            self.hide()
            return
        # Allow the pointer to transition from the source into the hint.
        self._cancel("_leave_pending")
        if not self._destroyed:
            self._leave_pending = self.tree.after(150, self._dismiss_outside)

    def _on_enter(self, event: tk.Event) -> None:
        self._cancel("_leave_pending")

    def _dismiss_outside(self) -> None:
        self._leave_pending = None
        if self._destroyed:
            return
        try:
            x, y = self.tree.winfo_pointerxy()
            widget = self.tree.winfo_containing(x, y)
            if self._window is not None and widget is not None:
                if widget is self._window or str(widget).startswith(
                    str(self._window) + ".",
                ):
                    return
            if widget is self.tree and self._target == self._target_at(
                x - self.tree.winfo_rootx(), y - self.tree.winfo_rooty(),
            ):
                return
        except tk.TclError:
            pass
        self.hide()

    def _content(self, target: _Target) -> tuple[str, tkfont.Font, tuple] | None:
        """Read only the current target and its theme/tag display font."""
        style = ttk.Style(self.tree)
        style_name = self.tree.cget("style") or "Treeview"
        if target.region == "heading":
            text = self.tree.heading(target.column, "text")
            font_name = style.lookup(style_name + ".Heading", "font")
            # Treeview has no heading bbox API; get its y boundaries from
            # the actual identified heading region at this column's center.
            x = self._column_x(target.column)
            width = int(self.tree.column(target.column, "width"))
            center = x + width // 2
            ys = [
                y for y in range(min(100, self.tree.winfo_height()))
                if self.tree.identify_region(center, y) == "heading"
            ]
            if not ys:
                return None
            bbox = (x, ys[0], width, ys[-1] - ys[0] + 1)
        else:
            if not self.tree.exists(target.item):
                return None
            bbox = self.tree.bbox(target.item, target.column)
            if not bbox:
                return None
            text = self.tree.set(target.item, target.column)
            font_name = style.lookup(style_name, "font", self.tree.state())
            for tag in self.tree.item(target.item, "tags"):
                tag_font = self.tree.tag_configure(tag, "font")
                if tag_font:
                    font_name = tag_font
                    break
        font = tkfont.Font(root=self.tree, font=font_name or "TkDefaultFont")
        return str(text), font, tuple(bbox)

    def _column_x(self, column: str) -> int:
        display = self.tree.cget("displaycolumns")
        if display == ("#all",) or display == "#all":
            display = self.tree.cget("columns")
        return 1 + sum(
            int(self.tree.column(other, "width"))
            for other in display[:int(column[1:]) - 1]
        )

    @staticmethod
    def _overflows(text: str, font: tkfont.Font, bbox: tuple) -> bool:
        if not text:
            return False
        lines = text.split("\n")
        return (
            max(font.measure(line) for line in lines) > max(0, bbox[2] - 8)
            or (
                len(lines) > 1
                and len(lines) * font.metrics("linespace") > max(0, bbox[3] - 4)
            )
        )

    def _show(self, target: _Target) -> None:
        if self._destroyed or target != self._target:
            return
        self._pending = None
        try:
            content = self._content(target)
            if content is None:
                self.hide()
                return
            text, font, bbox = content
            if not self._overflows(text, font, bbox):
                return
            self._show_window(text, font, bbox)
        except tk.TclError:
            self.hide()

    def _create_window(self) -> None:
        window = tk.Toplevel(self.tree)
        window.withdraw()
        window.overrideredirect(True)
        window.transient(self.tree.winfo_toplevel())
        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1)
        text = tk.Text(
            window, wrap="word", background="#ffffe0", foreground="#202020",
            relief="solid", borderwidth=1, padx=6, pady=5,
            cursor="arrow", takefocus=False, highlightthickness=0,
        )
        text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        for widget in (window, text, scrollbar):
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
        self._window = window
        self._text = text
        self._scrollbar = scrollbar

    def _show_window(self, value: str, font: tkfont.Font, bbox: tuple) -> None:
        if self._window is None:
            self._create_window()
        window, text, scrollbar = self._window, self._text, self._scrollbar
        # Text keeps only a Tcl font name; retain the Python owner while shown.
        self._font = font
        screen_width = self.tree.winfo_screenwidth()
        screen_height = self.tree.winfo_screenheight()
        width = min(
            600, screen_width - 20,
            max(120, max(font.measure(line) for line in value.split("\n")) + 32),
        )
        max_height = min(400, screen_height - 20)
        text.configure(state="normal", font=font)
        text.delete("1.0", "end")
        text.insert("1.0", value)
        text.configure(state="disabled")
        text.yview_moveto(0)
        scrollbar.grid()
        x = max(10, min(
            self.tree.winfo_rootx() + bbox[0], screen_width - width - 10,
        ))
        below = self.tree.winfo_rooty() + bbox[1] + bbox[3]
        initial_y = max(10, min(below, screen_height - max_height - 10))
        window.geometry(f"{width}x{max_height}+{x}+{initial_y}")
        # A withdrawn Toplevel does not apply its pixel geometry to Text.
        # Map it before querying wrapped lines, including when reusing it.
        window.deiconify()
        window.update_idletasks()
        # Query wrapped display lines after the Text's pixel width is set.
        lines = text.count("1.0", "end", "displaylines")
        needed = (lines[0] if lines else 1) * font.metrics("linespace") + 12
        height = min(max_height, max(font.metrics("linespace") + 12, needed))
        if needed <= max_height:
            scrollbar.grid_remove()
        y = below if below + height <= screen_height - 10 else (
            self.tree.winfo_rooty() + bbox[1] - height
        )
        y = max(10, min(y, screen_height - height - 10))
        window.geometry(f"{width}x{height}+{x}+{y}")
        window.deiconify()
        window.lift()
