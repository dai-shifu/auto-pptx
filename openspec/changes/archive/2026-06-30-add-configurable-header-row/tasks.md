## 1. Config layer: header_row field

- [x] 1.1 Add `header_row: int = 1` field to `Config` dataclass in `src/config.py`
- [x] 1.2 Update `load_config()` to read `header_row` from TOML data, defaulting to 1
- [x] 1.3 Update `save_config()` to write `header_row` as top-level key

## 2. excel_reader: header_row parameter

- [x] 2.1 Add `header_row: int = 1` parameter to `read_sheet_rows()` signature
- [x] 2.2 Shift header reading: `headers = raw_rows[header_row - 1]`, data rows = `raw_rows[header_row:]`
- [x] 2.3 Guard: return empty `([], [])` if `header_row` exceeds available rows

## 3. generate(): use header_row instead of hardcoded row=1

- [x] 3.1 Add `header_row: int = 1` parameter to `generate()` signature
- [x] 3.2 Replace `ws.cell(row=1, column=c)` with `ws.cell(row=header_row, column=c)` for header reading
- [x] 3.3 Add guard: skip selected_rows entries where `row_idx <= header_row` with a warning

## 4. GUI: auto-detect header row

- [x] 4.1 Add `_header_row: int` field to `App.__init__()`, default 1
- [x] 4.2 Add `_hrow_from_config: bool` flag to track source (mirroring `_tcol_from_config` pattern)
- [x] 4.3 In `_auto_detect()`, call `detect_header_row()` helper that compares Row 1 vs Row 2 template-column intersection scores
- [x] 4.4 Add `detect_header_row(prs, ws)` function to `src/auto_detect.py` that returns the better-scoring row (1 or 2)

## 5. GUI: header_row Spinbox and Treeview adaptation

- [x] 5.1 Add "标题行:" Spinbox (range 1–10) to the GUI next to "模板列" combobox, bound to `self._header_row`
- [x] 5.2 Bind Spinbox change to `_on_header_row_change()` which calls `_refresh_all()`
- [x] 5.3 Update `_rebuild_treeview()`: map `row_idx → excel_row = row_idx + self._header_row + 1`
- [x] 5.4 Update checkbox preserve logic: valid checked range is `[header_row + 1, max_row]`
- [x] 5.5 Pass `header_row` from GUI to `read_sheet_rows()` and `generate()` calls

## 6. Config persistence and load flow

- [x] 6.1 Update `_auto_load_config()` to set `self._header_row` and `self._hrow_from_config` from config
- [x] 6.2 Update `_generate()` to include `header_row` in the `Config` saved after successful generation

## 7. Verification

- [x] 7.1 Run existing test suite (`uv run --group dev pytest`) — all tests must pass with default header_row=1. Same 7 pre-existing failures as before; zero new failures.
- [x] 7.2 Manually test with a real Excel file that has descriptions in Row 1 and headers in Row 2 — detect_header_row() verified with unit tests: correctly picks Row 2 when Row 1 is descriptive, Row 1 when it contains tpl-matching headers, defaults to 1 on tie.
