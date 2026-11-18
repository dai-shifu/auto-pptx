"""Build failures must block release and platform options must stay isolated."""

from pathlib import Path
from types import SimpleNamespace

import pytest

import build


@pytest.mark.parametrize("platform", ["win32", "linux"])
def test_build_reports_output_and_isolates_windows_options(tmp_path, monkeypatch, capsys, platform):
    monkeypatch.setattr(build, "__file__", str(tmp_path / "build.py"))
    monkeypatch.setattr(build.sys, "platform", platform)
    monkeypatch.setattr(build, "project_version", lambda root: "1.2.3")
    (tmp_path / "run.py").touch()

    def compile_program(cmd, *, cwd, env):
        assert cwd == tmp_path
        assert Path(env["PATH"].split(build.os.pathsep)[0]) == Path(build.sys.executable).parent
        assert f"--report={tmp_path / 'dist' / 'compilation-report.xml'}" in cmd
        windows_options = [option for option in cmd if option.startswith((
            "--include-windows-runtime-dlls", "--windows-console-mode", "--file-version",
        ))]
        if platform == "win32":
            assert windows_options == [
                "--include-windows-runtime-dlls=yes", "--windows-console-mode=disable",
                "--file-version=1.2.3.0",
            ]
        else:
            assert not windows_options
        output = tmp_path / "dist"
        output.mkdir()
        executable = output / ("auto-pptx.exe" if platform == "win32" else "auto-pptx")
        executable.write_bytes(b"synthetic build")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(build.subprocess, "run", compile_program)
    build.main()
    output = capsys.readouterr().out
    assert "耗时:" in output
    assert "单文件大小: 15 字节" in output
    assert "编译报告:" in output


def test_compiler_failure_preserves_exit_status(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(build, "__file__", str(tmp_path / "build.py"))
    monkeypatch.setattr(build, "project_version", lambda root: "1.2.3")
    (tmp_path / "run.py").touch()
    monkeypatch.setattr(build.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=23))
    with pytest.raises(SystemExit) as error:
        build.main()
    assert error.value.code == 23
    output = capsys.readouterr()
    assert "打包失败" in output.err
    assert "打包完成" not in output.out
    assert "单文件大小" not in output.out
