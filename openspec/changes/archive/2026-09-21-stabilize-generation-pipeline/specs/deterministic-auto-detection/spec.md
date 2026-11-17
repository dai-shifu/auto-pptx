## ADDED Requirements

### Requirement: Slash-separated template values participate in detection
The system SHALL split each non-empty template-column candidate value on `/`, trim each token, discard empty tokens, and compare the resulting tokens with template names.

#### Scenario: Multi-template cell identifies its column
- **WHEN** a candidate column contains `Ni-NTA / GST` and both names exist in the template
- **THEN** both tokens SHALL contribute matches to that column's detection score

### Requirement: Auto-mapping is deterministic and one-to-one
The system SHALL produce the same automatic mapping for identical ordered inputs, and SHALL NOT automatically assign one Excel column to multiple placeholders or multiple Excel columns to one placeholder.

#### Scenario: Repeated detection is stable
- **WHEN** detection is run repeatedly with identical ordered headers and placeholders
- **THEN** every run SHALL return the same ordered suggestions and diagnostics

#### Scenario: Equal fuzzy candidates remain unresolved
- **WHEN** two available Excel columns have the same best fuzzy-match score for one placeholder
- **THEN** the placeholder SHALL remain unmapped and the result SHALL identify the competing candidates

#### Scenario: Exact match wins before fuzzy matching
- **WHEN** one Excel column exactly matches a placeholder ignoring case and another is only a fuzzy match
- **THEN** the exact matching column SHALL be selected

### Requirement: Placeholder order follows the template
The system SHALL return placeholders in first-seen slide, shape, paragraph, and table-cell order while removing duplicates.

#### Scenario: Duplicate placeholder appears on several slides
- **WHEN** the same placeholder is encountered multiple times in a template
- **THEN** it SHALL appear once at the position of its first occurrence

### Requirement: Data-context changes refresh suggestions
The system SHALL recompute template-column and mapping suggestions when the Excel file, selected Sheet, header row, headers, or sampled rows change, even when the PPT template path is unchanged.

#### Scenario: User selects another Excel file
- **WHEN** the user selects a different Excel file while retaining the current PPT template
- **THEN** suggestions SHALL be based on the new workbook rather than cached workbook data

#### Scenario: User changes the header row
- **WHEN** the user changes the header-row selection
- **THEN** suggestions SHALL be recomputed from the resulting headers and rows

### Requirement: Header detection uses downstream template evidence
The system SHALL evaluate candidate header rows using the uniqueness of their non-empty headers and template-column evidence in subsequent rows. If no candidate has positive downstream template evidence, the system SHALL select row 1.

#### Scenario: Explanatory row precedes the actual headers
- **WHEN** an explanatory row with multiple cells precedes a header row whose subsequent data contains template names
- **THEN** the detector SHALL select the actual header row

#### Scenario: No candidate yields template evidence
- **WHEN** no candidate header produces a detectable template column in subsequent rows
- **THEN** the detector SHALL return row 1
