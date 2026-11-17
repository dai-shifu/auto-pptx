"""Fail CI before pytest if a real Tk display cannot be created."""

import tkinter as tk


if __name__ == "__main__":
    root = tk.Tk()
    root.update()
    root.destroy()
    print("Tk display available")
