import os
import customtkinter as ctk
from engine.deepl_translate import translate_filename

class FileListManager:
    def __init__(self, frame, config, log_fn=None):
        self.frame = frame
        self.config = config
        self.selected_files = []
        self.file_widgets = []
        self.selected_index = None
        self.log_fn = log_fn or (lambda msg: None)

    def refresh(self):
        for w in self.file_widgets:
            w.destroy()
        self.file_widgets.clear()

        for i, path in enumerate(self.selected_files):
            name = os.path.basename(path)
            display_name = name

            if self.config.get("translate_filenames") and self.config.get("deepl_api_key"):
                translated = translate_filename(name, self.config["deepl_api_key"])
                display_name = f"{name} ➔ {translated}"

            label = ctk.CTkLabel(
                self.frame,
                text=display_name,
                anchor="w",
                width=580,
                height=32,
                font=("Segoe UI", 12)
            )
            label.pack(fill="x", padx=5, pady=2)
            label.configure(cursor="hand2")
            label.bind("<Button-1>", lambda e, idx=i: self.select(idx))
            self.file_widgets.append(label)

    def select(self, index):
        self.selected_index = index
        for i, w in enumerate(self.file_widgets):
            w.configure(fg_color="#e2e8f0" if i == index else "transparent")

    def add_files(self, filepaths):
        for f in filepaths:
            if f not in self.selected_files:
                self.selected_files.append(f)
        self.refresh()

    def remove_selected(self):
        if self.selected_index is not None and 0 <= self.selected_index < len(self.selected_files):
            removed = self.selected_files.pop(self.selected_index)
            self.selected_index = None
            self.refresh()
            self.log_fn(f"Removed file: {os.path.basename(removed)}")

    def clear(self):
        self.selected_files.clear()
        self.selected_index = None
        self.refresh()
