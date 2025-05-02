import customtkinter as ctk
from tkinter import messagebox
from ui.tooltip import ToolTip

def open_advanced_processing(app, config, save_config, is_processing):
    win = ctk.CTkToplevel(app)
    win.title("Advanced Processing")
    win.geometry("400x220")
    win.resizable(False, False)

    # Center the dialog
    win.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (win.winfo_width() // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (win.winfo_height() // 2)
    win.geometry(f"+{x}+{y}")

    # Config vars
    audio_var = ctk.BooleanVar(value=config.get("audio_cleanup", True))
    translate_var = ctk.BooleanVar(value=config.get("translate_filenames", False))

    # Audio cleanup
    audio_check = ctk.CTkCheckBox(win, text="Enable Audio Cleanup", variable=audio_var)
    audio_check.pack(pady=(25, 10))
    ToolTip(win, audio_check, "Normalizes and denoises the audio track using FFmpeg.")

    # Filename translation
    translate_check = ctk.CTkCheckBox(win, text="Translate Filenames", variable=translate_var)
    translate_check.pack(pady=5)
    ToolTip(win, translate_check, "Uses DeepL API to rename files automatically.")

    def save():
        if is_processing:
            messagebox.showwarning("Busy", "Please wait for the current job to finish.")
            return

        config["audio_cleanup"] = audio_var.get()
        config["translate_filenames"] = translate_var.get()
        save_config(config)
        win.destroy()

    save_button = ctk.CTkButton(win, text="Save", command=save, width=160)
    save_button.pack(pady=20)
    ToolTip(win, save_button, "Apply changes for future processing.")
