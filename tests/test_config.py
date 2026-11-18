import pytest

from src.config import Config, load_config, save_config


def test_load_config_success(tmp_path):
    """加载 config.toml，验证 template_column 和 mapping 方向。"""
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        'template_column = "填料"\n\n[mapping]\n"标题" = "title"\n"作者" = "author"\n',
        encoding="utf-8",
    )
    config = load_config(cfg)
    assert config.template_column == "填料"
    assert config.mapping == {"标题": "title", "作者": "author"}


def test_load_config_file_not_found(tmp_path):
    """文件不存在时返回默认值，不创建文件。"""
    path = tmp_path / "nonexistent.toml"
    config = load_config(path)
    assert config.template_column == "填料"
    assert config.header_row == 1
    assert config.mapping == {}
    assert not path.exists()


def test_load_config_invalid_toml(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text("{{invalid toml", encoding="utf-8")
    with pytest.raises(ValueError, match="配置文件格式错误"):
        load_config(bad)


def test_load_config_defaults(tmp_path):
    """缺失字段使用默认值。"""
    cfg = tmp_path / "cfg.toml"
    cfg.write_text('template_column = "标签"\n', encoding="utf-8")
    config = load_config(cfg)
    assert config.template_column == "标签"
    assert config.mapping == {}


def test_save_and_load_roundtrip(tmp_path):
    """保存再加载，映射方向保持不变（excel_col → placeholder）。"""
    config = Config(
        template_column="填料",
        mapping={"标题": "title", "部门": "dept"},
    )
    path = tmp_path / "config.toml"
    save_config(config, path)
    loaded = load_config(path)
    assert loaded.template_column == "填料"
    assert loaded.mapping == {"标题": "title", "部门": "dept"}


def test_save_without_mapping(tmp_path):
    """无映射时也正常保存。"""
    config = Config(template_column="填料")
    path = tmp_path / "config.toml"
    save_config(config, path)
    loaded = load_config(path)
    assert loaded.template_column == "填料"
    assert loaded.mapping == {}
