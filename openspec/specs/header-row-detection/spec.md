# header-row-detection Specification

## Purpose
Define evidence-based detection and manual selection of Excel header rows when workbooks contain preamble content.
## Requirements
### Requirement: Header row detection scans multiple rows

The system SHALL inspect up to the first 5 rows. A candidate header row SHALL contain at least two unique, non-empty headers and SHALL be ranked by template-column evidence in its subsequent rows. If no candidate has positive evidence, row 1 SHALL be used.

#### Scenario: Header in row 1 with clear data rows below

- **WHEN** Row 1 values are `[项目, 批次, 模板, 备注]`, Row 2 values are `[P001, B01, Ni-NTA, x]`, Row 3 values are `[P002, B02, GST, y]`, and template names are `{Ni-NTA, GST}`
- **THEN** Row 1 is a valid unique header candidate whose subsequent rows contain template evidence, and the system returns row 1

#### Scenario: Header in row 2 with merged cell in row 1

- **WHEN** Row 1 values are `[大标题, , , ]` (only 1 non-empty), Row 2 values are `[项目, 批次, 模板]`, Row 3 values are `[P001, B01, Ni-NTA]`, and template names are `{Ni-NTA, GST}`
- **THEN** Row 1 is skipped, Row 2 is a valid unique header candidate with downstream template evidence, and the system returns row 2

#### Scenario: All rows score zero

- **WHEN** no valid candidate has downstream template-name evidence
- **THEN** the system returns row index 1 as the default

#### Scenario: Header in row 3

- **WHEN** Row 1 values are `[大标题, , , ,]` (1 non-empty, skipped), Row 2 values are `[附注, , ,]` (1 non-empty, skipped), Row 3 values are `[项目, 批次, 模板]`, Row 4 values are `[P001, B01, Ni-NTA]`, and template names are `{Ni-NTA}`
- **THEN** Rows 1 and 2 are skipped, Row 3 has downstream template evidence, and the system returns row 3
