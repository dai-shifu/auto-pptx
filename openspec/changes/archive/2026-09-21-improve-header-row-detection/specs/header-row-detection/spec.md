## ADDED Requirements

### Requirement: Header row detection scans multiple rows

The system SHALL scan up to 5 rows of the Excel sheet to determine the most likely header row by computing, for each row, the intersection ratio of its non-empty cell values with the template name set. The row with the lowest ratio SHALL be selected as the header row.

Rows with fewer than 2 non-empty cell values SHALL be skipped as merged-cell residue rows.

#### Scenario: Header in row 1 with clear data rows below

- **WHEN** Row 1 values are `[项目, 批次, 模板, 备注]`, Row 2 values are `[P001, B01, Ni-NTA, x]`, Row 3 values are `[P002, B02, GST, y]`, and template names are `{Ni-NTA, GST}`
- **THEN** Row 1 score = 0.0 (no intersection with template names), Row 2 score = 0.25, Row 3 score = 0.25, and the system returns row 1

#### Scenario: Header in row 2 with merged cell in row 1

- **WHEN** Row 1 values are `[大标题, , , ]` (only 1 non-empty), Row 2 values are `[项目, 批次, 模板]`, Row 3 values are `[P001, B01, Ni-NTA]`, and template names are `{Ni-NTA, GST}`
- **THEN** Row 1 is skipped (non-empty count = 1 < 2), Row 2 score = 0.0, Row 3 score = 0.33, and the system returns row 2

#### Scenario: All rows score zero

- **WHEN** all scanned rows have 0 template name intersection (no template names found in any row), or only one valid row exists
- **THEN** the system returns row index 1 as the default

#### Scenario: Header in row 3

- **WHEN** Row 1 values are `[大标题, , , ,]` (1 non-empty, skipped), Row 2 values are `[附注, , ,]` (1 non-empty, skipped), Row 3 values are `[项目, 批次, 模板]`, Row 4 values are `[P001, B01, Ni-NTA]`, and template names are `{Ni-NTA}`
- **THEN** Row 3 score = 0.0, Row 4 score = 0.33, and the system returns row 3
