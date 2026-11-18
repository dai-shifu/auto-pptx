## ADDED Requirements

### Requirement: Shared fixtures verify end-to-end generation results

Regression tests SHALL use shared fixtures to verify generated slide count and order, retained template markers, and representative replacements in text and tables. The suite SHALL cover empty row selection and an unknown worksheet as distinct errors without producing an output file.

#### Scenario: Selected data rows produce the final slides

- **WHEN** the end-to-end test generates a deck from known matching rows in the shared fixtures
- **THEN** it SHALL check that the output contains only the expected slides in selection order, with their template markers and expected replacement values

#### Scenario: Generation is given an empty selection or an unknown worksheet

- **WHEN** a regression test attempts generation with no selected rows or an unknown worksheet
- **THEN** it SHALL check for the corresponding error and verify that no output file was created
