## Why

The current generation pipeline can silently reuse stale auto-detection results, produce non-deterministic mappings, and save presentations with unresolved placeholders. At the same time, the test suite has drifted from its committed fixtures and real-world sample files, so regressions cannot be distinguished reliably from broken test data.

## What Changes

- Make template-column and placeholder mapping detection deterministic, conflict-aware, and compatible with slash-separated template values.
- Invalidate or recompute detection results whenever the PPT template, Excel file, Sheet, or header row changes.
- Strengthen header-row detection so explanatory rows are not selected solely because they have no template-name overlap.
- Validate duplicate headers, missing template matches, mapping conflicts, unresolved placeholders, and zero-page output before reporting generation success.
- Return a structured generation result containing page counts and warnings so the GUI can present one actionable summary.
- Replace tests that depend on mutable or missing files under `docs/` with reproducible generated fixtures, and keep committed binary fixtures synchronized with their generator.
- Add regression coverage for multi-template cells, cache invalidation, ambiguous mappings, header-row candidates, and output validation.

## Capabilities

### New Capabilities

- `deterministic-auto-detection`: Defines normalized template-column detection, one-to-one mapping suggestions, conflict handling, cache invalidation, and robust header-row selection.
- `generation-validation`: Defines preflight and post-generation validation plus structured success and warning reporting.
- `reproducible-test-fixtures`: Defines self-contained, deterministic test assets that do not depend on mutable customer files.

### Modified Capabilities

None.

## Impact

- Affected code: `src/auto_detect.py`, `src/gui.py`, `src/generator.py`, `src/excel_reader.py`, and potentially `src/pptx_engine.py` for unresolved-placeholder inspection.
- Affected tests: auto-detection, Excel reading, GUI state behavior, generation integration, template matching, and fixture generation tests.
- User-visible behavior: invalid or ambiguous input produces explicit warnings or validation errors instead of silent partial output; changing inputs always refreshes suggestions.
- Dependencies and file formats remain unchanged.
