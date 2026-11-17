## ADDED Requirements

### Requirement: Editable protein expression and purification daily report
The repository SHALL provide a separate synthetic daily-report example with overview, project-progress, and risks-and-plan templates. Visual elements SHALL remain editable. Experimental images SHALL be added manually by users.

#### Scenario: Generate the complete example
- **WHEN** all five example data rows are selected with their matching template and column mappings
- **THEN** the existing generator SHALL produce an overview, three project pages, and a risks-and-plan page in that order without unmatched templates or unresolved data placeholders
- **AND** template markers SHALL remain outside the slide canvas

### Requirement: Reproducible and inspectable example assets
The example SHALL include a template PPTX, data XLSX, generated sample PPTX, previews rendered from that PPTX, and a builder using existing runtime dependencies. Existing test fixtures SHALL remain unchanged.

#### Scenario: Rebuild in an isolated directory
- **WHEN** a maintainer executes the builder with a temporary output directory
- **THEN** the assets SHALL reproduce the documented slide contents and ordering using the existing generator
- **AND** the build SHALL NOT modify tracked fixture files or user configuration

### Requirement: Concise task-oriented documentation
README and user documentation SHALL describe current functionality accurately, provide a consistent example entry point, and distinguish unmapped placeholders, mapped empty cells, retained template markers, manual images, and manually prepared overview values.

#### Scenario: Follow the example instructions
- **WHEN** a user follows the example guide
- **THEN** they SHALL be able to select the correct files, sheet, header row, template column, mappings, and five rows
- **AND** documentation SHALL state the expected five-page result and relevant limitations
