"""Release packages and retries must preserve data and published content."""

import json
import shutil
import urllib.request

import pytest

from scripts import release
from scripts.publish_release import AssetRedirect, publish


COMMIT = "a" * 40


@pytest.fixture
def package(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    for name in ("pyproject.toml",):
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(release.ROOT / name, destination)
    (root / "config.toml").write_text("private local configuration", encoding="utf-8")
    executable = tmp_path / "auto-pptx.exe"
    executable.write_bytes(b"MZ synthetic executable for package tests")
    monkeypatch.setattr(release.subprocess, "check_output", lambda *a, **kw: COMMIT + "\n")
    archive = release.package_windows(executable, tmp_path / "release", root=root)
    return archive


@pytest.mark.parametrize("tag", ["v9.9.9", "0.1.0", "v0.1.0-rc1", "v00.1.0"])
def test_tag_mismatch_is_rejected(tag):
    with pytest.raises(ValueError, match="Release tag"):
        release.project_version(tag=tag)


def test_windows_version_limits(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "65536.0.0"\n')
    with pytest.raises(ValueError, match="65535"):
        release.project_version(tmp_path)


def test_only_executable_is_distributed_with_optional_checksum(package):
    assert release.verified_assets(package.parent)[0] == package
    assert {path.name for path in package.parent.iterdir()} == {
        package.name, "SHA256SUMS.txt", "release-info.json"
    }
    assert package.read_bytes() == b"MZ synthetic executable for package tests"
    info = json.loads((package.parent / "release-info.json").read_text())
    assert info["commit"] == COMMIT
    assert info["trial"] is None
    assert info["executable_sha256"] == release.sha256(package)


def test_altered_package_is_rejected(package):
    package.write_bytes(package.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="SHA256SUMS"):
        release.verified_assets(package.parent)


class FakeGitHub:
    def __init__(self, draft=True, existing=None):
        self.release = {"draft": draft} if draft is not None else None
        self.existing = existing or {}
        self.created = []
        self.uploaded = []

    def find_release(self, tag):
        return self.release

    def assets(self, release):
        return [{"name": name, "id": name} for name in self.existing]

    def asset_bytes(self, asset):
        return self.existing[asset["id"]]

    def create_draft(self, tag, commit):
        self.created.append((tag, commit))
        return {"draft": True}

    def upload(self, release, path):
        self.uploaded.append(path.name)


def test_new_release_is_a_draft(package):
    client = FakeGitHub(draft=None)
    tag = f"v{release.project_version()}"
    publish(client, tag, COMMIT, package.parent)
    assert client.created == [(tag, COMMIT)]
    assert set(client.uploaded) == {package.name, "SHA256SUMS.txt"}


def test_retry_uploads_only_missing_assets(package):
    client = FakeGitHub(existing={package.name: package.read_bytes()})
    publish(client, f"v{release.project_version()}", COMMIT, package.parent)
    assert not client.created
    assert client.uploaded == ["SHA256SUMS.txt"]


def test_conflicting_checksum_fails_before_any_upload(package):
    client = FakeGitHub(existing={"SHA256SUMS.txt": b"conflicting"})
    with pytest.raises(ValueError, match="Conflicting"):
        publish(client, f"v{release.project_version()}", COMMIT, package.parent)
    assert not client.uploaded
    assert not client.created


def test_published_release_remains_unchanged(package):
    client = FakeGitHub(draft=False, existing={package.name: b"old published content"})
    publish(client, f"v{release.project_version()}", COMMIT, package.parent)
    assert not client.uploaded
    assert not client.created


def test_wrong_commit_is_rejected_before_network_access(package):
    client = FakeGitHub()
    with pytest.raises(ValueError, match="provenance"):
        publish(client, f"v{release.project_version()}", "b" * 40, package.parent)
    assert not client.uploaded


def test_trial_provenance_cannot_be_published_as_formal_release(package):
    metadata = package.parent / "release-info.json"
    info = json.loads(metadata.read_text())
    info["trial"] = "local"
    metadata.write_text(json.dumps(info))
    client = FakeGitHub(draft=None)
    with pytest.raises(ValueError, match="provenance"):
        publish(client, f"v{release.project_version()}", COMMIT, package.parent)
    assert not client.created
    assert not client.uploaded


def test_api_token_is_not_forwarded_to_asset_host():
    request = urllib.request.Request(
        "https://api.github.com/repos/example/project/releases/assets/1",
        headers={"Authorization": "Bearer synthetic-test-token"},
    )
    redirected = AssetRedirect().redirect_request(
        request, None, 302, "Found", {}, "https://release-assets.githubusercontent.com/example"
    )
    assert not redirected.has_header("Authorization")
