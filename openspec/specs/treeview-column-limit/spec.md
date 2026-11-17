# treeview-column-limit Specification

## Purpose
Define a compact and readable Excel data preview for wide worksheets.
## Requirements
### Requirement: Treeview displays only the first 5 columns

The Treeview data preview SHALL display the first five available headers from the configured header row, plus the leading checkbox column. It SHALL additionally display the selected template column when that column exists outside the first five columns, as defined by `data-preview-columns`; mapping-column positions SHALL NOT add other preview columns.

#### Scenario: Headers have more than 5 columns

- **WHEN** headers are `[A, B, C, D, E, F, G, H]` and no additional template column is selected
- **THEN** the Treeview displays columns `[#, A, B, C, D, E]` (checkbox + 5 data columns)

#### Scenario: Headers have fewer than 5 columns

- **WHEN** headers are `[A, B, C]`
- **THEN** the Treeview displays columns `[#, A, B, C]` (checkbox + all available headers)

#### Scenario: Treeview refreshes when header row changes

- **WHEN** user changes the header row from 1 to 3
- **THEN** headers are re-read from the new header row and the Treeview displays the first five available columns, plus any selected template column outside them

#### Scenario: Template column is outside the first five columns

- **WHEN** headers are `[A, B, C, D, E, F, 模板]` and the selected template column is `模板`
- **THEN** the Treeview displays `[#, A, B, C, D, E, 模板]` without adding other mapping columns

### Requirement: Treeview column width is larger

The GUI SHALL allocate data-column widths from the Treeview's actual available inner width after reserving the fixed 40px checkbox column. Data columns SHALL share that budget evenly, subject to a maximum width of 200px per data column and integer rounding. All preview columns SHALL fit the visible viewport at supported window sizes. Widths SHALL be recalculated on viewport-width or preview-column changes without altering stored values or rebuilding data rows solely for resizing. User divider dragging SHALL NOT allow column widths to exceed these constraints.

#### Scenario: Short column name

- **WHEN** a column has a short heading such as `项目`
- **THEN** its width follows the available budget and 200px cap rather than the number of heading characters

#### Scenario: Long column name

- **WHEN** a column heading is 30 characters long
- **THEN** the column remains at most 200px wide and within the available budget
- **AND** clipped heading text is available through the overflow tooltip

#### Scenario: Six data columns in the minimum window size

- **WHEN** the preview contains five initial data columns and one appended template column at a window size of 1000×600
- **THEN** the checkbox and all six data columns fit beside the vertical scrollbar without horizontal scrolling

#### Scenario: Viewport width changes

- **WHEN** the user widens or narrows the preview viewport
- **THEN** data-column widths are recalculated within the total budget and per-column cap
- **AND** the checkbox remains 40px wide and checked rows and complete cell values are preserved
