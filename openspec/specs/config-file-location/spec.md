# Config File Location

## Purpose

Define where the application reads and writes its persistent configuration in
development and packaged builds, including safe behavior when the file is
missing or cannot be created.

## Requirements

### Requirement: Config file saved beside executable in packaged builds

When the application is packaged as a standalone executable (Nuitka `--onefile`), the system SHALL read and write `config.toml` in the same directory as the executable file, detected via `sys.argv[0].resolve().parent`.

#### Scenario: Onefile executable reads config from its own directory

- **WHEN** the application is launched from a Nuitka `--onefile` executable at `D:\dist\auto-pptx.exe`
- **THEN** `config.toml` SHALL be read from and written to `D:\dist\config.toml`

#### Scenario: Development mode uses project root

- **WHEN** the application is run in development mode via `python run.py`
- **THEN** `config.toml` SHALL be read from and written to the project root directory (where `run.py` resides, determined by `sys.argv[0].resolve().parent`)

### Requirement: Config file auto-created on startup when missing

When `config.toml` does not exist at the resolved path, the system SHALL automatically create it with default configuration values at startup, rather than waiting for a successful generation.

#### Scenario: First launch creates config with defaults

- **WHEN** the application is launched for the first time and no `config.toml` exists
- **THEN** a `config.toml` file SHALL be created at the resolved path containing default values (`template_column = "填料"`, `header_row = 1`)

#### Scenario: Subsequent launch loads existing config

- **WHEN** the application is launched and `config.toml` already exists
- **THEN** configuration SHALL be loaded from the existing file without overwriting it

#### Scenario: Missing config does not prevent application from working

- **WHEN** `config.toml` is missing and the target directory is read-only (cannot create file)
- **THEN** the application SHALL still launch with in-memory defaults and display a status message indicating the config could not be saved

### Requirement: load_config returns defaults when file is absent

The `load_config()` function SHALL return a `Config` with default values when the target file does not exist, rather than raising `FileNotFoundError`.

#### Scenario: load_config on missing file

- **WHEN** `load_config()` is called with a path that does not exist
- **THEN** it SHALL return `Config(template_column="填料", header_row=1, mapping={})` without raising an exception

#### Scenario: load_config on invalid TOML still raises

- **WHEN** `load_config()` is called with a path to a file containing invalid TOML syntax
- **THEN** it SHALL raise `ValueError("配置文件格式错误: ...")`
