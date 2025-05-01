# theme/style.py — Custom UI Theming
from tkinter import ttk

def apply_theme(root):
    style = ttk.Style(root)
    root.configure(bg="#2b2b2b")

    style.theme_use("clam")

    style.configure("TLabel", background="#2b2b2b", foreground="#f0f0f0", font=("Segoe UI", 10))
    style.configure("TButton", background="#444", foreground="#f0f0f0", padding=6)
    style.configure("TCheckbutton", background="#2b2b2b", foreground="#f0f0f0")
    style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#b4d273", background="#2b2b2b")

    style.map("TButton", background=[("active", "#666")])
