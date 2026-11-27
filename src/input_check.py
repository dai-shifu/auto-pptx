"""Read-only compatibility checks for the selections used by the GUI."""

from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from .auto_detect import (
    DetectionResult,
    TemplateMetadata,
    collect_slide_placeholders,
    detect_from_metadata,
    tokenize_template_value,
)
from .excel_reader import cell_text, generation_headers
from .generator import validate_headers, validate_mapping
from .pptx_engine import load_template
from .template_matching import iter_template_pages


@dataclass(frozen=True)
class CheckSettings:
    sheet_name: str
    header_row: int
    template_column: str | None
    mapping: dict[str, str]
    selected_rows: tuple[int, ...]
    explicitly_unmapped: tuple[str, ...] = ()


@dataclass(frozen=True)
class PageCheck:
    number: int
    name: str | None
    placeholders: tuple[str, ...]
    usable: bool


@dataclass(frozen=True)
class PageMatch:
    page: PageCheck
    unmapped: tuple[str, ...]
    empty: tuple[str, ...]


@dataclass(frozen=True)
class RowCheck:
    number: int
    matches: tuple[PageMatch, ...] = ()
    unmatched: tuple[str, ...] = ()
    skipped_reason: str | None = None


@dataclass
class CheckReport:
    settings: CheckSettings
    headers: list[str] = field(default_factory=list)
    pages: tuple[PageCheck, ...] = ()
    suggestions: DetectionResult | None = None
    rows: list[RowCheck] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    read_detail: str | None = None

    @property
    def expected_pages(self) -> int | None:
        if self.problems or not self.settings.template_column or not self.rows:
            return None
        return sum(len(row.matches) for row in self.rows)


def check_inputs(
    template_path: str | Path, excel_path: str | Path, settings: CheckSettings,
) -> CheckReport:
    """Read the supplied files, without generating pages or changing any settings."""
    report = CheckReport(settings)
    if not template_path or not excel_path or not settings.sheet_name:
        report.problems.append("请先选择模板 PPT、Excel 文件和工作表，再检查。")
        return report

    try:
        prs = load_template(template_path)
        report.pages = tuple(
            PageCheck(page.number, page.name, tuple(collect_slide_placeholders(page.slide)), page.usable)
            for page in iter_template_pages(prs)
        )
    except Exception as exc:
        report.problems.append("无法读取模板 PPT。请重新选择有效的 .pptx 文件。")
        report.read_detail = str(exc)
        return report
    if not any(page.usable for page in report.pages):
        report.problems.append("没有可匹配的模板页。请在普通文本框中添加 {{tpl::名称}}。")

    try:
        workbook = load_workbook(excel_path, data_only=True)
    except Exception as exc:
        report.problems.append("无法读取 Excel。请重新选择有效的 .xlsx 文件。")
        report.read_detail = str(exc)
        return report
    try:
        if settings.sheet_name not in workbook.sheetnames:
            report.problems.append("当前工作表不存在。请重新选择工作表。")
        else:
            sheet = workbook[settings.sheet_name]
            if isinstance(sheet, Worksheet):
                _check_sheet(sheet, report)
            else:
                report.problems.append("当前工作表没有可检查的单元格。请改选数据工作表。")
    finally:
        workbook.close()
    return report


def _check_sheet(sheet: Worksheet, report: CheckReport) -> None:
    settings = report.settings
    if not 1 <= settings.header_row <= sheet.max_row:
        report.problems.append("标题行不在工作表范围内。请重新设置标题行。")
        return
    report.headers = generation_headers(sheet, settings.header_row)
    try:
        validate_headers(report.headers)
    except ValueError as exc:
        report.problems.append(f"第 {settings.header_row} 行：{exc}。请修正 Excel 标题。")
        return
    if not any(report.headers):
        report.problems.append("标题行没有非空列名。请检查 Excel 标题或重选标题行。")
        return

    pages_by_name = {
        page.name: page for page in report.pages if page.usable and page.name is not None
    }
    metadata = TemplateMetadata(
        tuple(pages_by_name),
        tuple(dict.fromkeys(name for page in report.pages for name in page.placeholders)),
    )
    rows = [
        [cell_text(value) for value in row]
        for row in sheet.iter_rows(min_row=settings.header_row + 1, values_only=True)
    ]
    report.suggestions = detect_from_metadata(metadata, report.headers, rows)
    try:
        validate_mapping(report.headers, settings.mapping)
    except ValueError as exc:
        report.problems.append(f"{exc}。请检查 GUI 的列映射。")
    if settings.template_column and settings.template_column not in report.headers:
        report.problems.append("当前模板列不在标题行中。请重新选择模板列。")
    if report.problems or not settings.template_column or not settings.selected_rows:
        return

    template_index = report.headers.index(settings.template_column)
    source_columns = {
        placeholder: report.headers.index(column) for column, placeholder in settings.mapping.items()
    }
    for row_number in settings.selected_rows:
        row_index = row_number - settings.header_row - 1
        if not 0 <= row_index < len(rows):
            report.rows.append(RowCheck(row_number, skipped_reason="不是当前工作表中的数据行"))
            continue
        row = rows[row_index]
        template_names = tokenize_template_value(row[template_index])
        if not template_names:
            report.rows.append(RowCheck(row_number, skipped_reason="模板列没有可匹配的名称"))
            continue
        matches: list[PageMatch] = []
        unmatched: list[str] = []
        for name in template_names:
            page = pages_by_name.get(name)
            if page is None:
                unmatched.append(name)
                continue
            matches.append(PageMatch(
                page,
                tuple(p for p in page.placeholders if p not in source_columns),
                tuple(p for p in page.placeholders if p in source_columns and row[source_columns[p]] == ""),
            ))
        report.rows.append(RowCheck(row_number, tuple(matches), tuple(unmatched)))


def format_check_report(report: CheckReport, *, for_sharing: bool = False) -> str:
    """Format a local report or a shareable view with no raw cell or file details."""
    settings = report.settings
    lines = ["生成检查（只读）", "这是本次检查的快照；文件或设置变化后请重新检查。"]
    if report.problems:
        lines.append("\n需要先处理")
        lines.extend(f"- {problem}" for problem in report.problems)
        if report.read_detail and not for_sharing:
            lines.append(f"本机读取详情：{report.read_detail}")
    expected_pages = report.expected_pages
    if expected_pages is not None:
        lines.append(f"\n已勾选数据：预计 {expected_pages} 页（不是已生成的页数）")
        for row in report.rows:
            lines.extend(_format_row(row, for_sharing=for_sharing))
        if expected_pages == 0:
            lines.append("所选行没有匹配页。请核对模板列的值与 PPT 模板标识，或重新勾选数据。")
    if not report.problems and not settings.template_column:
        lines.append("\n请先确认模板列，再检查预计选页结果。")
    if report.headers and not settings.selected_rows:
        lines.append("\n未勾选数据行。请先勾一行，再查看选页结果。")

    lines.extend([
        "\n当前设置",
        f"工作表：{settings.sheet_name or '未选择'}；标题行：第 {settings.header_row} 行",
        f"模板列：{settings.template_column or '未选择'}；已勾选 {len(settings.selected_rows)} 行",
    ])
    if report.headers:
        lines.append("Excel 列名：" + "、".join(header for header in report.headers if header))
        lines.append("当前映射（Excel 列 → PPT 占位符）：" + _format_mapping(settings.mapping))
        if settings.explicitly_unmapped:
            lines.append("明确不映射：" + "、".join(settings.explicitly_unmapped))

    if report.pages:
        lines.append("\nPPT 模板页")
        for page in report.pages:
            status = "" if page.usable else "（重复标识，使用首个同名页）" if page.name else "（不会选用）"
            placeholders = "、".join(page.placeholders) or "无"
            lines.append(f"- 第 {page.number} 页：{page.name or '无模板标识'}{status}；占位符：{placeholders}")
    if report.suggestions is not None:
        suggestions = report.suggestions
        lines.append("\n自动建议（未修改当前设置）")
        candidates = "；".join(
            f"{candidate.header or '无标题列'}（{candidate.matches}/{candidate.token_count} 个不同名称匹配）"
            for candidate in suggestions.template_candidates
        )
        lines.append("候选模板列：" + (candidates or "未找到，请核对模板名及模板列。"))
        if len(suggestions.template_candidates) > 1:
            lines.append("需要确认：有同分模板列，请核对哪一列用于选页。")
        lines.append("建议映射：" + _format_mapping(suggestions.mapping))
        for conflict in suggestions.conflicts:
            lines.append(f"需要确认：{conflict.placeholder} 的候选来源是 {'、'.join(conflict.candidates)}。")
        lines.append("检测只比较名称，不能确认两个字段的业务含义是否相同。")

    lines.append("\n检查不生成 PPT，也不验证版式、文字溢出或保存是否成功。")
    return "\n".join(lines)


def _format_mapping(mapping: dict[str, str]) -> str:
    return "；".join(f"{column} → {{{{{placeholder}}}}}" for column, placeholder in mapping.items()) or "无"


def _format_row(row: RowCheck, *, for_sharing: bool) -> list[str]:
    prefix = f"- Excel 第 {row.number} 行："
    if row.skipped_reason:
        return [prefix + f"跳过（{row.skipped_reason}）。请核对行和模板列。"]
    pages = " → ".join(f"{match.page.name}（模板第 {match.page.number} 页）" for match in row.matches)
    status = "部分匹配：" if row.unmatched and row.matches else ""
    lines = [prefix + status + (pages or "跳过（无匹配页）")]
    if row.unmatched:
        detail = f"{len(row.unmatched)} 项" if for_sharing else "、".join(row.unmatched)
        lines.append(f"  找不到模板：{detail}。请核对该行模板列和 PPT 标识。")
    for match in row.matches:
        if match.unmapped:
            lines.append(f"  模板第 {match.page.number} 页未映射（保留占位符）：{'、'.join(match.unmapped)}。请检查映射。")
        if match.empty:
            lines.append(f"  模板第 {match.page.number} 页来源为空（填空文本）：{'、'.join(match.empty)}。如需内容，请检查该行。")
    return lines
