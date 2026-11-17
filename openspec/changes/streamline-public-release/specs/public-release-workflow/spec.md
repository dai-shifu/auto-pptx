## ADDED Requirements

### Requirement: Windows release tools run in Git Bash
Windows workflow commands SHALL execute in Git Bash. Maintained verification and packaging helpers SHALL use Python and SHALL NOT require PowerShell scripts. Windows maintainer instructions SHALL provide Git Bash commands.

#### Scenario: A maintainer reproduces a Windows build
- **WHEN** a maintainer runs the documented commands from Git Bash with Python and uv available
- **THEN** building, packaging, checksum verification, and executable startup verification SHALL run without a PowerShell script

### Requirement: Public development starts from a reviewed snapshot
The project SHALL provide a repeatable one-time source export containing the final reviewed working files, source ZIP, and per-file size and SHA-256 manifest. It SHALL exclude original Git metadata, local environments, caches, tool-local settings, and unrelated build output. Subsequent development SHALL use the public repository and preserve its public history.

#### Scenario: First migration is prepared
- **WHEN** the export is run after the release changes and content review are complete
- **THEN** the extracted archive SHALL contain the final workflows, scripts, documentation, configuration, license, and synthetic resources matching the manifest
- **AND** the internal repository history SHALL remain unchanged

#### Scenario: A later public update is made
- **WHEN** contributors update the public project after migration
- **THEN** they SHALL commit changes to the public repository without reinitializing its history or importing internal history

### Requirement: Continuous integration covers GUI tests
Push and pull request workflows SHALL run the complete regression suite with locked dependencies and an available Tk display. GUI tests SHALL NOT be considered covered solely because they skip without a display.

#### Scenario: CI runs without a usable display
- **WHEN** the workflow cannot create a real Tk window
- **THEN** the display precheck SHALL fail instead of treating skipped GUI tests as successful GUI verification

#### Scenario: CI has a usable display
- **WHEN** the display precheck succeeds
- **THEN** the complete regression suite SHALL execute with that display available

### Requirement: Versions are validated before release builds
The project version SHALL be maintained in `pyproject.toml` and used for executable version metadata and release package names. Formal release tags SHALL use `vX.Y.Z` and match that version before compilation starts.

#### Scenario: Tag and project version differ
- **WHEN** a formal tag does not match the project version or required format
- **THEN** the workflow SHALL fail before compiling or creating a Release

### Requirement: Windows executable is the only required user download
The release workflow SHALL build a standalone Windows x64 executable only after tests pass. It SHALL distribute a versioned exe directly, with a separate SHA-256 attachment for optional integrity verification. It SHALL NOT distribute a ZIP, configuration, or example bundle as the Windows user download. The source commit and workflow run SHALL be recorded in build artifacts. Verification SHALL cover actual executable startup, first-run configuration creation, and a minimal generation flow, with the verification method recorded.

#### Scenario: A user downloads the executable
- **WHEN** a user runs the downloaded exe from a writable directory without a config.toml
- **THEN** the program SHALL run without a separate Python installation and create config.toml next to the executable using existing application behavior
- **AND** the checksum SHALL describe the exact executable distributed

### Requirement: Trial builds and formal releases have distinct outputs
Manual workflow dispatch SHALL produce identifiable downloadable trial artifacts without creating a Release. Valid formal tags SHALL produce draft GitHub Releases; automatic construction SHALL NOT publish them as final releases.

#### Scenario: A trial build finishes
- **WHEN** a manually dispatched build passes validation
- **THEN** its artifacts SHALL be downloadable and distinguished from formal releases
- **AND** no GitHub Release SHALL be created

#### Scenario: A formal build finishes
- **WHEN** a valid tagged build passes validation
- **THEN** its package and checksum SHALL be attached to a draft for that tag

### Requirement: Publication retries preserve released content
Repeating publication for a tag SHALL preserve matching existing assets, reject conflicting same-name draft assets, and leave an already published Release unchanged.

#### Scenario: An upload is retried
- **WHEN** an existing draft attachment has the expected name and identical bytes
- **THEN** publication SHALL reuse it without rebuilding or replacing it

#### Scenario: A draft asset conflicts
- **WHEN** an existing same-name draft attachment has different bytes
- **THEN** publication SHALL fail explicitly without overwriting that attachment

#### Scenario: The tag already has a published Release
- **WHEN** publication is rerun for that tag
- **THEN** the published release and its attachments SHALL remain unchanged
