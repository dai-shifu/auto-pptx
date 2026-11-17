# data-preview-columns Specification

## Purpose
Define which Excel columns appear in the GUI preview so template selection remains visible and understandable.
## Requirements
### Requirement: Data preview includes the selected template column

The GUI data preview SHALL display the first five Excel columns and SHALL additionally display the selected template column when that column exists outside the first five columns.

#### Scenario: Template column is outside the first five columns

- **WHEN** the headers are `[A, B, C, D, E, F, 模板]` and the selected template column is `模板`
- **THEN** the preview data columns are `[A, B, C, D, E, 模板]`

#### Scenario: Template column is already visible

- **WHEN** the headers are `[模板, A, B, C, D, E]` and the selected template column is `模板`
- **THEN** the preview data columns are `[模板, A, B, C, D]` without duplicating `模板`

#### Scenario: Template column is unavailable

- **WHEN** the selected template column is empty or is not present in the current Sheet headers
- **THEN** the preview displays only the first five available Excel columns

### Requirement: Template-column changes refresh the data preview

The GUI SHALL rebuild the data preview after the user selects a different template column and SHALL preserve the set of checked data rows.

#### Scenario: User selects a different template column

- **WHEN** the user changes the template-column selection to a column outside the first five Excel columns
- **THEN** the newly selected template column appears in the preview and the existing checked rows remain checked
