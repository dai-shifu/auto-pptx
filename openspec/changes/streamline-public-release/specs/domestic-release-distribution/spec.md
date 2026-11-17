## ADDED Requirements

### Requirement: Download instructions distinguish verified domestic access
The README SHALL prominently explain how to obtain the Windows package and a domestic download option. Actual links SHALL be configured using real project addresses; unverified or unconfigured domestic access SHALL be clearly identified and SHALL NOT be advertised as verified.

#### Scenario: Domestic hosting is not yet configured
- **WHEN** documentation is prepared before domestic hosting validation
- **THEN** it SHALL identify the domestic option as pending and SHALL NOT present a fabricated working download URL

#### Scenario: Domestic hosting passes validation
- **WHEN** a domestic channel has been configured and verified
- **THEN** documentation SHALL provide a clear domestic Windows download entry and retain the primary release entry

### Requirement: Channels distribute identical release bytes
All channels SHALL distribute the same versioned Windows exe and SHA-256 from one successful build. Domestic source mirrors SHALL be one-way copies of the public development repository and SHALL direct contributions to that primary repository.

#### Scenario: A package is copied to a domestic channel
- **WHEN** a maintainer uploads a release package to the selected domestic channel
- **THEN** the downloaded package SHALL match the original SHA-256 and version
- **AND** it SHALL NOT be rebuilt separately for that channel

### Requirement: Domestic availability is verified before final publication
Before a release is announced as domestically available, maintainers SHALL check the chosen channel's current attachment constraints against the actual exe and test downloading from a domestic network in a signed-out browser. The release checklist SHALL record download completion, account or client requirements, checksum verification, first-run configuration creation, and Windows startup and minimal generation results. A domestic direct-download channel SHALL pass without requiring a platform account or a separate download client.

#### Scenario: Candidate channel requires an account or cannot hold the package
- **WHEN** verification finds mandatory login, a mandatory client, failed downloads, or incompatible attachment capacity
- **THEN** the candidate SHALL remain unverified and maintainers SHALL select another channel or explicitly defer domestic availability
- **AND** documentation SHALL NOT claim the candidate satisfies direct domestic downloads

#### Scenario: Download and program verification succeed
- **WHEN** signed-out domestic download, checksum verification, and Windows package checks pass
- **THEN** the checklist SHALL record the version, channel, test date, and results before formal publication

### Requirement: Distribution failure can be retried independently
The initial domestic distribution process SHALL provide documented manual upload and verification steps. Failed domestic uploads SHALL reuse the original package and checksum; a GitHub draft SHALL remain a draft until the planned domestic distribution and final package checks pass.

#### Scenario: Domestic upload fails
- **WHEN** the domestic channel rejects or interrupts an upload
- **THEN** maintainers SHALL retain the original build artifacts and retry distribution without recompiling
- **AND** the release checklist SHALL leave domestic verification incomplete
