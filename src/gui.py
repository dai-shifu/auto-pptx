"""tkinter GUI：单 Excel + 可视化行选择工作流。"""
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .auto_detect import (
    TemplateMetadata,
    analyze_template,
    detect_from_metadata,
    detect_header_row,
)
from .config import Config, load_config, save_config
from .excel_reader import read_sheet_rows
from .gui_check import CheckDialog
from .gui_layout import (
    MappingPane,
    Workspace,
    configure_preview_row_height,
    preview_column_widths,
)
from .gui_tooltip import TreeviewTooltip
from .generator import generate
from .input_check import CheckSettings, check_inputs
from .pptx_engine import load_template

def _get_config_path() -> Path:
    """返回 config.toml 路径。exe 同目录（打包）或项目根目录（开发），均由 sys.argv[0] 自动定位。"""
    return Path(sys.argv[0]).resolve().parent / "config.toml"


CONFIG_PATH = _get_config_path()


def _preview_columns(
    headers: list[str], template_column: str = "",
) -> list[tuple[int, str]]:
    """返回前五列，并在必要时追加当前模板列。"""
    columns = list(enumerate(headers[:5]))
    visible_headers = {header for _, header in columns}
    if template_column and template_column not in visible_headers:
        try:
            template_index = headers.index(template_column)
        except ValueError:
            pass
        else:
            columns.append((template_index, template_column))
    return columns


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Auto PPTX Generator")
        root.resizable(True, True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        # ── 模板 PPT ──
        frm = ttk.Frame(root, padding=10)
        frm.grid(row=0, column=0, sticky="ew")
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="模板 PPT:").grid(row=0, column=0, sticky="w")
        self.tpl_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.tpl_var, width=50).grid(
            row=0, column=1, padx=5, sticky="ew",
        )
        ttk.Button(frm, text="浏览", command=self._browse_tpl).grid(row=0, column=2)

        # ── Excel 文件 ──
        ttk.Label(frm, text="Excel 文件:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.excel_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.excel_var, width=50).grid(
            row=1, column=1, padx=5, pady=(5, 0), sticky="ew",
        )
        ttk.Button(frm, text="浏览", command=self._browse_excel).grid(row=1, column=2, pady=(5, 0))

        # ── Sheet 选择 + 标题行 + 模板列 ──
        sheet_frm = ttk.Frame(root, padding=10)
        sheet_frm.grid(row=1, column=0, sticky="ew")
        sheet_frm.columnconfigure(1, weight=1)
        sheet_frm.columnconfigure(5, weight=1)
        ttk.Label(sheet_frm, text="Sheet:").grid(row=0, column=0)
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(sheet_frm, textvariable=self.sheet_var, width=25, state="readonly")
        self.sheet_combo.grid(row=0, column=1, sticky="ew", padx=5)
        self.sheet_combo.bind("<<ComboboxSelected>>", self._on_sheet_change)

        ttk.Label(sheet_frm, text="标题行:").grid(row=0, column=2, padx=(20, 0))
        self.hrow_var = tk.IntVar(value=1)
        self.hrow_spin = ttk.Spinbox(sheet_frm, textvariable=self.hrow_var, from_=1, to=15, width=4,
                                     command=self._on_header_row_change)
        self.hrow_spin.grid(row=0, column=3, padx=5)

        ttk.Label(sheet_frm, text="模板列:").grid(row=0, column=4, padx=(20, 0))
        self.tcol_var = tk.StringVar()
        self.tcol_combo = ttk.Combobox(sheet_frm, textvariable=self.tcol_var, width=15, state="readonly")
        self.tcol_combo.grid(row=0, column=5, sticky="ew", padx=5)
        self.tcol_combo.bind("<<ComboboxSelected>>", self._on_tcol_change)

        # ── Treeview 数据预览 ──
        self.workspace = Workspace(root, on_adjust=self._hide_tooltip)
        self.workspace.grid(row=2, column=0, sticky="nsew")
        tree_frm = self.preview_frame = ttk.Frame(self.workspace, padding=10)
        tree_frm.columnconfigure(0, weight=1)
        tree_frm.rowconfigure(2, weight=1)
        self.workspace.add(tree_frm, weight=7)

        ttk.Label(
            tree_frm, text="数据预览 (☑ = 生成)", font=("", 9, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        btn_row = ttk.Frame(tree_frm)
        btn_row.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        ttk.Button(btn_row, text="全选", command=self._select_all).pack(side="left", padx=(0, 5))
        ttk.Button(btn_row, text="取消全选", command=self._deselect_all).pack(side="left")

        columns = ("#",)
        table = ttk.Frame(tree_frm)
        table.grid(row=2, column=0, sticky="nsew")
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(table, columns=columns, show="headings", height=12)
        if root.tk.call("tk", "windowingsystem") == "win32":
            configure_preview_row_height(self.tree)
        self.tree.heading("#", text="☑")
        self.tree.column("#", width=40, minwidth=40, anchor="center", stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree_scroll = ttk.Scrollbar(
            table, orient="vertical", command=self.tree.yview,
        )
        self.tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self._on_tree_scroll)

        self.tree.bind("<Button-1>", self._on_tree_click)
        # Explicit Linux wheel bindings also work on Tk 9, which omits these.
        self.tree.bind("<Button-4>", lambda _event: self._scroll_tree(-1))
        self.tree.bind("<Button-5>", lambda _event: self._scroll_tree(1))
        self.tree.bind("<Configure>", self._resize_tree_columns)
        self.tooltip = TreeviewTooltip(self.tree)

        # ── 映射区 ──
        self.mapping_pane = MappingPane(self.workspace)
        self.workspace.add(self.mapping_pane, weight=3)
        self.mapping_frame = self.mapping_pane.content
        self.mapping_widgets: list[tuple[str, tk.StringVar]] = []

        # ── 生成按钮 + 状态 ──
        btn_frm = ttk.Frame(root, padding=10)
        btn_frm.grid(row=3, column=0, sticky="ew")
        btn_frm.columnconfigure(2, weight=1)
        self.generate_btn = ttk.Button(btn_frm, text="生成 PPT", command=self._generate)
        self.generate_btn.grid(row=0, column=0, sticky="w")
        self.check_btn = ttk.Button(btn_frm, text="检查当前设置", command=self._check_current)
        self.check_btn.grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(btn_frm, textvariable=self.status_var, width=1).grid(
            row=0, column=2, sticky="ew", padx=10,
        )
        self._check_window: CheckDialog | None = None

        # 内部状态
        self._headers: list[str] = []
        self._rows: list[list[str]] = []
        self._checked: set[int] = set()
        self._placeholders: list[str] = []
        self._auto_mapping: dict[str, str] = {}  # excel_col → placeholder
        self._explicit_mapping: dict[str, str | None] = {}
        self._template_cache_key: tuple[str, int, int] | None = None
        self._template_metadata: TemplateMetadata | None = None

        # 来源标记：区分 config.toml 加载值和 auto_detect 临时值
        self._mapping_from_config: bool = False
        self._preferred_template_column: str | None = None

        # 标题行：可通过 Spinbox 或 auto-detect 设置
        self._header_row: int = 1
        self._hrow_from_config: bool = False

        # 启动时加载 config.toml
        self._auto_load_config()

    # ── 文件浏览 ──

    def _browse_tpl(self):
        path = filedialog.askopenfilename(filetypes=[("PPT 文件", "*.pptx")])
        if path:
            self.tpl_var.set(path)
            self._refresh_all()

    def _browse_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel 文件", "*.xlsx")])
        if path:
            self.excel_var.set(path)
            self._update_sheets(path)

    def _update_sheets(self, excel_path: str):
        try:
            from openpyxl import load_workbook
            wb = load_workbook(excel_path, read_only=True)
            sheets = wb.sheetnames
            wb.close()
            self.sheet_combo["values"] = sheets
            if sheets:
                self.sheet_var.set(sheets[0])
                self._refresh_all()
            else:
                self._set_template_columns([])
        except Exception as e:
            self._set_template_columns([])
            self.status_var.set(f"读取 Sheet 失败: {e}")

    def _on_sheet_change(self, _event=None):
        self._refresh_all()

    def _on_tcol_change(self, _event=None):
        # 模板列切换时重建 Treeview（关键列可能变），保留勾选
        self._preferred_template_column = self.tcol_var.get() or None
        self._rebuild_treeview(preserve_checks=True)

    def _on_header_row_change(self):
        self._header_row = self.hrow_var.get()
        self._hrow_from_config = True  # 用户手动选择，阻止 auto-detect 覆盖
        self._refresh_all()

    # ── 刷新逻辑 ──

    def _set_template_columns(self, headers: list[str]) -> None:
        columns = [header for header in headers if header]
        self.tcol_combo["values"] = columns
        preferred = self._preferred_template_column
        self.tcol_var.set(preferred if preferred in columns else "")

    def _refresh_all(self):
        """Sheet 切换或 PPT/Excel 变化时刷新 Treeview 和映射。"""
        excel_path = self.excel_var.get()
        sheet_name = self.sheet_var.get()
        tpl_path = self.tpl_var.get()

        if not excel_path or not sheet_name:
            self._set_template_columns([])
            return

        try:
            # 自动检测标题行（仅在未由 config 指定时）
            if not self._hrow_from_config and tpl_path:
                self._detect_header_row(excel_path, sheet_name, tpl_path)

            self._headers, self._rows = read_sheet_rows(
                excel_path, sheet_name, header_row=self._header_row,
            )
            self._set_template_columns(self._headers)
            if tpl_path:
                self._auto_detect()
            self._rebuild_treeview()
            self._rebuild_mapping()
        except Exception as e:
            self._set_template_columns([])
            self.status_var.set(f"加载数据失败: {e}")

    def _detect_header_row(self, excel_path: str, sheet_name: str, tpl_path: str):
        """扫描前 5 行，自动判定标题行（模板名交集占比最低的行）。"""
        try:
            temp_headers, temp_rows = read_sheet_rows(excel_path, sheet_name, header_row=1)
            if not temp_rows:
                return  # 只有标题行时无需检测
            metadata = self._template_metadata_for(tpl_path)
            tpl_names = set(metadata.template_names)
            if tpl_names:
                # 构建候选行：第 1 行 headers + 后续数据行（共最多 5 行）
                detect_rows = [temp_headers] + temp_rows[:4]
                self._header_row = detect_header_row(tpl_names, detect_rows)
                self.hrow_var.set(self._header_row)
        except Exception:
            pass  # 检测失败，保持当前值

    def _auto_detect(self):
        """自动检测模板列和映射。"""
        tpl_path = self.tpl_var.get()
        if not tpl_path or not self._headers:
            return

        try:
            metadata = self._template_metadata_for(tpl_path)
            detection = detect_from_metadata(metadata, self._headers, self._rows)
            # 映射建议依赖当前 Excel/Sheet/标题行，每次数据刷新都重新计算。
            # config 和用户手动选择保存在 _explicit_mapping 中并在 UI 层覆盖建议。
            self._auto_mapping = detection.mapping  # {excel_col: placeholder}
            self._placeholders = list(metadata.placeholders)

            if self._preferred_template_column not in self._headers:
                self.tcol_var.set(detection.template_column or "")

            if detection.conflicts:
                names = ", ".join(conflict.placeholder for conflict in detection.conflicts)
                self.status_var.set(f"自动映射存在冲突，请手动确认: {names}")

        except Exception as e:
            self.status_var.set(f"自动检测失败: {e}")

    def _template_metadata_for(self, template_path: str) -> TemplateMetadata:
        """仅缓存由 PPT 决定的元数据；Excel 相关检测始终重新执行。"""
        path = Path(template_path).resolve()
        stat = path.stat()
        cache_key = (str(path), stat.st_mtime_ns, stat.st_size)
        if cache_key != self._template_cache_key or self._template_metadata is None:
            self._template_metadata = analyze_template(load_template(path))
            self._template_cache_key = cache_key
        return self._template_metadata

    # ── Treeview ──

    def _hide_tooltip(self) -> None:
        tooltip = getattr(self, "tooltip", None)
        if tooltip is not None:
            tooltip.hide()

    def _on_tree_scroll(self, first: str, last: str) -> None:
        self._hide_tooltip()
        self.tree_scroll.set(first, last)

    def _scroll_tree(self, units: int) -> str:
        self._hide_tooltip()
        self.tree.yview_scroll(units, "units")
        return "break"

    def _resize_tree_columns(self, _event=None) -> None:
        """Resize columns only; keep row items, selection and full values intact."""
        width = self.tree.winfo_width()
        if width <= 42:
            return
        columns = self.tree["columns"][1:]
        width_key = (width, columns)
        if getattr(self, "_tree_width_key", None) == width_key:
            return
        self._tree_width_key = width_key
        self._hide_tooltip()
        # bbox exposes the theme's real left inset (border width varies by theme).
        visible_row = self.tree.identify_row(self.tree.winfo_height() // 2)
        bounds = self.tree.bbox(visible_row, "#1") if visible_row else ()
        inset = bounds[0] if bounds else 2
        widths = preview_column_widths(width - 2 * inset, len(columns))
        for column, column_width in zip(columns, widths):
            self.tree.column(column, width=column_width, minwidth=0, stretch=False)
        self.tree.xview_moveto(0)

    def _rebuild_treeview(self, preserve_checks: bool = False):
        """用当前 headers + rows 重建 Treeview。

        preserve_checks=True 时保留现有勾选（仅更新列结构），
        否则清空勾选，默认为全不选。
        展示前 5 列；模板列不在其中时追加到右侧。
        """
        self._hide_tooltip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        display_cols = _preview_columns(self._headers, self.tcol_var.get())

        tree_cols = ["#"] + [h for _, h in display_cols]
        self.tree["columns"] = tree_cols
        self.tree.heading("#", text="☑")
        self.tree.column("#", width=40, minwidth=40, anchor="center", stretch=False)
        for _, h in display_cols:
            self.tree.heading(h, text=h)
            self.tree.column(h, width=120, minwidth=0, stretch=False)
        self._tree_width_key = None

        max_row = len(self._rows) + self._header_row  # 最后一个数据行的 Excel 行号
        min_data_row = self._header_row + 1
        if preserve_checks:
            self._checked = {r for r in self._checked if min_data_row <= r <= max_row}
        else:
            self._checked.clear()
        for row_idx, row in enumerate(self._rows):
            excel_row = row_idx + self._header_row + 1
            values = [self._checkbox_text(excel_row)] + [row[idx] for idx, _ in display_cols]
            self.tree.insert("", "end", iid=str(excel_row), values=values)
        self._resize_tree_columns()

    def _checkbox_text(self, row_idx: int) -> str:
        return "☑" if row_idx in self._checked else "☐"

    def _on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        self._hide_tooltip()
        if region == "separator":
            return "break"
        col = self.tree.identify_column(event.x)
        if region != "cell" or col != "#1":
            return
        item = self.tree.identify_row(event.y)
        if not item:
            return
        try:
            row_idx = int(item)
        except ValueError:
            return
        if row_idx in self._checked:
            self._checked.discard(row_idx)
        else:
            self._checked.add(row_idx)
        self.tree.set(item, "#", self._checkbox_text(row_idx))
        self._update_selection_status()
        return "break"   # 阻止 Treeview 默认选中行为

    def _select_all(self):
        for item in self.tree.get_children():
            row_idx = int(item)
            self._checked.add(row_idx)
            self.tree.set(item, "#", "☑")
        self._update_selection_status()

    def _deselect_all(self):
        self._checked.clear()
        for item in self.tree.get_children():
            self.tree.set(item, "#", "☐")
        self._update_selection_status()

    def _update_selection_status(self):
        count = len(self._checked)
        self.status_var.set(f"已选择 {count} 行")

    # ── 映射区 ──

    def _rebuild_mapping(self):
        """Rebuild mapping controls while preserving explicit choices."""
        self.mapping_pane.clear()
        self.mapping_widgets.clear()

        if not self._headers:
            return

        ph_choices = ["(不映射)"] + self._placeholders

        headers = [h for h in self._headers if h]  # 跳过空标题
        cells = []
        for header in headers:
            cell = ttk.Frame(self.mapping_frame)
            cell.columnconfigure(0, weight=1)
            cells.append(cell)

            ttk.Label(cell, text=header, width=14, anchor="e").grid(
                row=0, column=0, sticky="ew",
            )
            ttk.Label(cell, text=" → ", foreground="gray").grid(row=0, column=1)

            explicit = self._explicit_mapping.get(header, ...)
            suggested = self._auto_mapping.get(header, "(不映射)") if explicit is ... else explicit
            var = tk.StringVar(value=suggested if suggested else "(不映射)")
            combo = ttk.Combobox(cell, textvariable=var, values=ph_choices, width=14, state="readonly")
            combo.grid(row=0, column=2)
            combo.bind(
                "<<ComboboxSelected>>",
                lambda _event, col=header, value=var: self._remember_mapping(col, value.get()),
            )
            self.mapping_widgets.append((header, var))
        self.mapping_pane.set_cells(cells)

    def _remember_mapping(self, excel_col: str, placeholder: str) -> None:
        """记录用户显式选择，使后续数据刷新不会覆盖它。"""
        self._explicit_mapping[excel_col] = None if placeholder == "(不映射)" else placeholder

    # ── 检查与生成 ──

    def _current_settings(self) -> CheckSettings:
        mapping: dict[str, str] = {}
        explicitly_unmapped: list[str] = []
        for column, var in self.mapping_widgets:
            value = var.get()
            if value and value != "(不映射)":
                mapping[column] = value
            elif column in self._explicit_mapping and self._explicit_mapping[column] is None:
                explicitly_unmapped.append(column)
        return CheckSettings(
            self.sheet_var.get(),
            self._header_row,
            self.tcol_var.get() or None,
            mapping,
            tuple(sorted(self._checked)),
            tuple(explicitly_unmapped),
        )

    def _check_current(self) -> None:
        if self._check_window is not None and self._check_window.winfo_exists():
            self._check_window.destroy()
        report = check_inputs(self.tpl_var.get(), self.excel_var.get(), self._current_settings())
        self._check_window = CheckDialog(self.root, report)

    def _generate(self):
        tpl_path = self.tpl_var.get()
        excel_path = self.excel_var.get()
        sheet_name = self.sheet_var.get()

        if not tpl_path:
            messagebox.showerror("错误", "请选择模板 PPT")
            return
        if not excel_path:
            messagebox.showerror("错误", "请选择 Excel 文件")
            return
        if not sheet_name:
            messagebox.showerror("错误", "请选择 Sheet")
            return
        if not self._checked:
            messagebox.showerror("错误", "请至少勾选一行数据")
            return

        try:
            settings = self._current_settings()
            prs = load_template(tpl_path)
            output = Path(excel_path).parent / f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
            result = generate(
                prs,
                excel_path,
                settings.sheet_name,
                list(settings.selected_rows),
                output,
                template_column=settings.template_column,
                mapping=settings.mapping,
                header_row=settings.header_row,
            )

            # 保存 config.toml
            config = Config(
                template_column=settings.template_column or "",
                header_row=settings.header_row,
                mapping=settings.mapping,
            )
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            save_config(config, CONFIG_PATH)

            summary = f"已生成 {result.generated_pages} 页\n{result.output_path}"
            if result.warnings:
                summary += "\n\n警告：\n" + "\n".join(f"- {warning}" for warning in result.warnings)
            self.status_var.set(f"生成完成: {result.generated_pages} 页 → {result.output_path}")
            messagebox.showinfo("完成", summary)
        except Exception as e:
            self.status_var.set(f"错误: {e}")
            messagebox.showerror("错误", str(e))

    def _auto_load_config(self):
        """启动时加载 config.toml，文件不存在则创建空配置。"""
        try:
            config = load_config(CONFIG_PATH)
            # 首次启动时自动写入 config.toml 到磁盘
            if not CONFIG_PATH.exists():
                save_config(config, CONFIG_PATH)
            self._preferred_template_column = config.template_column or None
            if config.mapping:
                self._auto_mapping = config.mapping
                self._explicit_mapping = dict(config.mapping)
                self._mapping_from_config = True
            if config.header_row:
                self._header_row = config.header_row
                self.hrow_var.set(config.header_row)
                self._hrow_from_config = True
            self.status_var.set("已从 config.toml 加载配置")
        except Exception as e:
            self.status_var.set(f"配置加载失败: {e}")


def main() -> None:
    if sys.platform == "win32":
        from ctypes import windll

        # Set system DPI awareness in the GUI process before Tk creates a window.
        windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    # Leave room for the window frame and taskbar on smaller displays.
    width = max(1000, min(1600, root.winfo_screenwidth() - 64))
    height = max(600, min(950, root.winfo_screenheight() - 96))
    root.geometry(f"{width}x{height}")
    root.minsize(1000, 600)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
