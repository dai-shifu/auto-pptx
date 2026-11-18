"""Fail CI before pytest if a real Tk display cannot be created."""

import tkinter as tk
import sys


if __name__ == "__main__":
    root = tk.Tk()
    root.update()
    print(f"Python: {sys.executable}")
    print(f"Tk: {root.tk.call('package', 'provide', 'Tk')}")
    print(f"Tk library: {root.tk.call('set', 'tk_library')}")
    print(f"Tk scaling: {root.tk.call('tk', 'scaling')}")
    root.destroy()
    print("Tk display available")
