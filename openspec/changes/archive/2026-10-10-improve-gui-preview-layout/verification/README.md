# GUI verification

Executed with real Tk widgets in Xvfb on WSL2 Linux, Python 3.11.15, Tk 9.0.3.
The final complete suite passes **136 tests with no skips** (5.27 seconds),
including presentation-generation regressions and 10 tooltip tests.
OpenSpec strict validation and the whitespace diff check also pass.

```sh
env UV_PROJECT_ENVIRONMENT=/tmp/auto-pptx-venv UV_CACHE_DIR=/tmp/auto-pptx-uv-cache xvfb-run -a uv run --group dev pytest -q
openspec validate improve-gui-preview-layout --strict
git diff --check
```

The GUI layout suite passes **54 tests**, including 300 rows, 41 mapping items,
the 1400×850 and 1000×600 window sizes, actual divider dragging, final-row mouse
selection, mapping reflow, retained generation arguments, and independent wheel
scrolling. Headless runs explicitly skip real-Tk tests; they are not equivalent
to this displayed verification.

```sh
xvfb-run -a /tmp/auto-pptx-venv/bin/python -m pytest tests/test_gui_layout.py -q
```

## Screenshots

- [Default window, 1400×850](default-1400x850.png)
- [Minimum window, 1000×600](minimum-1000x600.png)
- [Overflow tooltip](minimum-tooltip.png)

This Tk9/Xvfb build exposes only the X11 core fonts `fixed`, `bitstream charter`,
and `courier 10 pitch`. Fontconfig lists Chinese fonts, but this Tk build cannot
use them. Screenshot labels and displayed sample data therefore use English in
the verification instance only; product text remains Chinese. These screenshots
verify geometry and visibility, rather than Windows appearance or Chinese glyph
rendering. The underlying workbook used for timing contains Chinese long text.

## 300-row workbook and interaction measurements

The temporary `.xlsx` contained 300 data rows and 41 columns, with repeated long
Chinese text in 40 columns and a final template column (approximately 129KB).
It was read from disk using the application's existing load path and canonical
PPT fixture; no generated workbook or presentation was added to the repository.
The file-selection load includes reading Sheet names, header detection, Excel
reading, template detection, Treeview insertion, mapping construction, and the
subsequent Tk layout callbacks.

| Operation | Observed time |
|---|---:|
| Single `read_sheet_rows` | 468ms |
| Complete `_update_sheets`, including UI layout | 2118ms |
| Select all 300 rows | 48ms |
| Clear all 300 rows | 5ms |
| Scroll to final row | 6ms |
| Rebuild preview | 17ms |

These are one-run measurements on this machine, not performance guarantees.
The preview and selection interactions remain responsive at 300 rows. Initial
loading still takes roughly two seconds for this deliberately wide, long-text
workbook; duplicate reads and main-thread Excel processing remain outside the
scope of this layout change.

At minimum size, preview/mapping heights were 307px/131px and six data-column
widths were 154/154/154/154/154/153px. At default size, heights were 482px/206px
and all six data columns reached the 200px cap. Both vertical scrollbars and the
generation button remained mapped. Raw environment and timing details are in
[metrics.json](metrics.json).
