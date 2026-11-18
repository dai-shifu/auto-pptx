"""Prepare synthetic inputs and verify output from the standalone Windows GUI."""

import argparse
from io import BytesIO
import json
from pathlib import Path
import posixpath
import shutil
import tomllib
from xml.etree import ElementTree
from zipfile import ZipFile

from openpyxl import load_workbook
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from scripts.release import sha256


def prepare(directory: Path, executable: Path) -> None:
    """Copy the exe and create reviewed synthetic inputs in an empty directory."""
    from tests.create_fixtures import build_acceptance_fixture_set

    if not executable.is_file():
        raise ValueError("Executable does not exist")
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("Acceptance directory must be empty")
    directory.mkdir(parents=True, exist_ok=True)
    copied = directory / executable.name
    shutil.copy2(executable, copied)
    build_acceptance_fixture_set(directory)
    (directory / "acceptance.json").write_text(json.dumps({
        "executable": copied.name, "sha256": sha256(copied),
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Run {copied.resolve()} on Windows. Select template.pptx and test_data.xlsx,")
    print("choose Sheet 数据, header row 1 and template column 模板, select all rows,")
    print("then generate. Confirm the acceptance_unmapped warning appears.")
    print("Verify the output with: python -m scripts.check_windows_generation verify "
          f'"{directory}" "<generated output.pptx>"')


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(directory: Path, output: Path) -> None:
    """Check hashes, saved config, generated content and internal relationships."""
    info = json.loads((directory / "acceptance.json").read_text(encoding="utf-8"))
    _require(sha256(directory / info["executable"]) == info["sha256"], "Exe hash changed")
    with (directory / "config.toml").open("rb") as stream:
        config = tomllib.load(stream)
    _require(config.get("header_row") == 1, "Wrong saved header row")
    _require(config.get("template_column") == "模板", "Wrong saved template column")
    expected_mapping = {name: name for name in (
        "标题", "作者", "姓名", "部门", "销售额", "利润", "总结", "日期",
    )}
    _require(config.get("mapping") == expected_mapping, "Saved mappings differ")
    result = Presentation(output)
    _require(len(result.slides) == 3, "Expected only three generated slides")
    texts = "\n".join(
        shape.text for slide in result.slides for shape in slide.shapes if shape.has_text_frame
    )
    for expected in ("年度报告", "张三", "李四", "华东区", "业绩优秀", "2026-01-01",
                     "{{tpl::cover}}", "{{tpl::content}}", "{{tpl::summary}}",
                     "{{acceptance_unmapped}}"):
        _require(expected in texts, f"Missing text: {expected}")
    for placeholder in ("标题", "作者", "姓名", "部门", "总结", "日期"):
        _require("{{" + placeholder + "}}" not in texts, f"Unreplaced: {placeholder}")
    tables = [shape.table for slide in result.slides for shape in slide.shapes if shape.has_table]
    _require(len(tables) == 1, "Expected one generated table")
    _require(tables[0].cell(1, 1).text == "500万", "Wrong sales table value")
    _require(tables[0].cell(2, 1).text == "120万", "Wrong profit table value")
    images = [shape.image.blob for slide in result.slides for shape in slide.shapes
              if shape.shape_type == MSO_SHAPE_TYPE.PICTURE]
    _require(images == [(directory / "synthetic.png").read_bytes()], "Image data differs")
    charts = [shape.chart for slide in result.slides for shape in slide.shapes if shape.has_chart]
    _require(len(charts) == 1, "Expected one native chart")
    _require(tuple(charts[0].series[0].values) == (12, 34), "Chart values differ")
    with ZipFile(output) as archive:
        _require(archive.testzip() is None, "Corrupt PPTX ZIP member")
        names = set(archive.namelist())
        embedded = [name for name in names if name.startswith("ppt/embeddings/")]
        _require(len(embedded) == 1, "Expected one embedded chart workbook")
        chart_name = str(charts[0].part.partname).lstrip("/")
        chart_xml = ElementTree.fromstring(archive.read(chart_name))
        external_data = chart_xml.find("{http://schemas.openxmlformats.org/drawingml/2006/chart}externalData")
        _require(external_data is not None, "Missing embedded chart data link")
        relationship_id = external_data.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        )
        chart_rels = posixpath.join(
            posixpath.dirname(chart_name), "_rels", posixpath.basename(chart_name) + ".rels",
        )
        _require(chart_rels in names, "Missing chart relationships")
        relationships = ElementTree.fromstring(archive.read(chart_rels))
        workbook_rel = next((rel for rel in relationships if rel.get("Id") == relationship_id), None)
        _require(workbook_rel is not None, "Broken embedded chart data link")
        _require(workbook_rel.get("TargetMode") != "External"
                 and workbook_rel.get("Type", "").endswith("/package"),
                 "Chart data must link to an embedded workbook")
        workbook_name = posixpath.normpath(posixpath.join(
            posixpath.dirname(chart_name), workbook_rel.get("Target", ""),
        )).lstrip("/")
        _require(workbook_name == embedded[0], "Chart links to a different workbook")
        workbook = load_workbook(BytesIO(archive.read(workbook_name)), data_only=True)
        try:
            rows = list(workbook.active.values)
            _require(rows[1:] == [("A", 12), ("B", 34)], "Embedded workbook data differs")
        finally:
            workbook.close()
        for name in names:
            if not name.endswith(".rels"):
                continue
            base = posixpath.dirname(posixpath.dirname(name))
            for rel in ElementTree.fromstring(archive.read(name)):
                if rel.get("TargetMode") == "External":
                    continue
                target = rel.get("Target", "")
                resolved = posixpath.normpath(posixpath.join(base, target)).lstrip("/")
                _require(resolved in names, f"Broken relationship: {name}: {target}")
    print(f"Content verified: {output}; exe SHA-256: {info['sha256']}")
    print("Record the Windows environment, first-run startup and visible warning separately.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    inputs = subcommands.add_parser("prepare")
    inputs.add_argument("directory", type=Path)
    inputs.add_argument("executable", type=Path)
    outputs = subcommands.add_parser("verify")
    outputs.add_argument("directory", type=Path)
    outputs.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.directory, args.executable)
    else:
        verify(args.directory, args.output)
