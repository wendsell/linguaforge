# dialogs/advanced.py

import customtkinter as ctk

class AdvancedDialog:
    def __init__(self, parent, config, save_callback):
        self.top = ctk.CTkToplevel(parent)
        self.top.title("Advanced Processing")
        self.top.geometry("380x180")
        self.top.resizable(False, False)

        self.config = config
        self.save_callback = save_callback

        self.cleanup_var = ctk.BooleanVar(value=self.config.get("audio_cleanup", True))
        self.translate_var = ctk.BooleanVar(value=self.config.get("translate_filenames", False))

        ctk.CTkLabel(self.top, text="Advanced Processing Options", font=("Segoe UI", 16, "bold")).pack(pady=(15, 5))

        cleanup_check = ctk.CTkCheckBox(
            self.top, text="Enable Audio Cleanup", variable=self.cleanup_var,
            onvalue=True, offvalue=False
        )
        cleanup_check.pack(pady=8)

        translate_check = ctk.CTkCheckBox(
            self.top, text="Translate Filenames", variable=self.translate_var,
            onvalue=True, offvalue=False
        )
        translate_check.pack(pady=8)

        ctk.CTkButton(self.top, text="Save", command=self.save).pack(pady=16)

        self.top.focus()
        self.top.grab_set()
        self.top.transient(parent)

    def save(self):
        self.config["audio_cleanup"] = self.cleanup_var.get()
        self.config["translate_filenames"] = self.translate_var.get()
        self.save_callback(self.config)
        self.top.destroy()
