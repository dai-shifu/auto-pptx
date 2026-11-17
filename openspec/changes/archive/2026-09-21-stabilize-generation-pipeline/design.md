## Context

The GUI currently mixes template analysis, data-dependent auto-detection, widget state, and generation warnings. Detection is cached only by template path even though its result also depends on the Excel file, Sheet, header row, and rows. Placeholder discovery uses a set, then reverses a placeholder-to-column mapping into a column-to-placeholder dictionary, making collisions order-dependent. Generation communicates skipped work through console output and can report success even when placeholders remain or no useful slide was produced.

The repository also contains binary fixtures that no longer match `tests/create_fixtures.py`, and some tests depend on mutable or absent files under `docs/`. A stable implementation therefore requires test-data repair alongside runtime changes.

## Goals / Non-Goals

**Goals:**

- Make detection repeatable for identical inputs and refresh it for every data-context change.
- Support the documented slash-separated template-column format during detection as well as generation.
- Detect ambiguous mappings instead of silently choosing an order-dependent winner.
- Improve automatic header-row selection using evidence from the rows below each candidate.
- Give callers a structured result and prevent zero-page output from being reported as success.
- Make the automated test suite self-contained and reproducible.

**Non-Goals:**

- Reimplement slide cloning, animation/background preservation, or run-level formatting preservation.
- Add background threads, pagination, or other GUI performance work.
- Change the config file format or the Excel-to-placeholder mapping direction.
- Add new runtime dependencies.

## Decisions

### 1. Separate template analysis from data-dependent detection

Template-derived metadata (template names and ordered placeholders) will be computed independently from Excel-derived suggestions. If caching is retained, only template-derived metadata may be cached, keyed by resolved template path and file modification metadata. Template-column and mapping suggestions will be recomputed whenever the Excel path, Sheet, header row, headers, or sampled rows change.

This avoids a large composite cache with difficult invalidation rules while still allowing PPT parsing to be optimized later. The alternative of keeping the current template-path cache and manually resetting it in every event handler is rejected because new input paths can easily miss an invalidation hook.

### 2. Use shared normalization with deterministic one-to-one mapping

Template-column values will be split on `/`, trimmed, and empty tokens discarded before comparison with template names. Placeholder discovery will preserve first-seen slide/shape order rather than return set order.

Mapping will run in two deterministic passes: case-insensitive exact matches first, then edit-distance matches. A source column and destination placeholder can each participate in at most one automatic mapping. Equal-score or competing candidates will remain unmapped and produce a conflict diagnostic for manual resolution.

Fuzzy matching remains available for compatibility, but it will no longer silently resolve ambiguity based on iteration order.

### 3. Score header candidates by downstream usefulness

For each candidate among the first five rows, the detector will first require at least two non-empty, unique header values. It will then treat subsequent rows as data and calculate whether a template column can be detected. Candidates will be ranked by template-column match confidence, header uniqueness, and then earliest row as the stable tie-breaker. If no candidate has positive downstream evidence, row 1 remains the default.

This directly tests the purpose of a header row. Looking only for low overlap between a row and template names cannot distinguish a header from an explanatory subtitle.

### 4. Introduce structured diagnostics and generation results

Detection will expose suggestions plus diagnostics instead of encoding all uncertainty as a partial dictionary. Generation will return a small result value containing generated-page count, skipped-row/template information, unresolved placeholders, and human-readable warnings.

Duplicate non-empty headers, invalid explicit mappings, and zero generated pages are validation errors. Missing templates and unresolved placeholders are collected as warnings when at least one valid slide is generated. The GUI will show one summary after completion; command-line logging may remain as a compatibility aid but is not the source of truth.

The alternative of treating every unresolved placeholder as fatal is rejected because templates can intentionally retain placeholders for later manual editing.

### 5. Generate test assets from repository-owned definitions

Unit and integration tests will create the needed XLSX and PPTX assets in `tmp_path` from shared fixture builders. Tests will not require customer files under `docs/`. The committed sample fixtures, if retained for developer convenience, will be regenerated from the same builders and covered by semantic consistency checks such as slide names, row values, and Sheet names rather than byte hashes.

## Risks / Trade-offs

- **[Previously accepted fuzzy mappings become unresolved]** → Surface the competing candidates in the GUI so the user can resolve them explicitly.
- **[Header detection still cannot infer every workbook layout]** → Keep the manual header-row control authoritative and cover common preamble/merged-row layouts with tests.
- **[Structured return values require call-site updates]** → Update the GUI and tests in the same change; keep exceptions for invalid inputs to preserve the existing error flow.
- **[Fixture builders duplicate some production-format knowledge]** → Centralize builders in one test support module and keep fixtures deliberately small.

## Migration Plan

1. Repair fixture builders and migrate tests away from `docs/` dependencies to establish a trustworthy baseline.
2. Add deterministic detection APIs and regression tests while preserving the public mapping direction.
3. Add validation/result types and update the generator and GUI call sites.
4. Run the full suite and manually verify the active header-row scenarios before archiving the related older change.

Rollback is limited to reverting this change; no persisted user data or configuration format is migrated.

## Open Questions

- Whether unresolved placeholders should become fatal under a future optional "strict generation" mode.
- Whether committed binary fixtures remain useful once all tests generate temporary assets.
