import customtkinter as ctk

class AdvancedProcessingDialog:
    def __init__(self, parent, config, save_config_fn, is_running):
        self.config = config
        self.save_config = save_config_fn
        self.is_running = is_running

        self.win = ctk.CTkToplevel(parent)
        self.win.title("Advanced Processing")
        self.win.geometry("400x200")
        self.win.transient(parent)
        self.win.grab_set()

        self.cleanup_var = ctk.BooleanVar(value=self.config.get("audio_cleanup", True))
        self.translate_var = ctk.BooleanVar(value=self.config.get("translate_filenames", False))

        cleanup_cb = ctk.CTkCheckBox(
            self.win,
            text="Enable Audio Cleanup",
            variable=self.cleanup_var,
            command=self.toggle_audio_cleanup
        )
        cleanup_cb.pack(pady=(30, 10))

        translate_cb = ctk.CTkCheckBox(
            self.win,
            text="Translate Filenames",
            variable=self.translate_var,
            command=self.toggle_translate_filenames
        )
        translate_cb.pack(pady=10)

    def toggle_audio_cleanup(self):
        self.config["audio_cleanup"] = self.cleanup_var.get()
        self.save_config(self.config)

    def toggle_translate_filenames(self):
        self.config["translate_filenames"] = self.translate_var.get()
        self.save_config(self.config)
