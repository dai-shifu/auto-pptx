## Context

The codebase assumes Row 1 is always the header row. Four locations hardcode this:

```
excel_reader.py:97     headers = raw_rows[0]
excel_reader.py:38     headers = rows[0]           (legacy read_excel)
generator.py:41  ws.cell(row=1, …)       (generate header read)
gui.py:212             max_row = len(self._rows) + 1  (Treeview row→Excel mapping)
```

Example workbooks in batch-generation workflows frequently have a description/note in Row 1:

```
Row 1: 项目明细结果汇总表
Row 2: 项目编号 | 填料 | 日期 | 批次 | …  ← actual headers
Row 3: DEMO-001   | GST  | …                   ← data
```

The existing `extract_project_ids()` and `find_row_by_project_id()` already accept a `header_row` parameter — proving the need was foreseen but never extended to the main pipeline.

## Goals / Non-Goals

**Goals:**
- Let users specify which row is the header via `config.toml` (`header_row` key)
- Auto-detect the header row by comparing candidate rows (1, 2) against template names
- Persist detected/configured `header_row` in `config.toml` after generation
- Default to 1 when nothing is configured and detection is inconclusive

**Non-Goals:**
- Arbitrary header row positions beyond Row 1–2 (auto-detection only checks these two)
- Multi-row headers (e.g., Row 1–2 merged)
- Excel files where the header row is the only row (no data)
- CLI-only batch mode configuration

## Decisions

### Decision 1: Auto-detect by template-name intersection scoring

**Chosen**: For each candidate row (1 and 2), extract the cell values as candidate headers, build the column-value sets, and compute intersection ratio with `{{tpl::name}}` identifiers. Pick the row with the higher ratio. If both score zero or tie, default to 1.

```
candidate_1: ["说明", "备注", "空", …] ∩ tpl_names → ratio = 0.0
candidate_2: ["填料", "日期", "项目编号", …] ∩ tpl_names → ratio > 0.0
⇒ pick Row 2
```

**Alternatives considered**:
- Regex heuristics (e.g., "if Row 1 contains only Chinese characters, skip") — fragile, language-dependent
- Always check both rows — we do this, but with domain-appropriate scoring

**Rationale**: Reuses existing `detect_template_column()` scoring logic. Tpl-name intersection is already the strongest signal that a column is a "real" header.

### Decision 2: `header_row` flows through the pipeline, not inferred

**Chosen**: `header_row` is passed explicitly through the call chain:

```
config.toml → App._auto_load_config() → self._header_row
  → read_sheet_rows(excel_path, sheet, header_row)
  → generate(prs, excel, sheet, rows, output, header_row=…)
```

The GUI is the single source of truth; `generate()` receives it as a parameter.

**Alternatives considered**:
- Auto-detect inside `generate()` independently — would diverge from what the user sees in the GUI
- Store `header_row` in a module-level global — breaks the explicit-data-flow pattern

**Rationale**: Explicit parameter passing is consistent with how `template_column` and `mapping` already flow. The GUI owns detection; the generator trusts what it receives.

### Decision 3: `read_sheet_rows()` return value stays the same shape

**Chosen**: `read_sheet_rows()` still returns `(headers, rows)` where `rows` is a list of data rows (lists of strings). The `header_row` parameter shifts which Excel row is treated as the header.

The returned `rows` are always 0-indexed from the GUI's perspective, but the Treeview maps `row_idx` to Excel row via `row_idx + header_row + 1`.

**Alternatives considered**:
- Return absolute Excel row numbers inside each row — adds complexity, callers can compute it
- Return a dataclass instead of tuple — unnecessary for 2 values

**Rationale**: Minimal API change. The only caller that needs absolute row numbers (`generate()`) receives `selected_rows` which are already absolute Excel row numbers, so no mapping is needed there.

### Decision 4: Config field naming and backward compatibility

**Chosen**: Add `header_row: int = 1` to the `Config` dataclass. The `load_config()` function reads it with `int(data.get("header_row", 1))`. The `save_config()` function writes it as a top-level key.

Old config files without `header_row` → default 1 → identical behavior to before.

**Rationale**: Follows the existing pattern for `template_column` and `mapping`. No migration needed.

### Decision 5: GUI header row selector — automatic vs manual

**Chosen**: Add a `ttk.Spinbox` next to the "模板列" dropdown, labeled "标题行:", with range 1–10. Initially populated by auto-detection. User can spin it manually. Changing it triggers a full `_refresh_all()` (rebuild Treeview with different headers).

Auto-detection only fires on `_refresh_all()` when `header_row` is not from config (tracked by `_hrow_from_config` flag, same pattern as `_tcol_from_config`).

**Rationale**: Consistent with the existing UX pattern for template column — auto-detect first, user overrides are sticky.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Auto-detection picks the wrong row if Row 1 happens to match tpl names better than Row 2 | Manual override via Spinbox; detection result is visible immediately in the Treeview column headers |
| Row > 2 could be headers in some edge case | Spinbox allows up to 10; auto-detection only checks 1–2 but user can manually go higher |
| `read_sheet_rows()` with `header_row=2` on a 2-row Excel returns empty headers (Row 2 is headers, no data rows) | This is correct behavior — an Excel with only a header row has no data |
| `selected_rows` in the range `[header_row+1, …]` are passed to `generate()` — if user manually sets `header_row` higher than the number of rows, `selected_rows` may include the header row itself | Guard: `generate()` should skip or warn if `selected_rows` contains rows ≤ `header_row` |
