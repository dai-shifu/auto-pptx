from pathlib import Path

import pytest
from pptx import Presentation

from src.generator import generate
from src.pptx_engine import load_template

def test_end_to_end(tmp_path, generated_fixtures: Path):
    """端到端测试：单 Excel 管线。"""
    prs = load_template(generated_fixtures / "template.pptx")
    output = tmp_path / "output.pptx"

    generate(
        prs=prs,
        excel_path=generated_fixtures / "test_data.xlsx",
        sheet_name="数据",
        selected_rows=[2, 3, 4],
        output_path=output,
    )

    result = Presentation(str(output))
    assert len(result.slides) >= 2


def test_end_to_end_empty(tmp_path, generated_fixtures: Path):
    """空选择应失败，且不留下输出文件。"""
    prs = load_template(generated_fixtures / "template.pptx")
    output = tmp_path / "output.pptx"

    with pytest.raises(ValueError):
        generate(
            prs=prs,
            excel_path=generated_fixtures / "test_data.xlsx",
            sheet_name="数据",
            selected_rows=[],
            output_path=output,
        )
    assert not output.exists()


def test_invalid_sheet(tmp_path, generated_fixtures: Path):
    """无效 Sheet 名应抛出 ValueError。"""
    prs = load_template(generated_fixtures / "template.pptx")

    with pytest.raises(ValueError, match="Sheet"):
        generate(
            prs=prs,
            excel_path=generated_fixtures / "test_data.xlsx",
            sheet_name="不存在的Sheet",
            selected_rows=[2],
            output_path=tmp_path / "unused.pptx",
        )
