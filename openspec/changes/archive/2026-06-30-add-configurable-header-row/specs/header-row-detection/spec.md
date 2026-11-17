## ADDED Requirements

### Requirement: Config stores and loads header_row

The `Config` dataclass SHALL include a `header_row` field with a default value of 1. The `load_config()` function SHALL read `header_row` from `config.toml` when present, and default to 1 when absent. The `save_config()` function SHALL write `header_row` to `config.toml` as a top-level key.

#### Scenario: Config file has header_row

- **WHEN** `config.toml` contains `header_row = 2`
- **THEN** `load_config()` returns a Config with `header_row = 2`

#### Scenario: Config file lacks header_row

- **WHEN** `config.toml` exists but does not contain a `header_row` key
- **THEN** `load_config()` returns a Config with `header_row = 1`

#### Scenario: Save config with header_row

- **WHEN** `save_config()` is called with a Config where `header_row = 2`
- **THEN** the written `config.toml` SHALL contain `header_row = 2`

### Requirement: read_sheet_rows accepts header_row parameter

The `read_sheet_rows()` function SHALL accept an optional `header_row` parameter (default 1) specifying which Excel row (1-based) contains column headers. Headers SHALL be read from that row; data rows SHALL be all subsequent rows.

#### Scenario: header_row = 1 (default, backward compatible)

- **WHEN** `read_sheet_rows(path, sheet)` is called without `header_row`
- **THEN** headers are read from Excel Row 1
- **AND** data rows begin from Excel Row 2

#### Scenario: header_row = 2

- **WHEN** `read_sheet_rows(path, sheet, header_row=2)` is called on an Excel with 5 rows where Row 2 is headers
- **THEN** headers are read from Excel Row 2
- **AND** data rows begin from Excel Row 3 (returned as `rows[0]`)

#### Scenario: header_row beyond available rows

- **WHEN** `read_sheet_rows(path, sheet, header_row=10)` is called on an Excel with 3 rows
- **THEN** headers SHALL be an empty list
- **AND** data rows SHALL be an empty list

### Requirement: generate uses header_row for header reading

The `generate()` function SHALL accept an optional `header_row` parameter (default 1) and SHALL read column headers from the specified row instead of hardcoded Row 1. The `selected_rows` list SHALL continue to contain absolute Excel row numbers, interpreted as data rows that MUST be greater than `header_row`.

#### Scenario: generate with header_row = 1 (backward compatible)

- **WHEN** `generate()` is called with `header_row=1` and `selected_rows=[2, 3, 4]`
- **THEN** headers are read from Excel Row 1
- **AND** selected_rows correspond to Rows 2–4 as before

#### Scenario: generate with header_row = 2

- **WHEN** `generate()` is called with `header_row=2` and `selected_rows=[3, 4, 5]`
- **THEN** headers are read from Excel Row 2
- **AND** data values for each selected row are read from the correct Excel row

#### Scenario: selected row equals header row

- **WHEN** `generate()` is called with `header_row=2` and `selected_rows` contains row 2
- **THEN** row 2 SHALL be skipped with a warning (it is the header row, not data)

### Requirement: GUI auto-detects header row

The GUI SHALL automatically detect the header row by comparing candidate rows (1 and 2) against `{{tpl::name}}` identifiers using template-column intersection scoring. The row with the higher score SHALL be selected. If scores are equal or both zero, the default (1) SHALL be used.

#### Scenario: Row 2 matches templates better than Row 1

- **WHEN** the GUI loads an Excel where Row 1 contains descriptive text and Row 2 contains column headers matching template names
- **THEN** `header_row` SHALL be auto-detected as 2
- **AND** the Treeview SHALL display Row 2 content as column headers

#### Scenario: Row 1 is the actual header

- **WHEN** the GUI loads an Excel where Row 1 contains column headers matching template names
- **THEN** `header_row` SHALL be auto-detected as 1
- **AND** behavior is identical to the current system

#### Scenario: Config overrides auto-detection

- **WHEN** `config.toml` specifies `header_row = 2`
- **AND** the GUI loads an Excel file
- **THEN** `header_row` SHALL be 2 regardless of auto-detection result

### Requirement: GUI Treeview adapts row numbering to header_row

The Treeview SHALL display checkboxes with row numbers that reflect absolute Excel row positions. Row index-to-Excel-row mapping SHALL account for the configured `header_row`.

#### Scenario: header_row = 2, Treeview row numbers

- **WHEN** `header_row = 2` and the Excel has 4 rows
- **THEN** the Treeview SHALL display rows with checkbox indices starting at 3 (the first data row)
- **AND** rows 1–2 SHALL not appear in the Treeview

#### Scenario: header_row = 1, Treeview row numbers (unchanged)

- **WHEN** `header_row = 1` and the Excel has 4 rows
- **THEN** the Treeview SHALL display rows with checkbox indices starting at 2
- **AND** behavior is identical to the current system
