import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet


def generation_headers(ws: Worksheet, header_row: int) -> list[str]:
    """Read headers using the generator's normalization rules."""
    return [str(cell.value).strip() if cell.value else "" for cell in ws[header_row]]


def cell_text(value: object) -> str:
    return str(value) if value is not None else ""


def read_excel(path: str | Path, mapping: dict[str, str], template_column: str = "") -> list[dict[str, str]]:
    """读取 Excel 文件，返回结构化行数据。

    Args:
        path: Excel 文件路径
        mapping: Excel 列名 → 占位符名 的映射
        template_column: 模板标记列名（原始列名，不参与映射转换）

    Returns:
        每行数据的列表，每个元素是 {占位符名: 值} 的字典
        如果指定了 template_column，该列以原始列名保留在每行中

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件为空或列名不匹配
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Excel 文件不存在: {path}")

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not rows:
        raise ValueError(f"Excel 文件为空: {path}")

    # 第一行为列名
    headers = [str(h).strip() if h is not None else "" for h in rows[0]]

    # 检查映射中的列名是否都存在
    missing = [col for col in mapping if col not in headers]
    if missing:
        raise ValueError(f"Excel 中缺少以下列: {missing}")

    # 后续每行转换为字典，按 mapping 转换键名
    result = []
    for row in rows[1:]:
        raw = {}
        for header, value in zip(headers, row):
            if header:  # 跳过空列名
                raw[header] = str(value) if value is not None else ""

        # 按 mapping 转换为占位符名
        record = {}
        for excel_col, placeholder in mapping.items():
            if excel_col in raw:
                record[placeholder] = raw[excel_col]

        # 保留模板标记列（原始列名，不映射）
        if template_column and template_column in raw:
            record[template_column] = raw[template_column]

        result.append(record)

    if not result:
        raise ValueError(f"Excel 文件没有数据行: {path}")

    return result


def read_sheet_rows(
    excel_path: str | Path,
    sheet_name: str,
    header_row: int = 1,
) -> tuple[list[str], list[list[str]]]:
    """读取指定 Sheet，返回 (headers, rows)。

    headers 从 header_row 行读取，rows 为 header_row+1 行起的所有数据行。
    所有值转换为字符串。
    """
    path = Path(excel_path)
    if not path.exists():
        raise FileNotFoundError(f"Excel 文件不存在: {path}")

    wb = load_workbook(path, read_only=True, data_only=True)
    if sheet_name not in wb.sheetnames:
        available = list(wb.sheetnames)
        wb.close()
        raise ValueError(f"Sheet '{sheet_name}' 不存在，可用 Sheet: {available}")
    ws = wb[sheet_name]

    raw_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not raw_rows:
        return [], []

    # header_row 超出可用行数时返回空
    hr_idx = header_row - 1  # 转为 0-based 索引
    if hr_idx >= len(raw_rows):
        return [], []

    headers = [str(h).strip() if h is not None else "" for h in raw_rows[hr_idx]]
    rows = [[str(v) if v is not None else "" for v in row] for row in raw_rows[header_row:]]
    return headers, rows


def extract_project_ids(
    ws: Worksheet,
    start_row: int,
    end_row: int,
    col_name: str = "项目编号",
    header_row: int = 1,
) -> list[str]:
    """从工作表中提取指定行范围内的项目编号列表。

    Args:
        ws: openpyxl Worksheet 对象
        start_row: 起始行号（1-based，数据行起始，不含标题行）
        end_row: 结束行号（1-based，含）
        col_name: 项目编号列名
        header_row: 标题行所在行号（1-based）

    Returns:
        项目编号字符串列表（空值跳过）
    """
    # 读取标题行确定列索引
    headers = [str(c.value).strip() if c.value is not None else "" for c in ws[header_row]]
    if col_name not in headers:
        raise ValueError(f"源头 Excel 中缺少 '{col_name}' 列，可用列: {headers}")
    col_idx = headers.index(col_name)

    # 限制结束行号不超过实际最大行
    max_row = ws.max_row
    actual_end = min(end_row, max_row)
    if end_row > max_row:
        print(f"提示: 结束行号 {end_row} 超出最大行 {max_row}，已自动调整为 {actual_end}", file=sys.stderr)

    project_ids: list[str] = []
    for row_idx in range(start_row, actual_end + 1):
        cell = ws.cell(row=row_idx, column=col_idx + 1)
        val = str(cell.value).strip() if cell.value is not None else ""
        if val:
            project_ids.append(val)

    return project_ids


def find_row_by_project_id(
    ws: Worksheet,
    project_id: str,
    col_name: str = "项目编号",
    header_row: int = 1,
) -> dict[str, str] | None:
    """按项目编号精确匹配完整行数据。

    Args:
        ws: openpyxl Worksheet 对象
        project_id: 要匹配的项目编号
        col_name: 项目编号列名
        header_row: 标题行所在行号（1-based）

    Returns:
        {列名: 值} 字典，未找到返回 None
        重复编号取首个并输出警告
    """
    # 读取标题行
    headers = [str(c.value).strip() if c.value is not None else "" for c in ws[header_row]]
    if col_name not in headers:
        raise ValueError(f"数据 Excel 中缺少 '{col_name}' 列，可用列: {headers}")
    col_idx = headers.index(col_name)

    data_start = header_row + 1
    found_first = False
    row_data: dict[str, str] = {}
    for row_idx in range(data_start, ws.max_row + 1):
        cell = ws.cell(row=row_idx, column=col_idx + 1)
        val = str(cell.value).strip() if cell.value is not None else ""

        if val == project_id:
            if found_first:
                print(f"警告: 项目编号 '{project_id}' 重复，使用第一个匹配行（第 {row_idx} 行）", file=sys.stderr)
                continue
            found_first = True

            # 读取完整行
            for i, header in enumerate(headers):
                if header:
                    cell_val = ws.cell(row=row_idx, column=i + 1).value
                    row_data[header] = str(cell_val) if cell_val is not None else ""

    if not found_first:
        print(f"警告: 项目编号 '{project_id}' 在数据 Excel 中未找到", file=sys.stderr)
        return None

    return row_data
