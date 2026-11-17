# reproducible-test-fixtures Specification

## Purpose
Define deterministic, repository-owned PPTX and XLSX fixtures for repeatable regression testing.
## Requirements
### Requirement: Automated tests are self-contained
The automated test suite SHALL create or use repository-owned fixtures and SHALL NOT require mutable customer files under `docs/`.

#### Scenario: Repository is checked out without customer examples
- **WHEN** the full test suite runs in a clean checkout containing only tracked test resources
- **THEN** tests SHALL execute without missing-file or customer-Sheet-name failures

### Requirement: Fixture builders define the fixture contract
Generated XLSX and PPTX fixtures SHALL come from shared fixture builders that define their Sheet names, row values, slide count, template markers, and placeholders.

#### Scenario: PPTX fixture is generated
- **WHEN** the template fixture builder runs
- **THEN** the resulting presentation SHALL contain exactly the documented slides, markers, and placeholders used by the tests

#### Scenario: XLSX fixture is generated
- **WHEN** the workbook fixture builder runs
- **THEN** the resulting workbook SHALL contain the documented Sheet, headers, and data values used by the tests

### Requirement: Committed binary fixtures remain synchronized
If binary fixtures remain committed, the system SHALL verify their semantic contents against the shared fixture contract rather than comparing unstable ZIP bytes.

#### Scenario: Committed fixture drifts from its builder
- **WHEN** a committed fixture has an extra slide, changed marker, changed Sheet, or changed row value
- **THEN** the fixture consistency test SHALL fail with the mismatched semantic property

### Requirement: Full suite establishes the baseline
The change SHALL be considered complete only when the full pytest suite passes without tests being disabled solely because fixtures are unavailable.

#### Scenario: Stabilization work is complete
- **WHEN** `uv run --group dev pytest` is run after implementation
- **THEN** all tests SHALL pass and no test SHALL require an untracked file under `docs/`
