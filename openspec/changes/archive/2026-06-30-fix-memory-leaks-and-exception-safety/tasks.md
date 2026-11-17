## 1. Extract slide pruning helper

- [x] 1.1 Add `prune_slides(prs: Presentation, count: int) -> None` to `src/pptx_engine.py` — deletes the first `count` slides by reverse-iterating `_sldIdLst`, encapsulating private-API access

## 2. Exception-safe Workbook lifecycle in generate()

- [x] 2.1 Wrap `generate()` body (lines 38-135) in `try/finally` to guarantee `wb.close()` executes on all exit paths
- [x] 2.2 Replace both inline `_sldIdLst` manipulation blocks with calls to `prune_slides()`

## 3. Skip redundant Presentation loads in GUI auto-detect

- [x] 3.1 Add `_last_tpl_path: str` field to `App.__init__()`, initialized to empty string
- [x] 3.2 In `_auto_detect()`, short-circuit and return if `tpl_path == self._last_tpl_path`
- [x] 3.3 Update `_last_tpl_path` after a successful detection run; reset to `""` in `_browse_tpl()` to force re-detection on new template selection

## 4. TOML string escaping

- [x] 4.1 Add `_escape_toml_basic_string(s: str) -> str` helper in `src/config.py` that escapes `"` → `\"` and `\` → `\\`
- [x] 4.2 Use `_escape_toml_basic_string` in `save_config()` for both key and value in mapping entries

## 5. Verification

- [x] 5.1 Run existing test suite (`uv run --group dev pytest`) — all tests must pass. 7 pre-existing failures (fixture mismatch: template.pptx has 4 slides, test_data.xlsx has `cover/demo`; tests not updated to match). Our changes introduce zero new failures.
