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

When `config.toml` does not exist at the resolved path, the system SHALL create an empty file at startup. Startup SHALL NOT write preset template columns, header rows, or mappings.

#### Scenario: First launch creates an empty config

- **WHEN** the application is launched for the first time and no `config.toml` exists
- **THEN** the system SHALL create an empty `config.toml` at the resolved path
- **AND** the GUI SHALL start at row 1 without treating it as a saved selection, so header-row detection remains available

#### Scenario: Subsequent launch loads existing config

- **WHEN** the application is launched and `config.toml` already exists
- **THEN** configuration SHALL be loaded from the existing file without overwriting it

#### Scenario: Missing config does not prevent application from working

- **WHEN** `config.toml` is missing and the target directory is read-only (cannot create file)
- **THEN** the application SHALL still launch with in-memory defaults and display a status message indicating the config could not be saved

### Requirement: load_config returns no saved settings for absent or empty files

The `load_config()` function SHALL return a `Config` with no saved settings when the target file is absent or empty. Loading a missing file SHALL NOT create it.

#### Scenario: load_config on missing or empty file

- **WHEN** `load_config()` is called with a missing or empty file
- **THEN** it SHALL return `Config(template_column="", header_row=None, mapping={})` without raising an exception

#### Scenario: load_config on invalid TOML still raises

- **WHEN** `load_config()` is called with a path to a file containing invalid TOML syntax
- **THEN** it SHALL raise `ValueError("配置文件格式错误: ...")`
