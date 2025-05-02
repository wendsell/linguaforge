import customtkinter as ctk
from ui.tooltip import ToolTip

def open_advanced_processing(app, config, save_config):
    win = ctk.CTkToplevel(app)
    win.title("Advanced Processing")
    win.geometry("400x200")
    win.resizable(False, False)

    # 💡 Center the dialog over the main app window
    win.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (win.winfo_width() // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (win.winfo_height() // 2)
    win.geometry(f"+{x}+{y}")

    # Checkbox variables
    audio_var = ctk.BooleanVar(value=config.get("audio_cleanup", True))
    translate_var = ctk.BooleanVar(value=config.get("translate_filenames", False))

    # Audio cleanup checkbox
    audio_check = ctk.CTkCheckBox(win, text="Enable Audio Cleanup", variable=audio_var)
    audio_check.pack(pady=(20, 10))
    ToolTip(win, audio_check, "Applies loudness normalization and denoising.")

    # Filename translation checkbox
    translate_check = ctk.CTkCheckBox(win, text="Translate Filenames to English", variable=translate_var)
    translate_check.pack(pady=(0, 20))
    ToolTip(win, translate_check, "Uses DeepL to rename files when needed.")

    # Save button
    def save():
        config["audio_cleanup"] = audio_var.get()
        config["translate_filenames"] = translate_var.get()
        save_config(config)
        win.destroy()

    save_button = ctk.CTkButton(win, text="Save", command=save, width=140)
    save_button.pack()
    ToolTip(win, save_button, "Save changes to advanced settings.")
