import customtkinter as ctk

class PreferencesDialog:
    def __init__(self, parent, config, save_config_fn, is_running):
        self.config = config
        self.save_config = save_config_fn
        self.is_running = is_running

        self.win = ctk.CTkToplevel(parent)
        self.win.title("Preferences")
        self.win.geometry("400x240")
        self.win.transient(parent)
        self.win.grab_set()

        ctk.CTkLabel(self.win, text="DeepL API Key:").pack(pady=(20, 5))
        self.api_entry = ctk.CTkEntry(self.win, width=300)
        self.api_entry.insert(0, self.config.get("deepl_api_key", ""))
        self.api_entry.pack()

        ctk.CTkLabel(self.win, text="Theme:").pack(pady=(20, 5))
        self.theme_option = ctk.CTkOptionMenu(
            self.win,
            values=["Light", "Dark"],
            command=self.change_theme
        )
        self.theme_option.set(self.config.get("theme", "Light"))
        self.theme_option.pack()

        ctk.CTkButton(self.win, text="Save", command=self.save).pack(pady=20)

    def save(self):
        self.config["deepl_api_key"] = self.api_entry.get()
        self.save_config(self.config)
        self.win.destroy()

    def change_theme(self, new_theme):
        if self.is_running():
            ctk.CTkLabel(self.win, text="⚠️ Can't change theme while running!", text_color="red").pack()
            return
        ctk.set_appearance_mode(new_theme)
        self.config["theme"] = new_theme
        self.save_config(self.config)
