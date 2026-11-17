## ADDED Requirements

### Requirement: Fixture examples are fabricated for public distribution
Shared fixture builders and committed binary fixtures SHALL use fabricated project identifiers and generic worksheet names rather than values copied from business attachments. The builders, dependent assertions, and committed fixture contents SHALL agree semantically after sanitization, while preserving the existing regression scenarios.

#### Scenario: Project lookup examples are generated
- **WHEN** the shared workbook fixture builder generates project lookup data
- **THEN** its example identifiers SHALL be `DEMO-001` and `DEMO-002`
- **AND** its detail worksheet SHALL be named `项目明细`
- **AND** successful lookup, missing lookup, and non-first-row-header scenarios SHALL remain testable

#### Scenario: Sanitized binary fixtures are verified
- **WHEN** fixture contract tests compare committed XLSX and PPTX files with the shared builders
- **THEN** semantic comparison SHALL pass using the fabricated values and generic names
- **AND** fixture data and document metadata SHALL NOT retain the business identifiers or private personal details identified during the release audit
