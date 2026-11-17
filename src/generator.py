"""单 Excel 管线：Excel → 模板匹配 + 占位符替换 → 批量生成 PPT。"""

import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook
from pptx import Presentation

from .auto_detect import (
    collect_placeholders,
    detect_and_suggest_detailed,
    tokenize_template_value,
)
from .pptx_engine import clone_slide, prune_slides, replace_in_slide
from .template_matching import build_template_index


@dataclass
class GenerationResult:
    """生成结果及需要向用户展示的非致命诊断。"""

    output_path: Path
    generated_pages: int
    skipped_rows: list[int] = field(default_factory=list)
    unmatched_templates: list[str] = field(default_factory=list)
    unresolved_placeholders: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def generate(
    prs: Presentation,
    excel_path: str | Path,
    sheet_name: str,
    selected_rows: list[int],
    output_path: str | Path,
    template_column: str | None = None,
    mapping: dict[str, str] | None = None,  # {excel_col: placeholder}
    header_row: int = 1,
) -> GenerationResult:
    """批量生成 PPT。

    从 Excel 指定 Sheet 读取数据，对 selected_rows 中的每一行：
    - 模板列值按 "/" 分割后直接匹配 {{tpl::name}} 标识的 Slide
    - 同行数据按 mapping 转换后替换占位符
    - 若未提供 template_column / mapping，则自动检测
    - header_row 指定标题行所在行号（1-based），默认 1
    """

    # 1. 加载 Excel
    wb = load_workbook(str(excel_path), data_only=True)
    try:
        if sheet_name not in wb.sheetnames:
            available = list(wb.sheetnames)
            raise ValueError(f"Sheet '{sheet_name}' 不存在，可用 Sheet: {available}")
        ws = wb[sheet_name]

        # 2. 读取标题行
        headers = [
            str(ws.cell(row=header_row, column=c).value).strip() if ws.cell(row=header_row, column=c).value else ""
            for c in range(1, ws.max_column + 1)
        ]

        _validate_headers(headers)

        # 3. 建立模板索引
        tpl_index = build_template_index(prs)
        if not tpl_index:
            raise ValueError("模板 PPT 中没有找到任何 {{tpl::}} 标识")

        # 空选择不能产生有效报告。
        if not selected_rows:
            raise ValueError("未选择任何数据行，无法生成 PPT")

        # 4. 确定模板列和映射（传入优先，否则自动检测）
        detection_warnings: list[str] = []
        if template_column is None or mapping is None:
            raw_rows = [
                [str(ws.cell(row=r, column=c + 1).value or "") for c in range(len(headers))]
                for r in selected_rows
            ]
            detection = detect_and_suggest_detailed(prs, headers, raw_rows)
            if template_column is None:
                template_column = detection.template_column
            if mapping is None:
                mapping = detection.mapping
            if detection.conflicts:
                conflicted = ", ".join(conflict.placeholder for conflict in detection.conflicts)
                detection_warnings.append(f"自动映射存在冲突，已保持未映射: {conflicted}")

        if template_column is None:
            raise ValueError("无法自动检测模板列，请确认 Excel 模板列的值与 PPT {{tpl::name}} 名称一致")
        if template_column not in headers:
            raise ValueError(f"模板列 '{template_column}' 不在 Excel 标题行中，可用列: {headers}")

        _validate_mapping(headers, mapping)

        tpl_col = headers.index(template_column)

        # 5. 记录原始模板页数量
        original_count = len(prs.slides)

        # 6. 逐行处理
        generated = 0
        skipped_rows: list[int] = []
        unmatched_templates: list[str] = []
        for row_idx in selected_rows:
            # 跳过标题行及之前的行（用户可能误选）
            if row_idx <= header_row:
                print(f"警告: 行 {row_idx} 是标题行或之前，跳过", file=sys.stderr)
                skipped_rows.append(row_idx)
                continue

            # 6a. 读取模板列值
            filler_cell = ws.cell(row=row_idx, column=tpl_col + 1)
            filler_raw = str(filler_cell.value).strip() if filler_cell.value is not None else ""
            if not filler_raw:
                print(f"警告: 行 {row_idx} 模板列为空，跳过", file=sys.stderr)
                skipped_rows.append(row_idx)
                continue

            # 6b. "/" 分割 → 直接作为 tpl 名称
            tpl_names_list = tokenize_template_value(filler_raw)
            if not tpl_names_list:
                skipped_rows.append(row_idx)
                continue

            # 6c. 读取同行数据
            row_data: dict[str, str] = {}
            for i, header in enumerate(headers):
                if header:
                    cell_val = ws.cell(row=row_idx, column=i + 1).value
                    row_data[header] = str(cell_val) if cell_val is not None else ""

            # 6d. 按 mapping 转换占位符
            mapped_data: dict[str, str] = {}
            for excel_col, placeholder in mapping.items():
                if excel_col in row_data:
                    mapped_data[placeholder] = row_data[excel_col]

            # 6e. 为每个 tpl 生成 Slide
            row_generated = 0
            for tpl_name in tpl_names_list:
                source_slide = tpl_index.get(tpl_name)
                if source_slide is None:
                    print(f"警告: '{tpl_name}' 在模板 PPT 未找到对应 Slide，跳过", file=sys.stderr)
                    if tpl_name not in unmatched_templates:
                        unmatched_templates.append(tpl_name)
                    continue

                new_slide = clone_slide(prs, source_slide)
                replace_in_slide(new_slide, mapped_data)
                generated += 1
                row_generated += 1

            if row_generated == 0:
                skipped_rows.append(row_idx)

        if generated == 0:
            raise ValueError("未生成任何幻灯片：所选行均为空、无效或没有匹配的模板")

        # 7. 删除原始模板页
        prune_slides(prs, original_count)
        if original_count > 0:
            print(f"已删除 {original_count} 个原始模板页", file=sys.stderr)

        unresolved = collect_placeholders(prs)
        warnings = detection_warnings + _build_warnings(
            skipped_rows, unmatched_templates, unresolved
        )

        # 8. 保存
        output_path = Path(output_path)
        prs.save(str(output_path))
        print(f"生成完成: {generated} 页 → {output_path}")
        return GenerationResult(
            output_path=output_path,
            generated_pages=generated,
            skipped_rows=skipped_rows,
            unmatched_templates=unmatched_templates,
            unresolved_placeholders=unresolved,
            warnings=warnings,
        )
    finally:
        wb.close()


def _validate_headers(headers: list[str]) -> None:
    duplicates = sorted(
        header for header, count in Counter(h for h in headers if h).items() if count > 1
    )
    if duplicates:
        raise ValueError(f"Excel 标题行包含重复列名: {duplicates}")


def _validate_mapping(headers: list[str], mapping: dict[str, str]) -> None:
    missing = sorted(column for column in mapping if column not in headers)
    if missing:
        raise ValueError(f"映射引用了不存在的 Excel 列: {missing}")

    duplicate_targets = sorted(
        target for target, count in Counter(mapping.values()).items() if target and count > 1
    )
    if duplicate_targets:
        raise ValueError(f"多个 Excel 列映射到同一占位符: {duplicate_targets}")


def _build_warnings(
    skipped_rows: list[int],
    unmatched_templates: list[str],
    unresolved_placeholders: list[str],
) -> list[str]:
    warnings: list[str] = []
    if skipped_rows:
        warnings.append(f"跳过 Excel 行: {', '.join(map(str, skipped_rows))}")
    if unmatched_templates:
        warnings.append(f"未找到模板: {', '.join(unmatched_templates)}")
    if unresolved_placeholders:
        warnings.append(f"仍有未替换占位符: {', '.join(unresolved_placeholders)}")
    return warnings
