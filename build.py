"""Nuitka 打包脚本。

使用方法:
    uv run --group build build.py

生成的可执行文件位于 dist/ 目录。
"""
import os
import subprocess
import sys
import time
from pathlib import Path

from scripts.release import project_version


def main() -> None:
    project_root = Path(__file__).parent
    entry = project_root / "run.py"
    version = project_version(project_root)
    output_dir = project_root / "dist"
    report = output_dir / "compilation-report.xml"

    if not entry.exists():
        print(f"错误: 入口文件不存在: {entry}", file=sys.stderr)
        sys.exit(1)

    # 确保 venv 的 bin 目录在 PATH 中（Nuitka 需要找到 patchelf）
    venv_bin = Path(sys.executable).parent
    env = os.environ.copy()
    env["PATH"] = str(venv_bin) + os.pathsep + env.get("PATH", "")

    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        f"--output-dir={output_dir}",
        f"--report={report}",
        f"--output-filename=auto-pptx",
        "--include-package=src",
        "--nofollow-import-to=pytest",
        "--nofollow-import-to=_pytest",
        "--no-deployment-flag=self-execution",
        "--assume-yes-for-downloads",
        "--enable-plugin=tk-inter",
    ]
    if sys.platform == "win32":
        cmd.extend([
            "--include-windows-runtime-dlls=yes",
            "--windows-console-mode=disable",
            "--company-name=auto-pptx",
            "--product-name=auto-pptx",
            "--file-description=Excel-to-PPTX Batch Generator",
            f"--file-version={version}.0",
            f"--product-version={version}.0",
        ])
    cmd.append(str(entry))

    print("开始 Nuitka 打包...", flush=True)
    print(f"命令: {' '.join(cmd)}", flush=True)

    started = time.perf_counter()
    result = subprocess.run(cmd, cwd=project_root, env=env)
    if result.returncode != 0:
        print("打包失败", file=sys.stderr)
        sys.exit(result.returncode)

    executable = output_dir / ("auto-pptx.exe" if sys.platform == "win32" else "auto-pptx")
    print(f"打包完成！输出目录: {output_dir}")
    print(f"耗时: {time.perf_counter() - started:.1f} 秒")
    print(f"单文件大小: {executable.stat().st_size:,} 字节")
    print(f"编译报告: {report}")


if __name__ == "__main__":
    main()
