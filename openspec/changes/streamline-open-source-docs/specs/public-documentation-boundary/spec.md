## ADDED Requirements

### Requirement: Public documentation serves users and contributors
Public documentation SHALL retain application usage, examples, source setup, testing, code conventions and contribution instructions. It SHALL identify GitHub as the development and contribution repository and Gitee as a one-way mirror and planned alternative download channel. It SHALL describe actual download availability without fabricated links or maintainer task lists.

#### Scenario: A contributor starts from the public repository
- **WHEN** a contributor reads the README
- **THEN** it SHALL link to a contribution guide and development documentation with setup, test, module and pull-request guidance

### Requirement: OpenSpec and shared agent guidance remain public
The repository and source exports SHALL include the complete OpenSpec structure: configuration, current specifications, change proposals, designs, tasks, archives and reviewed general verification evidence. A concise public AGENTS.md SHALL retain shared project constraints and refer to the contribution guide.

#### Scenario: Historical technical evidence is reviewed
- **WHEN** general verification reports and synthetic screenshots are included
- **THEN** they SHALL retain their technical results and historical context
- **AND** personal handover notes, identities and publication-account operations SHALL remain in local material

### Requirement: Maintainer operations remain local
First-publication instructions, account configuration, manual upload steps and actual publication acceptance records SHALL remain in a Git-ignored local directory. Personal agent skills and settings, root runtime configuration and one-time migration tools SHALL be untracked. Release descriptions SHALL contain user-facing package information without maintainer acceptance tasks.

#### Scenario: A release draft is generated
- **WHEN** the existing publisher creates a draft
- **THEN** its description SHALL retain executable startup and checksum information and omit manual publication tasks

### Requirement: Source exports retain collaboration resources and exclude local material
Source exports SHALL exclude .local directories at every level, personal agent settings and skills, runtime configuration and one-time migration tooling, even when tracked or explicitly included. They SHALL retain public documentation, shared AGENTS.md, complete OpenSpec and application build/test resources.

#### Scenario: Local material is tracked or explicitly included
- **WHEN** an export candidate contains local maintainer material or personal tool settings
- **THEN** it SHALL be absent from the exported tree, ZIP and manifest
- **AND** public contribution documents and OpenSpec records SHALL remain present

#### Scenario: A contributor tests the public snapshot
- **WHEN** the full application suite runs from the public snapshot
- **THEN** it SHALL succeed without local tools, personal settings or a pre-existing runtime configuration
