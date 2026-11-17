## ADDED Requirements

### Requirement: Workbook is closed on all exit paths

The `generate()` function SHALL ensure the openpyxl Workbook is closed regardless of whether generation succeeds, fails with a known error, or throws an unexpected exception.

#### Scenario: Normal generation path

- **WHEN** `generate()` completes all row processing successfully
- **THEN** the Workbook SHALL be closed before the function returns

#### Scenario: Exception during slide cloning

- **WHEN** `clone_slide()` or `replace_in_slide()` throws an exception during the row processing loop
- **THEN** the Workbook SHALL be closed before the exception propagates to the caller

#### Scenario: Exception during auto-detection

- **WHEN** `detect_and_suggest()` throws an exception while determining template column or mapping
- **THEN** the Workbook SHALL be closed before the exception propagates to the caller

### Requirement: Template Presentation is not reloaded on Sheet switch

The GUI SHALL NOT reload a Presentation from disk when only the selected Sheet name changes and the template file path has not changed.

#### Scenario: User switches Sheet with same template

- **WHEN** the user selects a different Sheet in the GUI dropdown
- **AND** the template PPT file path is unchanged from the last detection
- **THEN** the auto-detection SHALL reuse the previously collected placeholder and mapping data
- **AND** no new Presentation object SHALL be loaded from disk

#### Scenario: User changes template file

- **WHEN** the user selects a new template PPT file via the file browser
- **THEN** the auto-detection SHALL load the new Presentation and update placeholder/mapping data

### Requirement: Slide pruning is encapsulated in a single function

Slide removal from a Presentation SHALL be implemented in a dedicated `prune_slides()` function in `pptx_engine.py`, isolating the dependency on private python-pptx attributes (`_sldIdLst`) to one location.

#### Scenario: Pruning template slides after generation

- **WHEN** `prune_slides(prs, count)` is called with `count` > 0
- **THEN** the first `count` slides SHALL be removed from the Presentation
- **AND** the remaining slides SHALL retain their original order and content

#### Scenario: Pruning zero slides

- **WHEN** `prune_slides(prs, 0)` is called
- **THEN** no slides SHALL be removed and no error SHALL be raised

### Requirement: TOML serialization escapes special characters

The `save_config()` function SHALL produce valid TOML output when mapping keys or values contain characters that are special in TOML basic strings (double quotes, backslashes).

#### Scenario: Mapping value contains double quote

- **WHEN** a mapping entry has a value containing a double-quote character (e.g., `3" column`)
- **THEN** the generated TOML SHALL escape it as `\"` and remain parseable by `tomllib`

#### Scenario: Normal mapping values

- **WHEN** all mapping keys and values contain only alphanumeric characters, spaces, and underscores
- **THEN** the generated TOML SHALL be identical to the current format (no regressions)
