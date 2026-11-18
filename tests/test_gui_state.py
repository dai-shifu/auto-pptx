from types import SimpleNamespace

import pytest

from src import gui
from src.auto_detect import detect_header_row
from tests.create_fixtures import DATA_HEADERS, DATA_SHEET, DETAIL_HEADERS, DETAIL_SHEET, build_test_xlsx


class _Var:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def _app_for_detection() -> gui.App:
    app = gui.App.__new__(gui.App)
    app.tpl_var = _Var("template.pptx")
    app.tcol_var = _Var()
    app.status_var = _Var()
    app._headers = ["模板", "标题"]
    app._rows = [["cover", "报告"]]
    app._auto_mapping = {}
    app._placeholders = []
    app._preferred_template_column = None
    app._header_row = 1
    app._hrow_from_config = False
    app._template_metadata_for = lambda _path: gui.TemplateMetadata(
        ("cover", "summary"), ("标题",)
    )
    return app


def test_first_start_creates_configuration_next_to_executable(tmp_path, monkeypatch):
    """An exe-only distribution needs no preinstalled config file."""
    config_path = tmp_path / "config.toml"
    monkeypatch.setattr(gui, "CONFIG_PATH", config_path)
    app = _app_for_detection()
    app.hrow_var = _Var(1)

    app._auto_load_config()

    assert config_path.read_bytes() == b""
    config = gui.load_config(config_path)
    assert config.header_row is None
    assert app._header_row == app.hrow_var.get() == 1
    assert not app._hrow_from_config
    assert config.template_column == app.tcol_var.get() == ""
    assert app.status_var.get() == "已从 config.toml 加载配置"


def test_template_column_selection_only_uses_current_excel_headers(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    saved = 'template_column = "填料"\nheader_row = 1\n'
    config_path.write_text(saved, encoding="utf-8")
    monkeypatch.setattr(gui, "CONFIG_PATH", config_path)
    app = _app_for_detection()
    app.tcol_combo = {}
    app.excel_var = _Var(str(build_test_xlsx(tmp_path / "data.xlsx")))
    app.sheet_var = _Var(DATA_SHEET)
    app.hrow_var = _Var(1)
    app._rebuild_treeview = lambda **_opts: None
    app._rebuild_mapping = lambda: None
    app._auto_load_config()

    assert app.tcol_var.get() == ""
    assert app._hrow_from_config
    assert config_path.read_text(encoding="utf-8") == saved

    app.tpl_var.set("")
    app._refresh_all()
    assert app.tcol_combo["values"] == list(DATA_HEADERS)
    assert app.tcol_var.get() == ""

    app.tpl_var.set("template.pptx")
    app._refresh_all()
    assert app.tcol_var.get() == "模板"

    app.sheet_var.set(DETAIL_SHEET)
    app.hrow_var.set(2)
    app._on_header_row_change()
    assert app.tcol_combo["values"] == list(DETAIL_HEADERS)
    assert app.tcol_var.get() == "填料"

    app.tcol_var.set("项目编号")
    app._on_tcol_change()
    app._refresh_all()
    assert app.tcol_var.get() == "项目编号"

    app.sheet_var.set("不存在")
    app._refresh_all()
    assert app.tcol_combo["values"] == []
    assert app.tcol_var.get() == ""


def test_auto_detect_recomputes_when_data_context_changes(monkeypatch):
    calls: list[tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]] = []

    def detect(_metadata, headers, rows):
        calls.append((tuple(headers), tuple(tuple(row) for row in rows)))
        return SimpleNamespace(
            template_column=headers[0],
            mapping={headers[1]: "标题"},
            conflicts=(),
        )

    monkeypatch.setattr(gui, "detect_from_metadata", detect)
    app = _app_for_detection()

    app._auto_detect()
    app._headers = ["类型", "名称"]
    app._rows = [["summary", "结论"]]
    app._auto_detect()

    assert len(calls) == 2
    assert calls[1][0] == ("类型", "名称")
    assert app._auto_mapping == {"名称": "标题"}
    assert app.tcol_var.get() == "类型"


def test_manual_mapping_is_remembered():
    app = gui.App.__new__(gui.App)
    app._explicit_mapping = {}

    app._remember_mapping("标题", "报告标题")
    app._remember_mapping("备注", "(不映射)")

    assert app._explicit_mapping == {"标题": "报告标题", "备注": None}


@pytest.mark.parametrize("preamble_count", [0, 1, 2])
def test_header_detection_for_rows_one_through_three(preamble_count):
    preamble = [[f"说明 {index}", "自动生成"] for index in range(preamble_count)]
    rows = preamble + [
        ["模板", "标题"],
        ["cover", "报告"],
        ["summary", "结论"],
    ]

    assert detect_header_row({"cover", "summary"}, rows) == preamble_count + 1


def test_template_metadata_cache_does_not_cache_excel_detection(tmp_path, monkeypatch):
    template = tmp_path / "template.pptx"
    template.write_bytes(b"template")
    load_calls: list[object] = []
    metadata = gui.TemplateMetadata(("cover",), ("标题",))

    monkeypatch.setattr(gui, "load_template", lambda path: load_calls.append(path) or object())
    monkeypatch.setattr(gui, "analyze_template", lambda _prs: metadata)
    app = gui.App.__new__(gui.App)
    app._template_cache_key = None
    app._template_metadata = None

    assert app._template_metadata_for(str(template)) is metadata
    assert app._template_metadata_for(str(template)) is metadata
    assert len(load_calls) == 1


def test_preview_appends_template_column_after_first_five_columns():
    headers = ["A", "B", "C", "D", "E", "F", "模板"]

    assert gui._preview_columns(headers, "模板") == [
        (0, "A"),
        (1, "B"),
        (2, "C"),
        (3, "D"),
        (4, "E"),
        (6, "模板"),
    ]


def test_preview_does_not_duplicate_visible_template_column():
    headers = ["模板", "A", "B", "C", "D", "E"]

    assert gui._preview_columns(headers, "模板") == [
        (0, "模板"),
        (1, "A"),
        (2, "B"),
        (3, "C"),
        (4, "D"),
    ]


@pytest.mark.parametrize("template_column", ["", "不存在"])
def test_preview_ignores_unavailable_template_column(template_column):
    headers = ["A", "B", "C", "D", "E", "F"]

    assert gui._preview_columns(headers, template_column) == [
        (0, "A"),
        (1, "B"),
        (2, "C"),
        (3, "D"),
        (4, "E"),
    ]
