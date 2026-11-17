"""Check the Windows exe, versions, visible startup and first-run config."""

import argparse
import ctypes
import json
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from ctypes import wintypes
from pathlib import Path

from scripts.release import project_version, sha256


def executable_versions(executable: Path) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Read fixed file and product versions through the Windows version API."""
    version_api = ctypes.WinDLL("version", use_last_error=True)
    version_api.GetFileVersionInfoSizeW.argtypes = [
        wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)
    ]
    version_api.GetFileVersionInfoSizeW.restype = wintypes.DWORD
    version_api.GetFileVersionInfoW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p
    ]
    version_api.VerQueryValueW.argtypes = [
        ctypes.c_void_p, wintypes.LPCWSTR,
        ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(wintypes.UINT)
    ]
    size = version_api.GetFileVersionInfoSizeW(str(executable), None)
    if not size:
        raise ctypes.WinError(ctypes.get_last_error())
    buffer = ctypes.create_string_buffer(size)
    if not version_api.GetFileVersionInfoW(str(executable), 0, size, buffer):
        raise ctypes.WinError(ctypes.get_last_error())
    pointer = ctypes.c_void_p()
    length = wintypes.UINT()
    if not version_api.VerQueryValueW(
        buffer, "\\", ctypes.byref(pointer), ctypes.byref(length)
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    # VS_FIXEDFILEINFO begins with signature, struct version, then two DWORDs each
    # for file and product versions; DWORD order is major/minor and patch/build.
    fields = ctypes.cast(pointer, ctypes.POINTER(wintypes.DWORD))
    if fields[0] != 0xFEEF04BD or length.value < 13 * ctypes.sizeof(wintypes.DWORD):
        raise ValueError("Invalid Windows version resource")

    def parts(high: int, low: int) -> tuple[int, ...]:
        return high >> 16, high & 65535, low >> 16, low & 65535

    return parts(fields[2], fields[3]), parts(fields[4], fields[5])


@contextmanager
def verification_directory(runner_temp: Path | None = None) -> Iterator[Path]:
    """Keep local cleanup strict; allow locked files on a disposable CI runner."""
    temporary = tempfile.TemporaryDirectory(prefix="auto-pptx-check-", dir=runner_temp)
    try:
        yield Path(temporary.name)
    finally:
        failure = sys.exc_info()[1]
        try:
            temporary.cleanup()
        except OSError as error:
            message = f"Could not clean verification directory {temporary.name}: {error}"
            if failure is not None:
                failure.add_note(message)
            elif runner_temp is not None and isinstance(error, PermissionError):
                print(f"::warning::{message}; left for runner cleanup", file=sys.stderr)
            else:
                raise


def check_windows(directory: Path, *, runner_temp: Path | None = None) -> None:
    if sys.platform != "win32":
        raise RuntimeError("Executable verification must run on Windows")
    packages = list(directory.glob("*.exe"))
    if len(packages) != 1:
        raise ValueError("Expected exactly one Windows exe")
    package = packages[0]
    expected = f"{sha256(package)}  {package.name}\n"
    if (directory / "SHA256SUMS.txt").read_text(encoding="utf-8") != expected:
        raise ValueError("Executable checksum mismatch")
    version = project_version()
    expected_version = tuple(int(part) for part in version.split(".")) + (0,)
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    user32.FindWindowW.restype = wintypes.HWND
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.GetWindowThreadProcessId.argtypes = [
        wintypes.HWND, ctypes.POINTER(wintypes.DWORD)
    ]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    title = "Auto PPTX Generator"
    if user32.FindWindowW(None, title):
        raise RuntimeError("Close existing Auto PPTX Generator windows before verification")
    with verification_directory(runner_temp) as unpacked:
        executable = unpacked / package.name
        shutil.copyfile(package, executable)
        if executable_versions(executable) != (expected_version, expected_version):
            raise ValueError("Executable file/product version mismatch")
        info = json.loads((directory / "release-info.json").read_text(encoding="utf-8"))
        if info["version"] != version or info["executable_sha256"] != sha256(executable):
            raise ValueError("Executable does not match package metadata")
        config = unpacked / "config.toml"
        if config.exists():
            raise ValueError("Startup check requires a clean directory")
        process = subprocess.Popen([str(executable)], cwd=unpacked)
        window_process = None
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(
                        f"Program exited before verification: {process.returncode}"
                    )
                window = user32.FindWindowW(None, title)
                if window and user32.IsWindowVisible(window) and config.is_file():
                    pid = wintypes.DWORD()
                    if not user32.GetWindowThreadProcessId(window, ctypes.byref(pid)):
                        raise ctypes.WinError(ctypes.get_last_error())
                    # Keep the GUI child's handle before taskkill can remove its PID.
                    window_process = kernel32.OpenProcess(0x00100000, False, pid.value)
                    if not window_process:
                        raise ctypes.WinError(ctypes.get_last_error())
                    break
                time.sleep(0.5)
            else:
                raise RuntimeError("Visible Tk window did not appear within 60 seconds")
            with config.open("rb") as stream:
                created = tomllib.load(stream)
            if created.get("header_row") != 1 or not created.get("template_column"):
                raise ValueError("First-run configuration is invalid")
        finally:
            try:
                # onefile launches a child; kill and wait for both processes.
                if process.poll() is None:
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"], check=True
                    )
                process.wait(timeout=15)
                if window_process:
                    result = kernel32.WaitForSingleObject(window_process, 15000)
                    if result == 0xFFFFFFFF:
                        raise ctypes.WinError(ctypes.get_last_error())
                    if result != 0:
                        raise RuntimeError("GUI process did not exit within 15 seconds")
            finally:
                if window_process:
                    kernel32.CloseHandle(window_process)
    print("Executable, versions, visible startup and first-run config passed; "
          "manual generation check required")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument(
        "--runner-temp", type=Path,
        help="Use a disposable CI directory; warn if verified files remain locked",
    )
    args = parser.parse_args()
    check_windows(args.directory, runner_temp=args.runner_temp)
