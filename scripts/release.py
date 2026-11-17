"""Validate versions and prepare the standalone Windows exe download."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def project_version(root: Path = ROOT, tag: str | None = None) -> str:
    with (root / "pyproject.toml").open("rb") as stream:
        version = tomllib.load(stream)["project"]["version"]
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        raise ValueError("Project version must use X.Y.Z")
    if any(int(part) > 65535 for part in version.split(".")):
        raise ValueError("Windows version components must be at most 65535")
    if tag is not None and tag != f"v{version}":
        raise ValueError(f"Release tag must be v{version}, got {tag!r}")
    return version


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def package_windows(
    executable: Path,
    destination: Path,
    *,
    root: Path = ROOT,
    tag: str | None = None,
    trial: str | None = None,
) -> Path:
    """Copy only the executable, with separate checksums and build provenance."""
    version = project_version(root, tag)
    if trial is not None and not re.fullmatch(r"[A-Za-z0-9-]+", trial):
        raise ValueError("Trial identifier must contain only letters, digits or hyphens")
    if not executable.is_file():
        raise FileNotFoundError(executable)
    with executable.open("rb") as stream:
        if stream.read(2) != b"MZ":
            raise ValueError("Expected a Windows executable (MZ header)")
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    suffix = f"-trial-{trial}" if trial else ""
    name = f"auto-pptx-v{version}{suffix}-windows-x64.exe"
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / name
    if any(destination.iterdir()):
        raise FileExistsError(f"Use an empty output directory: {destination}")
    shutil.copyfile(executable, output)
    info = {
        "version": version,
        "commit": commit,
        "trial": trial,
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "local"),
        "executable_sha256": sha256(output),
        "verification": "Startup and first-run config automated on Windows; generation requires release checklist",
    }
    (destination / "release-info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "SHA256SUMS.txt").write_text(
        f"{sha256(output)}  {name}\n", encoding="utf-8"
    )
    return output


def verified_assets(directory: Path) -> list[Path]:
    """Reject missing, altered or ambiguous release inputs before publishing."""
    checksum = directory / "SHA256SUMS.txt"
    match = re.fullmatch(
        r"([0-9a-f]{64})  (auto-pptx-v[0-9.]+-windows-x64\.exe)\n",
        checksum.read_text(encoding="utf-8"),
    )
    if match is None:
        raise ValueError("Expected one formal Windows exe in SHA256SUMS.txt")
    package = directory / match[2]
    if list(directory.glob("*.exe")) != [package] or sha256(package) != match[1]:
        raise ValueError("Release package does not match SHA256SUMS.txt")
    return [package, checksum]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("version", "package"))
    parser.add_argument("--tag")
    parser.add_argument("--trial")
    parser.add_argument("--executable", type=Path, default=ROOT / "dist/auto-pptx.exe")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/windows-release")
    args = parser.parse_args()
    if args.command == "version":
        print(project_version(tag=args.tag))
    else:
        if args.tag and args.trial:
            parser.error("--tag and --trial cannot be combined")
        print(package_windows(
            args.executable, args.output, tag=args.tag, trial=args.trial
        ))


if __name__ == "__main__":
    main()
