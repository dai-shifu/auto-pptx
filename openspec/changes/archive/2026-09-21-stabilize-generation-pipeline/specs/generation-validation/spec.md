## ADDED Requirements

### Requirement: Generation validates its input schema
The system SHALL reject duplicate non-empty Excel headers, mappings whose source columns do not exist, and mappings that assign more than one source column to the same placeholder before saving output.

#### Scenario: Duplicate Excel headers are present
- **WHEN** the selected header row contains the same non-empty header more than once
- **THEN** generation SHALL fail with an error identifying the duplicate header

#### Scenario: Explicit mapping references a missing column
- **WHEN** an explicit mapping references an Excel column absent from the selected header row
- **THEN** generation SHALL fail before cloning or saving slides

### Requirement: Zero-page generation is not successful
The system SHALL NOT report success or leave a final output presentation when no selected row and template combination generates a slide.

#### Scenario: Every selected template name is missing
- **WHEN** all selected rows refer to template names absent from the presentation
- **THEN** generation SHALL fail with a zero-page validation error and SHALL NOT create the final output file

### Requirement: Generation returns a structured result
Successful generation SHALL return a result containing the generated-page count, skipped inputs, unmatched template names, unresolved placeholders, and warning messages.

#### Scenario: Some rows generate and some are skipped
- **WHEN** at least one selected row generates a slide and another selected row has no matching template
- **THEN** the result SHALL report the generated-page count and identify the skipped row and unmatched template

### Requirement: Unresolved placeholders are visible
The system SHALL inspect generated slides for unresolved non-template placeholders and include their names in the generation result.

#### Scenario: Optional placeholder has no mapped value
- **WHEN** a generated slide still contains `{{备注}}`
- **THEN** the result SHALL include `备注` in its unresolved-placeholder diagnostics

### Requirement: GUI presents one generation summary
The GUI SHALL use the structured generation result to present the output path, generated-page count, and any warnings after generation completes.

#### Scenario: Generation succeeds with warnings
- **WHEN** slides are generated but unmatched templates or unresolved placeholders remain
- **THEN** the GUI SHALL report completion together with those warnings instead of silently reporting unconditional success
