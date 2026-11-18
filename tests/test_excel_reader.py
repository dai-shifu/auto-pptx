from pathlib import Path

import pytest

from src.excel_reader import read_excel


def test_read_excel_success(generated_fixtures: Path):
    mapping = {"标题": "title", "作者": "author", "姓名": "name", "部门": "dept",
               "销售额": "sales", "利润": "profit", "总结": "summary", "日期": "date"}
    rows = read_excel(generated_fixtures / "test_data.xlsx", mapping, template_column="模板")
    assert len(rows) == 3
    assert rows[0]["title"] == "年度报告"
    assert rows[0]["模板"] == "cover"
    assert rows[0]["name"] == ""
    assert rows[1]["name"] == "李四"
    assert rows[2]["summary"] == "业绩优秀"


def test_read_excel_file_not_found():
    with pytest.raises(FileNotFoundError, match="Excel 文件不存在"):
        read_excel("nonexistent.xlsx", {"a": "b"})
