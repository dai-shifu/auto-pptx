## 1. Reproducible Test Baseline

- [x] 1.1 Extract shared XLSX and PPTX fixture builders that accept a destination path and define the canonical Sheets, rows, slides, markers, and placeholders
- [x] 1.2 Migrate generation and integration tests away from mutable or missing files under `docs/` to temporary repository-owned fixtures
- [x] 1.3 Regenerate the committed fixtures from the shared builders or remove them where temporary fixtures make them redundant
- [x] 1.4 Add semantic fixture-contract tests for slide count, template markers, Sheet names, headers, and representative row values
- [x] 1.5 Run the full suite and classify any remaining failures as product defects before changing runtime behavior

## 2. Deterministic Auto-Detection

- [x] 2.1 Add a shared template-value tokenizer that splits `/`, trims whitespace, and discards empty tokens, then use it in template-column detection
- [x] 2.2 Preserve first-seen order when collecting unique placeholders from text boxes and table cells
- [x] 2.3 Implement deterministic two-pass exact-then-fuzzy mapping with one-to-one source and destination constraints
- [x] 2.4 Return mapping conflict diagnostics for equal-score and competing candidates instead of silently overwriting dictionary entries
- [x] 2.5 Replace header-row overlap minimization with candidate validation and downstream template-column evidence, retaining row 1 as the no-evidence fallback
- [x] 2.6 Add unit tests for slash-separated cells, stable ordering, exact-match priority, ambiguous mappings, preamble rows, and no-evidence fallback

## 3. GUI Detection State

- [x] 3.1 Separate cached template metadata from Excel-dependent template-column and mapping suggestions
- [x] 3.2 Recompute Excel-dependent suggestions after Excel file, Sheet, header row, headers, or sampled rows change
- [x] 3.3 Keep explicit config and user selections authoritative while refreshing only automatically derived values
- [x] 3.4 Add focused state tests or extracted-controller tests proving that workbook and header changes cannot reuse stale suggestions

## 4. Generation Validation and Results

- [x] 4.1 Define structured detection diagnostics and a `GenerationResult` value containing page counts, skipped inputs, unmatched templates, unresolved placeholders, and warnings
- [x] 4.2 Add preflight validation for duplicate non-empty headers, missing mapped columns, and multiple source columns mapped to one placeholder
- [x] 4.3 Collect missing-template and skipped-row diagnostics during generation without losing successfully generated slides
- [x] 4.4 Scan generated slides for unresolved non-template placeholders and include their unique names in the result
- [x] 4.5 Treat zero generated pages as an error and ensure no final output file is left behind
- [x] 4.6 Update the GUI to present the output path, page count, and warnings from the structured result in one completion summary

## 5. Verification and Change Reconciliation

- [x] 5.1 Add end-to-end tests for mixed success and skipped rows, unresolved placeholders, duplicate headers, invalid mappings, and zero-page output
- [x] 5.2 Run `uv run --group dev pytest` and confirm the complete suite passes without untracked `docs/` inputs
- [x] 5.3 Manually verify Row 1, Row 2, and Row 3 header layouts plus switching Excel files and Sheets while retaining the same PPT template
- [x] 5.4 Re-run `openspec validate --change stabilize-generation-pipeline` and reconcile completed header-detection tasks with `improve-header-row-detection`
