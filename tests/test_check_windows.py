"""CI cleanup warnings must not hide executable verification failures."""

import json
import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from scripts import check_windows as check


def locked_directory(*args, **kwargs):
    raise PermissionError("executable is still locked")


@pytest.mark.parametrize("ci", [False, True])
def test_cleanup_of_locked_files_is_only_optional_in_ci(tmp_path, monkeypatch, capsys, ci):
    monkeypatch.setattr(check.tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(check.shutil, "rmtree", locked_directory)
    if ci:
        with check.verification_directory(tmp_path) as directory:
            assert directory.parent == tmp_path
        assert f"::warning::Could not clean verification directory {directory}" in (
            capsys.readouterr().err
        )
    else:
        with pytest.raises(PermissionError, match="still locked"):
            with check.verification_directory():
                pass


@pytest.mark.parametrize("ci", [False, True])
def test_cleanup_preserves_verification_error(tmp_path, monkeypatch, ci):
    monkeypatch.setattr(check.tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(check.shutil, "rmtree", locked_directory)
    with pytest.raises(ValueError, match="verification failed") as caught:
        with check.verification_directory(tmp_path if ci else None):
            raise ValueError("verification failed")
    assert "Could not clean verification directory" in caught.value.__notes__[0]


def test_ci_does_not_ignore_unrelated_cleanup_errors(tmp_path, monkeypatch):
    def disk_error(*args, **kwargs):
        raise OSError("disk failure")

    monkeypatch.setattr(check.shutil, "rmtree", disk_error)
    with pytest.raises(OSError, match="disk failure"):
        with check.verification_directory(tmp_path):
            pass


@pytest.fixture
def windows_check(tmp_path, monkeypatch):
    package = tmp_path / "release"
    package.mkdir()
    executable = package / "synthetic.exe"
    executable.write_bytes(b"MZ synthetic executable")
    digest = check.sha256(executable)
    (package / "SHA256SUMS.txt").write_text(f"{digest}  {executable.name}\n")
    (package / "release-info.json").write_text(json.dumps({
        "version": check.project_version(), "executable_sha256": digest,
    }))
    version = tuple(int(part) for part in check.project_version().split(".")) + (0,)
    monkeypatch.setattr(check, "executable_versions", lambda path: (version, version))
    monkeypatch.setattr(check.sys, "platform", "win32")
    user32, kernel32 = MagicMock(), MagicMock()
    user32.FindWindowW.side_effect = [0, 123]
    user32.IsWindowVisible.return_value = True

    def window_pid(window, pointer):
        pointer._obj.value = 200
        return 1

    user32.GetWindowThreadProcessId.side_effect = window_pid
    kernel32.OpenProcess.return_value = 456
    kernel32.WaitForSingleObject.return_value = 0
    monkeypatch.setattr(
        check.ctypes, "WinDLL",
        lambda name, **kwargs: {"user32": user32, "kernel32": kernel32}[name],
        raising=False,
    )
    process = MagicMock(pid=100)
    process.poll.return_value = None

    def start(args, cwd):
        (cwd / "config.toml").write_text('header_row = 1\ntemplate_column = "template"\n')
        return process

    monkeypatch.setattr(check.subprocess, "Popen", start)
    taskkill = MagicMock()
    monkeypatch.setattr(check.subprocess, "run", taskkill)
    return SimpleNamespace(
        package=package, process=process, kernel32=kernel32, taskkill=taskkill,
    )


def test_ci_verification_waits_for_gui_child_before_cleanup_warning(
    windows_check, tmp_path, monkeypatch, capsys,
):
    monkeypatch.setattr(check.shutil, "rmtree", locked_directory)
    check.check_windows(windows_check.package, runner_temp=tmp_path)
    windows_check.taskkill.assert_called_once_with(
        ["taskkill", "/PID", "100", "/T", "/F"], check=True,
    )
    windows_check.process.wait.assert_called_once_with(timeout=15)
    windows_check.kernel32.OpenProcess.assert_called_once_with(0x00100000, False, 200)
    windows_check.kernel32.WaitForSingleObject.assert_called_once_with(456, 15000)
    windows_check.kernel32.CloseHandle.assert_called_once_with(456)
    output = capsys.readouterr()
    assert "::warning::" in output.err
    assert "first-run config passed" in output.out


def test_live_gui_child_fails_ci_even_when_cleanup_is_locked(
    windows_check, tmp_path, monkeypatch, capsys,
):
    windows_check.kernel32.WaitForSingleObject.return_value = 258
    monkeypatch.setattr(check.shutil, "rmtree", locked_directory)
    with pytest.raises(RuntimeError, match="GUI process did not exit"):
        check.check_windows(windows_check.package, runner_temp=tmp_path)
    windows_check.kernel32.CloseHandle.assert_called_once_with(456)
    assert "first-run config passed" not in capsys.readouterr().out


def test_failed_taskkill_is_not_downgraded_to_ci_warning(
    windows_check, tmp_path, monkeypatch,
):
    windows_check.taskkill.side_effect = subprocess.CalledProcessError(1, "taskkill")
    monkeypatch.setattr(check.shutil, "rmtree", locked_directory)
    with pytest.raises(subprocess.CalledProcessError):
        check.check_windows(windows_check.package, runner_temp=tmp_path)
    windows_check.kernel32.CloseHandle.assert_called_once_with(456)


def test_parent_exit_timeout_still_fails_ci(windows_check, tmp_path, monkeypatch):
    windows_check.process.wait.side_effect = subprocess.TimeoutExpired("synthetic.exe", 15)
    monkeypatch.setattr(check.shutil, "rmtree", locked_directory)
    with pytest.raises(subprocess.TimeoutExpired):
        check.check_windows(windows_check.package, runner_temp=tmp_path)
    windows_check.kernel32.CloseHandle.assert_called_once_with(456)


def test_checksum_failure_still_fails_ci(windows_check, tmp_path):
    (windows_check.package / "synthetic.exe").write_bytes(b"modified executable")
    with pytest.raises(ValueError, match="checksum mismatch"):
        check.check_windows(windows_check.package, runner_temp=tmp_path)
    windows_check.taskkill.assert_not_called()
