# Repository Guidelines

Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, code style and PR requirements, and [docs/开发.md](docs/开发.md) for modules and build instructions.

- Follow Scott Adams’s “The Day You Became A Better Writer” and the [documentation guidelines](CONTRIBUTING.md#文档写作): lead with the point, use short sentences and active verbs, and remove repetition. Preserve technical meaning. Do not rewrite existing specifications or archives solely to change their style.
- Keep changes minimal and focused. Preserve Python 3.11 compatibility, four-space indentation and existing naming conventions.
- Keep the mapping direction as Excel column → PPT placeholder. Saved selections take priority over automatic suggestions.
- Preserve `{{tpl::name}}` markers and unmapped placeholders so generation warnings remain useful. Generation removes original template pages and retains generated pages.
- Keep the complete `openspec/` structure public. For substantial behavior changes, update the corresponding proposal, design, specifications and tasks alongside implementation. Current specifications describe current requirements; archives record historical decisions.
- Use the shared builders in `tests/create_fixtures.py`; keep committed fixtures synchronized. Write test output to temporary directories and distribute only synthetic or reviewed public data.
- Run relevant tests and the full suite before submitting. GUI tests require a working display; skips do not verify GUI behavior.
- Keep personal configuration, credentials, agent settings and maintainer operation notes out of public commits. The runtime `config.toml` is created beside the application entry point.
- Use Git Bash and Python helpers for Windows maintenance. Maintain the version in `pyproject.toml`; user release assets contain the standalone exe and optional SHA-256.
