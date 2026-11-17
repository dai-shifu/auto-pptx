## Why

Code review identified multiple resource leak paths in the core generation pipeline: Excel Workbook handles are leaked on exception paths (line 85-122 in `generate()`), and repeated Presentation load/unload during GUI Sheet switching relies on GC for ZIP file closure. These are correctness issues that degrade robustness in long-running GUI sessions and production batch runs.

## What Changes

- **Exception-safe Workbook lifecycle** in `generator.py:generate()` — use `try/finally` to guarantee `wb.close()` on all exit paths
- **Reduce repeated Presentation loads** in `gui.py:_auto_detect()` — avoid re-loading the template PPT when only the selected Sheet changes and the template hasn't changed
- **Encapsulate `_sldIdLst` manipulation** — extract the slide-pruning code into a helper function in `pptx_engine.py`, isolating python-pptx private API usage to one location
- **TOML string escaping** in `config.py:save_config()` — prevent malformed TOML when mapping values contain special characters

## Capabilities

### New Capabilities

- `resource-lifecycle`: Guarantees that file handles (`openpyxl.Workbook`, `pptx.Presentation`) are properly released in all code paths, including exceptions. Template Presentation objects are not re-loaded when only the Sheet selection changes.

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- **Affected code**: `src/generator.py`, `src/gui.py`, `src/pptx_engine.py`, `src/config.py`
- **No breaking changes**: all public APIs remain compatible
- **No new dependencies**
- **Tests**: existing test suite should continue to pass; no new test surface needed (existing tests already cover the same code paths)
