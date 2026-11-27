"""Compare read-only compatibility checks with the generation pipeline."""

from pathlib import Path

import pytest
from openpyxl import load_workbook
from pptx import Presentation
from pptx.util import Inches

from src.generator import generate
from src.input_check import CheckSettings, check_inputs, format_check_report
from tests.create_fixtures import DATA_SHEET


EXAMPLE = Path(__file__).resolve().parents[1] / "examples/bio-daily"


@pytest.fixture
def inputs(generated_fixtures):
    return generated_fixtures / "template.pptx", generated_fixtures / "test_data.xlsx"


def _generate(template, excel, settings, output):
    return generate(
        Presentation(str(template)), excel, settings.sheet_name, list(settings.selected_rows),
        output, template_column=settings.template_column, mapping=settings.mapping,
        header_row=settings.header_row,
    )


def _slide_text(path):
    return [
        [shape.text for shape in slide.shapes if shape.has_text_frame]
        for slide in Presentation(str(path)).slides
    ]


def test_public_example_row_two_predicts_and_generates_one_page(tmp_path):
    template, excel = EXAMPLE / "template.pptx", EXAMPLE / "data.xlsx"
    structure = check_inputs(template, excel, CheckSettings("日报数据", 1, "模板", {}, ()))
    assert structure.suggestions is not None
    settings = CheckSettings("日报数据", 1, "模板", structure.suggestions.mapping, (2,))

    report = check_inputs(template, excel, settings)

    assert report.problems == []
    assert report.expected_pages == 1
    row, = report.rows
    match, = row.matches
    assert (row.number, match.page.number, match.page.name) == (2, 1, "日报总览")
    assert not (row.unmatched or match.unmapped or match.empty)
    assert "预计 1 页" in format_check_report(report)

    result = _generate(template, excel, settings, tmp_path / "daily.pptx")
    assert result.generated_pages == report.expected_pages
    assert result.warnings == []
    actual, = _slide_text(result.output_path)
    assert "{{tpl::日报总览}}" in actual


def test_partial_match_after_blank_row_uses_first_duplicate_and_per_page_sources(inputs, tmp_path):
    template, excel = inputs
    missing_name = "PRIVATE-MISSING-TEMPLATE"
    body = "PRIVATE-CELL-CONTENT"
    workbook = load_workbook(excel)
    sheet = workbook.create_sheet("兼容性")
    sheet.append(("说明：标题在下一行",))
    sheet.append(("模板", "标题", "作者", "总结", "日期"))
    sheet.append((None,))
    sheet.append((f" summary / {missing_name} / cover ", body, None, "人工核对", "2026-01-01"))
    workbook.save(excel)
    workbook.close()

    prs = Presentation(str(template))
    duplicate = prs.slides.add_slide(prs.slide_layouts[6])
    duplicate.shapes.add_textbox(0, 0, Inches(4), Inches(1)).text = "{{tpl::cover}} {{重复页独有}}"
    prs.save(template)
    settings = CheckSettings(
        "兼容性", 2, "模板", {"作者": "作者", "总结": "总结", "日期": "日期"},
        (3, 4), explicitly_unmapped=("标题",),
    )
    before = {path: path.read_bytes() for path in inputs}
    output = tmp_path / "report.pptx"

    report = check_inputs(template, excel, settings)
    local = format_check_report(report)
    shared = format_check_report(report, for_sharing=True)

    assert all(path.read_bytes() == contents for path, contents in before.items())
    assert not output.exists()
    assert report.problems == []
    assert report.expected_pages == 2
    assert [(page.number, page.usable) for page in report.pages if page.name == "cover"] == [
        (1, True), (4, False),
    ]
    blank, partial = report.rows
    assert blank.number == 3 and blank.skipped_reason and not blank.matches
    assert partial.number == 4 and partial.skipped_reason is None
    assert partial.unmatched == (missing_name,)
    assert [(hit.page.number, hit.page.name) for hit in partial.matches] == [(3, "summary"), (1, "cover")]
    assert [(hit.unmapped, hit.empty) for hit in partial.matches] == [((), ()), (("标题",), ("作者",))]
    assert report.suggestions is not None
    assert report.suggestions.mapping["标题"] == "标题"
    assert "标题" not in settings.mapping
    assert "明确不映射：标题" in local
    assert "Excel 第 4 行：部分匹配：summary（模板第 3 页） → cover（模板第 1 页）" in local
    assert "模板第 1 页未映射（保留占位符）：标题" in local
    assert "模板第 1 页来源为空（填空文本）：作者" in local
    assert missing_name in local
    assert "找不到模板：1 项" in shared
    for value in (missing_name, body, "人工核对", str(template), str(excel), template.name, excel.name):
        assert value not in shared

    result = _generate(template, excel, settings, output)
    assert result.generated_pages == report.expected_pages
    assert result.skipped_rows == [blank.number]
    assert result.unmatched_templates == list(partial.unmatched)
    assert result.unresolved_placeholders == ["标题"]
    summary, cover = _slide_text(output)
    assert "{{tpl::summary}}" in summary and "总结: 人工核对" in summary
    assert "{{tpl::cover}}" in cover and "{{标题}}" in cover and "作者: " in cover
    assert all("重复页独有" not in text for text in cover)


def test_tied_candidates_do_not_override_current_template_column(inputs, tmp_path):
    template, excel = inputs
    workbook = load_workbook(excel)
    sheet = workbook[DATA_SHEET]
    candidate_column = sheet.max_column + 1
    for index, value in enumerate(("备选模板", "summary", "cover", "content"), start=1):
        sheet.cell(index, candidate_column, value)
    workbook.save(excel)
    workbook.close()
    settings = CheckSettings(DATA_SHEET, 1, "备选模板", {}, (2,))

    report = check_inputs(template, excel, settings)

    assert report.problems == []
    suggestions = report.suggestions
    assert suggestions is not None
    assert suggestions.template_column == "模板"
    assert [(item.header, item.matches, item.token_count) for item in suggestions.template_candidates] == [
        ("模板", 3, 3), ("备选模板", 3, 3),
    ]
    assert [match.page.name for match in report.rows[0].matches] == ["summary"]
    text = format_check_report(report)
    assert "模板列：备选模板；已勾选 1 行" in text
    assert "候选模板列：模板（3/3 个不同名称匹配）；备选模板（3/3 个不同名称匹配）" in text
    assert "需要确认：有同分模板列" in text

    result = _generate(template, excel, settings, tmp_path / "tied.pptx")
    actual, = _slide_text(result.output_path)
    assert "{{tpl::summary}}" in actual


@pytest.mark.parametrize(
    ("duplicate_headers", "mapping", "message", "detail"),
    [
        (True, {}, "重复列名", "第 1 行"),
        (False, {"标题": "标题", "作者": "标题"}, "同一占位符", "标题: 标题, 作者"),
    ],
    ids=("duplicate-headers", "repeated-mapping-target"),
)
def test_validation_blocks_check_and_generation(
    inputs, tmp_path, duplicate_headers, mapping, message, detail,
):
    template, excel = inputs
    if duplicate_headers:
        workbook = load_workbook(excel)
        workbook[DATA_SHEET]["C1"] = " 标题 "
        workbook.save(excel)
        workbook.close()
    settings = CheckSettings(DATA_SHEET, 1, "模板", mapping, (2,))

    report = check_inputs(template, excel, settings)

    assert report.rows == []
    assert report.expected_pages is None
    assert any(message in problem and detail in problem for problem in report.problems)
    text = format_check_report(report)
    assert "需要先处理" in text and message in text
    assert "已勾选数据：预计" not in text
    output = tmp_path / "blocked.pptx"
    with pytest.raises(ValueError, match=message):
        _generate(template, excel, settings, output)
    assert not output.exists()


def test_no_selected_rows_checks_structure_without_predicting_pages(inputs):
    settings = CheckSettings(DATA_SHEET, 1, "模板", {"标题": "标题"}, ())

    report = check_inputs(*inputs, settings)

    assert report.problems == []
    assert report.expected_pages is None
    assert report.rows == []
    assert "模板" in report.headers
    assert [page.name for page in report.pages] == ["cover", "content", "summary"]
    text = format_check_report(report)
    assert "标题 → {{标题}}" in text
    assert "未勾选数据行。请先勾一行" in text
    assert "已勾选数据：预计" not in text


@pytest.mark.parametrize(
    ("missing_index", "suffix", "message"),
    [(0, ".pptx", "无法读取模板 PPT"), (1, ".xlsx", "无法读取 Excel")],
    ids=("template", "workbook"),
)
def test_read_failure_drops_previous_rows_and_omits_raw_details_when_shared(
    inputs, tmp_path, missing_index, suffix, message,
):
    template, excel = inputs
    settings = CheckSettings(DATA_SHEET, 1, "模板", {}, (2,))
    assert check_inputs(template, excel, settings).expected_pages == 1
    missing = tmp_path / f"PRIVATE-INPUT{suffix}"
    changed = (missing, excel) if missing_index == 0 else (template, missing)

    report = check_inputs(*changed, settings)

    assert report.expected_pages is None
    assert report.rows == []
    assert report.headers == []
    assert report.suggestions is None
    assert any(message in problem for problem in report.problems)
    local = format_check_report(report)
    shared = format_check_report(report, for_sharing=True)
    assert report.read_detail and report.read_detail in local
    assert missing.name in local
    assert message in shared
    assert missing.name not in shared and report.read_detail not in shared
    assert "Excel 第 2 行：" not in local
