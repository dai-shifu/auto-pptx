"""Shared pytest fixtures backed by the canonical asset builders."""

from pathlib import Path

import pytest

from tests.create_fixtures import build_fixture_set


@pytest.fixture
def generated_fixtures(tmp_path: Path) -> Path:
    """Return a directory containing freshly generated canonical assets."""
    fixture_dir = tmp_path / "fixtures"
    build_fixture_set(fixture_dir)
    return fixture_dir
