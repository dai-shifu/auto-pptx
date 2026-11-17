from types import SimpleNamespace

import pytest

from src import gui
from src.auto_detect import detect_header_row


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
    app._tcol_from_config = False
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

    assert config_path.is_file()
    config = gui.load_config(config_path)
    assert config.header_row == 1
    assert config.template_column == app.tcol_var.get()
    assert app.status_var.get() == "已从 config.toml 加载配置"


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
