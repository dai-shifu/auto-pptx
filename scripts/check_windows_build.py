"""Check the locked Nuitka runtime discovery before a Windows build."""

import sys
from pathlib import Path


def main() -> None:
    if sys.platform != "win32":
        raise RuntimeError("Windows build preflight must run on Windows")
    # Use the same discovery as the locked Nuitka build, not a separate DLL search.
    from nuitka.freezer.DllDependenciesWin32 import getMSVCRedistPath
    from nuitka.Tracing import inclusion_logger
    from nuitka.Version import getNuitkaVersion

    print(f"Python: {sys.executable}", flush=True)
    print(f"Nuitka: {getNuitkaVersion()}", flush=True)
    runtime = getMSVCRedistPath(inclusion_logger)
    if runtime is None or not any(Path(runtime).rglob("*.dll")):
        raise RuntimeError(
            "Nuitka cannot locate redistributable runtime DLLs. Install the "
            "Visual Studio Build Tools C++ components with VC/Redist/MSVC files."
        )
    print(f"MSVC redistributable runtime: {runtime}", flush=True)


if __name__ == "__main__":
    main()
