## MODIFIED Requirements

### Requirement: Template-column changes refresh the data preview

The GUI SHALL keep the displayed columns in sync with the template-column selection and SHALL preserve checked Excel rows. When the displayed columns do not change, the GUI SHALL leave the existing preview rows and vertical scroll position intact.

#### Scenario: User selects a different template column

- **WHEN** the user changes the template-column selection to a column outside the first five Excel columns
- **THEN** the newly selected template column appears in the preview and the existing checked rows remain checked

#### Scenario: Both template columns are already visible

- **WHEN** the user switches between two template columns within the first five Excel columns
- **THEN** the preview rows are not rebuilt, and the checked Excel rows and vertical scroll position do not change
