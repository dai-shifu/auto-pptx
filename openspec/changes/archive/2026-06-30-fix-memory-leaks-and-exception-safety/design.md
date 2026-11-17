## Context

The codebase manages two external resources: openpyxl Workbooks (read from disk) and python-pptx Presentations (loaded into memory, saved to disk). Neither type has an explicit `close()` method — Workbooks have `wb.close()`, but Presentations rely on `__del__` for underlying ZIP file cleanup.

The current `generate()` function in `generator.py` opens a Workbook at line 32 and calls `wb.close()` at line 124, but the intervening code (loop body at lines 87-122 performing slide cloning and text replacement) can throw. Any exception skips the close, leaking the file handle.

In `gui.py`, `_auto_detect()` loads a Presentation on every `_refresh_all()` call — which fires on every Sheet change. Each Presentation holds an open ZIP file descriptor. While CPython's reference counting often reclaims these immediately, python-pptx's internal Part/Package object graph contains circular references that delay GC. In a long-running GUI session with frequent Sheet switching, file descriptors accumulate.

## Goals / Non-Goals

**Goals:**
1. Guarantee Workbook closure in `generate()` regardless of exceptions
2. Eliminate redundant Presentation loads in `gui.py` when only the Sheet changes
3. Encapsulate `_sldIdLst` manipulation into a single helper function for maintainability
4. Prevent TOML formatting issues when mapping values contain special characters

**Non-Goals:**
- Refactoring the overall architecture or adding a CLI mode
- Adding explicit `.close()` to python-pptx (upstream change)
- Full TOML serialization library replacement
- Adding resource pooling or lazy loading

## Decisions

### Decision 1: `try/finally` for Workbook lifecycle in `generate()`

**Chosen**: Wrap lines 38-135 of `generate()` in `try/finally` with `wb.close()` in the `finally` block.

**Alternatives considered**:
- `with` statement via `contextlib.closing` — cleaner but `openpyxl.Workbook` is not a context manager natively; wrapping with `closing` is equivalent to try/finally but adds an import
- Early `wb.close()` after reading all data into memory — would close before generation loop, eliminating the leak window entirely, but requires restructuring to read all rows upfront. This is actually the better approach but changes more code.

**Rationale**: `try/finally` is the minimal surgical fix. The data read pattern (line 40-43 for headers, then per-row cell reads inside the loop) makes moving the read earlier a larger refactor. `try/finally` achieves exception safety with minimal diff.

### Decision 2: Skip Presentation reload when only Sheet changes

**Chosen**: In `_auto_detect()`, check if the template path has changed since the last invocation. If unchanged, short-circuit and return without reloading.

Implementation: add a `_last_tpl_path: str | None` field to the `App` class. When `_auto_detect()` is called with the same path, skip the `load_template()` call. Reset to `None` when `_browse_tpl()` fires.

**Alternatives considered**:
- Cache the Presentation object — would hold the ZIP handle open, defeating the purpose
- Use a weakref cache — overengineered for this use case

**Rationale**: The simplest correct fix. Template detection data doesn't change when the user switches sheets. The only trigger for re-detection is the user selecting a different template PPT file.

### Decision 3: Extract `_sldIdLst` manipulation into a helper

**Chosen**: Add a `prune_slides(prs, count)` function to `pptx_engine.py` that deletes the first `count` slides from the presentation, encapsulating the private-API access.

Both `generate()` call sites (empty selection at line 55-58, and final prune at lines 127-131) will call this helper.

**Alternatives considered**:
- `prs.slides.delete_slide(index)` — exists but does an in-place deletion that shifts indices, making batch deletion awkward without reverse iteration
- Monkey-patching — fragile and unnecessary

**Rationale**: Similar code appears in two places. Extracting it DRYs the code, documents the intent, and creates a single point to update if python-pptx changes its internal API.

### Decision 4: TOML string escaping in `save_config()`

**Chosen**: Replace literal `f'"{excel_col}" = "{placeholder}"'` with a helper that escapes embedded double quotes and backslashes in both key and value strings.

**Rationale**: Current data sources (Excel column headers, placeholder names) rarely contain quotes, but the spec doesn't forbid it. A simple `str.replace('"', '\\"')` is sufficient for TOML basic strings.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Adding try/finally changes indentation of ~100 lines, making git blame noisy | Accept as one-time cost; the diff is mechanically trivial inside the try block |
| `_auto_detect()` skip might miss a case where the template file content changed on disk (same path) | File modification time check could be added, but in practice users don't edit template files while the GUI is open. If this becomes an issue, add `os.path.getmtime()` comparison. |
| `prune_slides()` still uses `_sldIdLst` — if python-pptx renames/removes it, this breaks | The helper localizes the breakage to one function, making the fix trivial when upgrading python-pptx |
| TOML basic-string escaping won't handle all edge cases (newlines, control chars) | Only applies to Excel column headers and placeholder names, which are validated elsewhere. If needed, switch to TOML literal strings (`''`) first. |
