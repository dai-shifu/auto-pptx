"""Shared pytest fixtures backed by the canonical asset builders."""

from pathlib import Path

import pytest

from tests.create_fixtures import build_fixture_set


def pytest_addoption(parser):
    parser.addoption(
        "--require-gui", action="store_true",
        help="Fail required GUI fixtures instead of skipping unavailable Tk",
    )


@pytest.fixture
def generated_fixtures(tmp_path: Path) -> Path:
    """Return a directory containing freshly generated canonical assets."""
    fixture_dir = tmp_path / "fixtures"
    build_fixture_set(fixture_dir)
    return fixture_dir
