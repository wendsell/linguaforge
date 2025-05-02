import customtkinter as ctk

def apply_theme(mode):
    if mode in ["Light", "Dark", "System"]:
        ctk.set_appearance_mode(mode)
    else:
        print(f"Unsupported theme: {mode}")