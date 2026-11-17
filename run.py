"""GUI 启动入口，同时供 Nuitka 打包使用。

用法:
    uv run run.py
"""
from src.gui import main

if __name__ == "__main__":
    main()
