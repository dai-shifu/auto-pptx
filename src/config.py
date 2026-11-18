"""配置模块：读取/写入 config.toml。"""
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    template_column: str = ""
    header_row: int | None = None
    mapping: dict[str, str] = field(default_factory=dict)  # excel_col → placeholder


def load_config(path: str | Path) -> Config:
    path = Path(path)
    if not path.exists():
        return Config()

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"配置文件格式错误: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("配置文件格式错误: 顶层必须是字典")

    return Config(
        template_column=str(data.get("template_column", "")),
        header_row=int(data["header_row"]) if "header_row" in data else None,
        mapping=_parse_string_dict(data.get("mapping", {})),
    )


def _parse_string_dict(raw: object) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def _escape_toml_basic_string(s: str) -> str:
    """转义 TOML 基本字符串中的特殊字符（双引号、反斜杠）。"""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def save_config(config: Config, path: str | Path) -> None:
    path = Path(path)
    lines: list[str] = []
    if config.template_column:
        tpl_col = _escape_toml_basic_string(config.template_column)
        lines.append(f'template_column = "{tpl_col}"\n')
    if config.header_row is not None:
        lines.append(f"header_row = {config.header_row}\n")

    if config.mapping:
        if lines:
            lines.append("\n")
        lines.append("[mapping]\n")
        for excel_col, placeholder in config.mapping.items():
            esc_key = _escape_toml_basic_string(excel_col)
            esc_val = _escape_toml_basic_string(placeholder)
            lines.append(f'"{esc_key}" = "{esc_val}"\n')

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
