from pptx import Presentation
from pptx.util import Inches

from src.auto_detect import (
    _levenshtein,
    collect_placeholders,
    detect_and_suggest,
    detect_header_row,
    detect_template_column,
    suggest_mapping,
    suggest_mapping_detailed,
    tokenize_template_value,
)


class TestLevenshtein:
    def test_same(self):
        assert _levenshtein("abc", "abc") == 0

    def test_one_substitution(self):
        assert _levenshtein("abc", "abd") == 1

    def test_one_insertion(self):
        assert _levenshtein("ab", "abc") == 1

    def test_one_deletion(self):
        assert _levenshtein("abc", "ab") == 1

    def test_chinese(self):
        assert _levenshtein("销售额", "销售额") == 0
        assert _levenshtein("销信额", "销售额") == 1

    def test_case_insensitive(self):
        assert _levenshtein("Name", "name") == 1


class TestDetectTemplateColumn:
    def test_exact_match(self):
        headers = ["模板", "姓名"]
        rows = [["cover", "张三"], ["content", "李四"]]
        tpl_names = {"cover", "content", "summary"}
        assert detect_template_column(headers, rows, tpl_names) == "模板"

    def test_no_match(self):
        headers = ["备注", "姓名"]
        rows = [["abc", "张三"], ["def", "李四"]]
        tpl_names = {"cover", "content"}
        assert detect_template_column(headers, rows, tpl_names) is None

    def test_partial_match_picks_best(self):
        headers = ["类型", "分类"]
        rows = [["cover", "x"], ["content", "y"], ["unknown", "z"]]
        tpl_names = {"cover", "content"}
        result = detect_template_column(headers, rows, tpl_names)
        assert result == "类型"  # 2/3 match vs 0/3

    def test_slash_separated_template_names(self):
        headers = ["模板", "备注"]
        rows = [[" Ni-NTA / GST / ", "ordinary"]]

        assert tokenize_template_value(rows[0][0]) == ["Ni-NTA", "GST"]
        assert detect_template_column(headers, rows, {"Ni-NTA", "GST"}) == "模板"


class TestSuggestMapping:
    def test_exact_match(self):
        mapping = suggest_mapping(
            ["姓名", "部门", "销售额"],
            ["name", "dept", "sales"]
        )
        assert mapping["name"] is None
        assert mapping["dept"] is None
        assert mapping["sales"] is None

    def test_case_insensitive_match(self):
        mapping = suggest_mapping(
            ["Name", "Dept"],
            ["name", "dept"]
        )
        assert mapping["name"] == "Name"
        assert mapping["dept"] == "Dept"

    def test_edit_distance_match(self):
        mapping = suggest_mapping(
            ["销信额"],
            ["销售额"]
        )
        assert mapping["销售额"] == "销信额"

    def test_no_match(self):
        mapping = suggest_mapping(
            ["姓名"],
            ["xyz"]
        )
        assert mapping["xyz"] is None

    def test_exact_matches_are_reserved_before_fuzzy_matches(self):
        mapping = suggest_mapping(["Name", "Nme"], ["Nane", "name"])

        assert mapping == {"Nane": "Nme", "name": "Name"}

    def test_equal_fuzzy_candidates_are_unresolved_with_diagnostics(self):
        result = suggest_mapping_detailed(["Namf", "Namh"], ["Name"])

        assert result.mapping == {"Name": None}
        assert result.conflicts[0].reason == "equal_fuzzy_candidates"
        assert result.conflicts[0].candidates == ("Namf", "Namh")

    def test_competing_placeholders_are_not_silently_overwritten(self):
        result = suggest_mapping_detailed(["abd"], ["abc", "abe"])

        assert result.mapping == {"abc": None, "abe": None}
        assert [conflict.placeholder for conflict in result.conflicts] == ["abc", "abe"]
        assert all(
            conflict.reason == "competing_placeholders"
            for conflict in result.conflicts
        )

    def test_repeated_detection_is_stable_and_one_to_one(self):
        expected = suggest_mapping_detailed(
            ["Name", "departmnt", "sale"], ["name", "department", "sales"]
        )

        for _ in range(10):
            actual = suggest_mapping_detailed(
                ["Name", "departmnt", "sale"], ["name", "department", "sales"]
            )
            assert actual == expected
        assigned = [column for column in expected.mapping.values() if column]
        assert len(assigned) == len(set(assigned))


class TestCollectPlaceholders:
    def test_preserves_first_seen_order_across_text_and_tables(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        text = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
        text.text = "{{second}} then {{first}} and {{second}}"
        table = slide.shapes.add_table(1, 2, Inches(1), Inches(2), Inches(4), Inches(1)).table
        table.cell(0, 0).text = "{{third}}"
        table.cell(0, 1).text = "{{first}} / {{fourth}}"

        assert collect_placeholders(prs) == ["second", "first", "third", "fourth"]


class TestDetectHeaderRow:
    def test_selects_header_after_explanatory_preamble(self):
        rows = [
            ["Report export", "Generated automatically"],
            ["模板", "姓名"],
            ["cover", "Alice"],
            ["content", "Bob"],
        ]

        assert detect_header_row({"cover", "content"}, rows) == 2

    def test_slash_separated_downstream_values_are_evidence(self):
        rows = [
            ["说明", "其他"],
            ["模板", "姓名"],
            ["Ni-NTA / GST", "Alice"],
        ]

        assert detect_header_row({"Ni-NTA", "GST"}, rows) == 2

    def test_no_downstream_template_evidence_falls_back_to_row_one(self):
        rows = [
            ["说明一", "说明二"],
            ["模板", "姓名"],
            ["unknown", "Alice"],
        ]

        assert detect_header_row({"cover"}, rows) == 1


class TestDetectAndSuggest:
    """验证 detect_and_suggest 返回 {excel_col: placeholder} 方向。"""

    def test_mapping_direction(self):
        """映射方向应为 excel_col → placeholder。"""
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        text = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(6), Inches(2))
        text.text = (
            "{{tpl::cover}} {{标题}} {{作者}} {{姓名}} {{部门}} "
            "{{销售额}} {{利润}} {{总结}} {{日期}}"
        )
        headers = ["模板", "标题", "作者", "姓名", "部门", "销售额", "利润", "总结", "日期"]
        rows = [
            ["cover", "年度报告", "张三", "", "", "", "", "", ""],
        ]

        tpl_col, mapping = detect_and_suggest(prs, headers, rows)
        assert tpl_col == "模板"
        # mapping key 是 excel_col，value 是 placeholder
        assert mapping["标题"] == "标题"
        assert mapping["作者"] == "作者"
        assert mapping["姓名"] == "姓名"
        assert mapping["部门"] == "部门"
        assert mapping["销售额"] == "销售额"
        assert mapping["利润"] == "利润"
        assert mapping["总结"] == "总结"
        assert mapping["日期"] == "日期"
