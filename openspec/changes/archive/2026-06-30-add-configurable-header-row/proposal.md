## Why

The codebase hardcodes Row 1 as the header row in four locations across the pipeline. In real-world Excel files, Row 1 is often a description/note row (e.g., "纯化实验结果表") and the actual column headers start at Row 2. This causes auto-detection to fail, template column values to be misinterpreted as headers, and generation to produce incorrect output.

## What Changes

- **Add `header_row` field to `Config`** — persisted in `config.toml`, defaults to 1 (backward compatible)
- **`read_sheet_rows()` accepts `header_row` parameter** — headers read from the specified row, data rows from all subsequent rows
- **`generate()` uses `header_row` instead of hardcoded `row=1`** — affects header reading, data row coordinates, and `max_column` scanning
- **Auto-detect header row in GUI** — compare Row 1 vs Row 2 as candidate headers by running `detect_template_column()` on each; pick the one with better tpl-name intersection
- **GUI Treeview row numbering adapts** — `row_idx` → Excel row mapping accounts for variable `header_row`
- **`config.toml` saves `header_row`** after each successful generation, so manual overrides persist

## Capabilities

### New Capabilities

- `header-row-detection`: The system SHALL auto-detect which Excel row contains column headers by comparing candidate rows against template names, and SHALL allow the user to manually override via `config.toml`.

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- **Affected code**: `src/config.py`, `src/excel_reader.py`, `src/generator.py`, `src/gui.py`
- **No breaking changes**: default `header_row=1` preserves existing behavior for all callers
- **config.toml**: gains optional `header_row` key; old configs without it load with default 1
- **No new dependencies**
