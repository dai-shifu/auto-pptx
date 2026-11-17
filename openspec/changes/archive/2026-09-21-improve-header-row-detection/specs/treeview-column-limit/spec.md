## ADDED Requirements

### Requirement: Treeview displays only the first 5 columns

The Treeview data preview SHALL display exactly the first 5 columns from the headers (as determined by the configured header row), plus the leading checkbox column. No additional columns SHALL be included, regardless of template column or mapping column positions.

#### Scenario: Headers have more than 5 columns

- **WHEN** headers are `[A, B, C, D, E, F, G, H]`
- **THEN** the Treeview displays columns `[#, A, B, C, D, E]` (checkbox + 5 data columns)

#### Scenario: Headers have fewer than 5 columns

- **WHEN** headers are `[A, B, C]`
- **THEN** the Treeview displays columns `[#, A, B, C]` (checkbox + all available headers)

#### Scenario: Treeview refreshes when header row changes

- **WHEN** user changes the header row from 1 to 3
- **THEN** headers are re-read from the new header row, and the Treeview displays the first 5 columns from the updated headers

### Requirement: Treeview column width is larger

The system SHALL use column width `max(120, min(280, len(header) * 20))` pixels for each data column in the Treeview.

#### Scenario: Short column name

- **WHEN** a column header is 3 characters long (e.g., "项目")
- **THEN** `len("项目") * 20 = 60 → clamped to max(120, 60) = 120px` width

#### Scenario: Long column name

- **WHEN** a column header is 30 characters long
- **THEN** `len * 20 = 600 → clamped to min(280, 600) = 280px` width
