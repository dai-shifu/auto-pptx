"""The external acceptance checker must detect incomplete generated artifacts."""

import pytest
from pptx import Presentation
from xml.etree import ElementTree
from zipfile import ZipFile

from scripts.check_windows_generation import prepare, verify
from src.config import Config, save_config
from src.generator import generate


@pytest.fixture
def acceptance(tmp_path):
    exe = tmp_path / "synthetic.exe"
    exe.write_bytes(b"MZ synthetic checker fixture; not a runnable exe")
    directory = tmp_path / "acceptance"
    prepare(directory, exe)
    output = directory / "output.pptx"
    result = generate(
        Presentation(directory / "template.pptx"), directory / "test_data.xlsx",
        "数据", [2, 3, 4], output, template_column="模板",
    )
    assert any("acceptance_unmapped" in warning for warning in result.warnings)
    mapping = {name: name for name in ("标题", "作者", "姓名", "部门", "销售额", "利润", "总结", "日期")}
    save_config(Config(template_column="模板", header_row=1, mapping=mapping), directory / "config.toml")
    return directory, output


def test_checker_accepts_complete_content(acceptance):
    verify(*acceptance)


@pytest.mark.parametrize("corruption", [
    "exe", "config", "mapping", "table", "slide", "chart", "workbook_relationship",
])
def test_checker_rejects_incomplete_acceptance(acceptance, corruption):
    directory, output = acceptance
    if corruption == "exe":
        (directory / "synthetic.exe").write_bytes(b"changed")
    elif corruption == "config":
        (directory / "config.toml").write_text('header_row = 2\n')
    elif corruption == "mapping":
        save_config(Config(template_column="模板", mapping={"标题": "标题"}), directory / "config.toml")
    elif corruption == "workbook_relationship":
        with ZipFile(output) as archive:
            members = {name: archive.read(name) for name in archive.namelist()}
        name = "ppt/charts/_rels/chart1.xml.rels"
        relationships = ElementTree.fromstring(members[name])
        for rel in list(relationships):
            if rel.get("Type", "").endswith("/package"):
                relationships.remove(rel)
        members[name] = ElementTree.tostring(relationships)
        with ZipFile(output, "w") as archive:
            for name, contents in members.items():
                archive.writestr(name, contents)
    else:
        prs = Presentation(output)
        if corruption == "slide":
            prs.slides.add_slide(prs.slide_layouts[6])
        elif corruption == "table":
            table = next(s.table for s in prs.slides[1].shapes if s.has_table)
            table.cell(1, 1).text = "wrong"
        else:
            shape = next(s for s in prs.slides[2].shapes if s.has_chart)
            shape._element.getparent().remove(shape._element)
        prs.save(output)
    with pytest.raises(ValueError):
        verify(directory, output)
