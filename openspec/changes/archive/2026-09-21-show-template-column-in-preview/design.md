## Context

The Treeview preview is intentionally bounded so wide spreadsheets do not overwhelm the GUI. Its current helper returns the first five headers only, even though the selected template column controls page generation and can appear anywhere in the spreadsheet. Automatic detection runs before the Treeview rebuild, and manual selection already triggers a rebuild with checked-row preservation.

## Goals / Non-Goals

**Goals:**

- Make the active template column visible in every populated preview.
- Retain the compact first-five-column snapshot.
- Preserve column order, row values, and checked rows across template-column changes.
- Keep the column-selection rule independently testable without constructing tkinter widgets.

**Non-Goals:**

- Showing every Excel or mapped column.
- Changing template-column detection, mapping, generation, or configuration persistence.
- Changing Treeview selection semantics or column widths.

## Decisions

### Pass the selected template column into the preview helper

`_preview_columns` will accept `headers` and `template_column`. It will begin with indexed entries for the first five headers, then append the indexed template column only when that name is non-empty, exists in `headers`, and is not already selected.

This keeps row-value lookup index-based and isolates the behavior for unit testing. Computing the extra column directly inside `_rebuild_treeview` was considered but would couple the rule to tkinter state and make regression tests more expensive.

### Append rather than reorder

When the template column lies beyond the first five columns, it will appear on the right. Moving it to the front was considered, but appending preserves the established order and matches the user documentation.

### Reuse the existing refresh lifecycle

`_refresh_all` already completes automatic detection before rebuilding the Treeview, and `_on_tcol_change` already rebuilds with `preserve_checks=True`. No new event bindings or state are required.

## Risks / Trade-offs

- **[Preview can contain six data columns]** → Limit the exception to exactly one active template column and retain the horizontal scrollbar.
- **[Configured template column is absent from a newly selected Sheet]** → Ignore absent values in the preview helper and show only the available first five columns; existing validation remains responsible for generation errors.
- **[Duplicate header names make name lookup ambiguous]** → Preserve the existing first-match behavior; duplicate non-empty headers are already rejected by generation validation.
