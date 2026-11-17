## Why

The GUI data preview currently shows only the first five Excel columns, so an automatically detected or manually selected template column becomes invisible when it appears later in the sheet. Users need to see that value while choosing rows because it determines which PowerPoint template pages each row will generate.

## What Changes

- Keep the first five Excel columns in the data preview.
- Append the selected template column when it is not already among those five columns.
- Avoid duplicating the template column when it is already visible.
- Refresh the appended column after automatic detection or manual template-column selection while preserving checked rows during manual selection changes.
- Add focused regression tests for preview-column selection.

## Capabilities

### New Capabilities

- `data-preview-columns`: Defines how the GUI combines the first five Excel columns with the selected template column in the data preview.

### Modified Capabilities

None.

## Impact

- `src/gui.py`: preview-column selection and Treeview rebuilding.
- `tests/test_gui_state.py`: preview-column regression coverage.
- `docs/使用培训.md`: existing documented behavior becomes consistent with the implementation.
- No generation pipeline, file format, or dependency changes.
