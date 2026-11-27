from collections.abc import Callable
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet


def generation_headers(ws: Worksheet, header_row: int) -> list[str]:
    """Read headers using the generator's normalization rules."""
    return [str(cell.value).strip() if cell.value else "" for cell in ws[header_row]]


def cell_text(value: object) -> str:
    return str(value) if value is not None else ""


def read_sheet_rows(
    excel_path: str | Path,
    sheet_name: str,
    header_row: int | Callable[[list[list[str]]], int] = 1,
) -> tuple[list[str], list[list[str]]]:
    """读取指定 Sheet，返回 (headers, rows)。

    标题行从 1 开始，也可由回调根据前五行确定。所有值转换为字符串。
    """
    path = Path(excel_path)
    if not path.exists():
        raise FileNotFoundError(f"Excel 文件不存在: {path}")

    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        if sheet_name not in wb.sheetnames:
            raise ValueError(f"Sheet '{sheet_name}' 不存在，可用 Sheet: {wb.sheetnames}")
        raw_rows = list(wb[sheet_name].iter_rows(values_only=True))
    finally:
        wb.close()

    if not raw_rows:
        return [], []

    if callable(header_row):
        candidates = [[cell_text(value) for value in row] for row in raw_rows[:5]]
        header_row = header_row(candidates)
    if not 1 <= header_row <= len(raw_rows):
        return [], []

    headers = [cell_text(value).strip() for value in raw_rows[header_row - 1]]
    rows = [[cell_text(value) for value in row] for row in raw_rows[header_row:]]
    return headers, rows
