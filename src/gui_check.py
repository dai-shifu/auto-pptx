"""GUI for viewing a local check and copying an editable share summary."""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from .input_check import CheckReport, format_check_report


class CheckDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, report: CheckReport) -> None:
        super().__init__(parent)
        self.title("检查当前设置")
        self.transient(parent)
        self.bind("<Escape>", lambda _event: self.destroy())
        self._report = report
        self.preview_window: tk.Toplevel | None = None
        self.report_text = _text_box(self, format_check_report(report))
        self.report_text.configure(state="disabled")

        bar = ttk.Frame(self, padding=(12, 0, 12, 12))
        bar.pack(fill="x")
        ttk.Button(bar, text="预览分享摘要", command=self.preview_summary).pack(side="left")
        ttk.Button(bar, text="关闭", command=self.destroy).pack(side="right")

    def preview_summary(self) -> None:
        if self.preview_window is not None and self.preview_window.winfo_exists():
            self.preview_window.lift()
            return

        preview = self.preview_window = tk.Toplevel(self)
        preview.title("预览分享摘要")
        preview.transient(self)
        preview.bind("<Escape>", lambda _event: preview.destroy())
        ttk.Label(
            preview, padding=(12, 12, 12, 0), wraplength=450, justify="left",
            text="摘要不包含路径或单元格正文。列名和模板名也可能敏感，请审阅并删改后再复制。程序不会发送摘要。",
        ).pack(anchor="w")
        summary = _text_box(preview, format_check_report(self._report, for_sharing=True))

        def copy_summary() -> None:
            self.clipboard_clear()
            self.clipboard_append(summary.get("1.0", "end-1c"))
            preview.destroy()

        bar = ttk.Frame(preview, padding=(12, 0, 12, 12))
        bar.pack(fill="x")
        ttk.Button(bar, text="复制摘要", command=copy_summary).pack(side="left")
        ttk.Button(bar, text="取消", command=preview.destroy).pack(side="right")
        summary.focus_set()


def _text_box(window: tk.Toplevel, text: str) -> ScrolledText:
    box = ScrolledText(window, width=72, height=22, wrap="word", font="TkDefaultFont")
    box.pack(fill="both", expand=True, padx=12, pady=12)
    box.insert("1.0", text)
    return box
