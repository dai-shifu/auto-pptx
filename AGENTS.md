# Repository Guidelines

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, and PR guidelines, and [docs/开发.md](docs/开发.md) for modules and builds.

- Keep changes focused and preserve Python 3.11 compatibility.
- Map Excel columns to PPT placeholders. Manual and saved selections take priority over automatic suggestions.
- Keep only generated slides in the output. Preserve `{{tpl::name}}` markers and leave unmapped placeholders visible with a warning.
- Keep the complete `openspec/` structure public. Update the corresponding proposal, design, specs, and tasks for substantial behavior changes. Preserve archives as historical records.
- Use the shared fixture builders in `tests/create_fixtures.py`, keep committed fixtures in sync, and write test output to temporary directories. A skipped GUI test does not verify GUI behavior.
- Keep runtime configuration, credentials, personal agent settings, and maintainer operation notes out of public commits. Distribute only synthetic or reviewed public data.
