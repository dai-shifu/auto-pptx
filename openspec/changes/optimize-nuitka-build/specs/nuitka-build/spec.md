## ADDED Requirements

### Requirement: Windows builds require redistributable runtimes
Windows builds SHALL require Nuitka to include Windows runtime DLLs and SHALL fail when those runtime files cannot be located. Non-Windows builds SHALL NOT receive Windows-only options.

#### Scenario: Runtime files cannot be found
- **WHEN** Nuitka cannot locate required redistributable runtime files during a Windows build
- **THEN** the build SHALL fail and preserve the compiler exit status
- **AND** packaging and publication SHALL NOT proceed

### Requirement: Builds produce diagnostic evidence
Builds SHALL request a Nuitka XML compilation report under dist. Successful builds SHALL print elapsed compilation time and final single-file size. CI SHALL preserve reports separately from user release assets when available, including after compilation failure.

#### Scenario: A build succeeds
- **WHEN** compilation produces the final executable
- **THEN** the script SHALL print elapsed seconds, executable size and report location

#### Scenario: Compilation fails
- **WHEN** Nuitka returns a nonzero status
- **THEN** the script SHALL return that status without a success summary
- **AND** CI SHALL attempt to preserve the report if present

### Requirement: Dependency inclusion preserves generation behavior
Builds SHALL use dependency analysis instead of broad third-party package inclusion where verified. Necessary dynamic imports, package data, Tk resources and single-file compression SHALL be preserved. Verification SHALL cover Excel reading and PPT generation including image and chart relationships before declaring platform acceptance complete.

#### Scenario: A package inclusion is narrowed
- **WHEN** a whole-package inclusion is removed
- **THEN** validation SHALL record the platform and outcome
- **AND** missing modules or resources SHALL be included specifically or the package inclusion SHALL be retained

### Requirement: Windows CI reuses compatible compiler caches
Windows CI SHALL restore and save the Nuitka cache using keys isolated by operating system, architecture, Python version and dependency lockfile. Updated caches SHALL use a unique run key and restore from a compatible prefix. Cache misses SHALL NOT prevent builds.

#### Scenario: A compatible earlier cache exists
- **WHEN** a later workflow runs with the same platform and dependencies
- **THEN** it SHALL attempt to restore that cache before compilation and save updated contents after success

### Requirement: CI validates workflow configuration
CI SHALL statically check all workflow files on branch pushes and pull requests. The check SHALL include GitHub Actions expression validation, not just YAML parsing. Windows release builds SHALL wait for this check to pass.

#### Scenario: A release expression uses an unavailable context
- **WHEN** a branch push or pull request changes the Release workflow to reference a context unavailable at that location
- **THEN** the workflow lint check SHALL fail without needing to trigger a Windows build

### Requirement: Windows acceptance requires source and executable evidence
Windows release validation SHALL run the source test suite with working Tk before compiling the executable. Tk initialization failures and skipped required GUI tests SHALL NOT count as platform acceptance. Final executable acceptance SHALL verify startup, first-run configuration, Excel reading and generation with synthetic text, table, image, chart and embedded workbook content. Source-entry generation SHALL NOT substitute for executable generation. Acceptance SHALL include the same executable in a clean Windows environment without project Python or build tools, with the executable hash and the target environment's runtime state recorded.

#### Scenario: A GUI test cannot initialize Tk
- **WHEN** a required Windows GUI test fails to initialize Tk or is skipped because its required desktop is unavailable
- **THEN** Windows platform acceptance SHALL remain incomplete
- **AND** the environment failure SHALL be reported separately from application failures

#### Scenario: The executable is checked outside the build environment
- **WHEN** a Windows executable is submitted for final acceptance
- **THEN** validation SHALL record its hash and verify startup, first-run configuration and synthetic generation in a clean Windows environment
- **AND** generated content and relationships SHALL be checked against the expected text, table, image, chart and embedded workbook results
- **AND** the draft SHALL NOT be published before the executable with that hash passes acceptance

### Requirement: Windows performance evidence identifies cache conditions
Windows cold and warm build measurements SHALL use the same source, paths, machine, Python, dependencies and compiler. The cold measurement SHALL start with an empty dedicated Nuitka cache and no previous build objects. The warm measurement SHALL reuse that cache without reusing previous build objects. Results SHALL record elapsed time, final executable size and compiler-cache hits and misses. Claims about dependency-narrowing improvements SHALL compare equivalent cold and warm measurements for both configurations.

#### Scenario: Only final-configuration measurements are available
- **WHEN** cold and warm Windows builds are measured for the final configuration without equivalent original-configuration measurements
- **THEN** validation SHALL report those results and their cache conditions
- **AND** it SHALL NOT attribute a Windows speedup or size reduction percentage to dependency narrowing

### Requirement: Source development is independent of the Windows build toolchain
Developers on macOS, Linux and Windows SHALL be able to run and test the project from source without installing Visual Studio or Build Tools. Windows executable builds SHALL use the dedicated Windows CI environment. A local runtime preflight failure SHALL report the missing build environment without downloading or installing a Windows toolchain.

#### Scenario: A developer works on macOS or Linux
- **WHEN** a developer changes and tests source code on macOS or Linux
- **THEN** the developer SHALL use the source runtime and test dependencies for that platform
- **AND** the Windows executable SHALL be produced by the Windows CI workflow

#### Scenario: The local Windows runtime preflight fails
- **WHEN** required redistributable files cannot be found on a developer's Windows machine
- **THEN** preflight SHALL fail with a diagnostic
- **AND** it SHALL NOT download or install Visual Studio or Build Tools
