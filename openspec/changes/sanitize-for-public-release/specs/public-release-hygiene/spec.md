## ADDED Requirements

### Requirement: Public source uses generic identities and examples
The public source snapshot SHALL use generic organization-independent names and fabricated examples. Retained source files, filenames, configuration, user documentation, specifications, change archives, and verification records SHALL NOT contain the organization identifiers, business attachment names, actual project identifiers, private contact details, or machine-specific user paths identified during the release audit. Public license attribution, generic domain terms, and standard technical URLs SHALL remain permitted.

#### Scenario: Retained documentation is checked
- **WHEN** the current README, training documentation, specifications, and change archives are reviewed for public release
- **THEN** organization-specific references and actual business identifiers SHALL have been replaced with generic descriptions and fabricated values
- **AND** the current change's planning and verification documents SHALL NOT reproduce the sensitive original values

#### Scenario: Generator module is imported
- **WHEN** the GUI or automated tests import the generation workflow
- **THEN** they SHALL use `src.generator` and the existing generation interface
- **AND** no compatibility module with an organization-specific name SHALL be shipped

### Requirement: Shared agent guidance is the single project guidance document
The public source snapshot SHALL contain a root `AGENTS.md` with applicable development guidance and SHALL NOT contain a root `CLAUDE.md`. Necessary and accurate guidance from the removed document SHALL be merged into `AGENTS.md` without retaining obsolete business examples.

#### Scenario: Contributor reads project guidance
- **WHEN** a contributor opens the public source root
- **THEN** `AGENTS.md` SHALL describe the current structure, development commands, and project conventions
- **AND** the guidance SHALL NOT depend on the removed document

### Requirement: Public configuration is a generic working example
The submitted example configuration SHALL use generic template and project fields while preserving the existing configuration schema and runtime configuration behavior.

#### Scenario: Example configuration is loaded
- **WHEN** the submitted `config.toml` is loaded
- **THEN** it SHALL select the generic template column `模板` and header row `1`
- **AND** its mappings SHALL use generic project fields in the Excel-column-to-PPT-placeholder direction
- **AND** existing user configurations SHALL continue to use the existing parsing and persistence behavior

### Requirement: Public snapshot excludes repository history and machine artifacts
The release process SHALL produce a standalone snapshot from the final reviewed files without original Git metadata, virtual environments, bytecode, test caches, tool-local settings, or unrelated build output. Preparing this snapshot SHALL NOT delete, rewrite, reinitialize, or push the original repository's history. Existing staged deletions SHALL remain excluded.

#### Scenario: Snapshot is extracted into an empty directory
- **WHEN** the public source archive is extracted independently
- **THEN** it SHALL contain the reviewed source, documentation, configuration, license, and synthetic test resources
- **AND** it SHALL contain no `.git` directory or file and no excluded machine artifacts
- **AND** it SHALL reflect the final reviewed working files rather than stale committed versions

#### Scenario: Original repository remains available
- **WHEN** public snapshot preparation finishes
- **THEN** the original repository's commits, branches, and remote configuration SHALL remain intact
- **AND** the release instructions SHALL describe creating a fresh repository and its initial commit from the extracted snapshot

### Requirement: Release verification checks the delivered content
Release verification SHALL inspect the actual delivered text, filenames, Office document contents and metadata, and retained screenshots, and SHALL run the complete existing regression suite. Verification records SHALL summarize findings without copying sensitive original values into the public snapshot.

#### Scenario: Office resources are included in the release
- **WHEN** XLSX or PPTX files are included in the snapshot
- **THEN** verification SHALL inspect their relevant XML content and document properties and review notes, external links, and embedded resources where present
- **AND** delivered resources SHALL satisfy the synthetic fixture requirements

#### Scenario: Release preparation is complete
- **WHEN** implementation is marked complete
- **THEN** the complete regression suite and OpenSpec strict validation SHALL have passed
- **AND** the extracted snapshot SHALL have been checked for required files, forbidden artifacts, and known sensitive residuals
