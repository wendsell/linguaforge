# ui/file_list.py
import os
import json
from tkinter import filedialog
import customtkinter as ctk

QUEUE_FILE = "queued_files.json"

class FileListManager:
    def __init__(self, parent, config, logger_fn=None):
        self.parent = parent
        self.config = config
        self.log = logger_fn or print
        self.selected_files = []
        self.file_widgets = []
        self.selected_widget_index = None
        self.processing = False

        self.reload_queue()

    def reload_queue(self):
        try:
            if os.path.exists(QUEUE_FILE):
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    self.selected_files = json.load(f)
                self.log(f"📂 Reloaded {len(self.selected_files)} queued files.")
        except Exception as e:
            self.log(f"⚠️ Failed to load queue: {e}")
        self.refresh_file_list()

    def persist_queue(self):
        try:
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.selected_files, f, indent=2)
        except Exception as e:
            self.log(f"⚠️ Failed to save queue: {e}")

    def refresh_file_list(self):
        for w in self.file_widgets:
            w.destroy()
        self.file_widgets.clear()

        for i, path in enumerate(self.selected_files):
            display = os.path.basename(path)
            label = ctk.CTkLabel(
                self.parent,
                text=display,
                anchor="w",
                width=580,
                height=30,
                text_color="black",
                font=("Segoe UI", 12),
                fg_color="#ffffff" if i != self.selected_widget_index else "#dbeafe"
            )
            label.pack(fill="x", padx=5, pady=2)
            label.bind("<Button-1>", lambda e, idx=i: self.select_file(idx))
            self.file_widgets.append(label)

    def select_file(self, idx):
        self.selected_widget_index = idx
        self.refresh_file_list()

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4;*.mkv;*.mov")])
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)
        self.persist_queue()
        self.refresh_file_list()

    def remove_selected(self):
        if self.selected_widget_index is not None:
            try:
                removed = self.selected_files.pop(self.selected_widget_index)
                self.log(f"➖ Removed {os.path.basename(removed)}")
                self.selected_widget_index = None
            except IndexError:
                self.log("⚠️ Invalid index")
        self.persist_queue()
        self.refresh_file_list()

    def clear_files(self):
        count = len(self.selected_files)
        self.selected_files.clear()
        self.selected_widget_index = None
        self.persist_queue()
        self.refresh_file_list()
        self.log(f"🧹 Cleared {count} files from queue")

    def mark_complete(self, file_path):
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            self.persist_queue()
            self.refresh_file_list()

    def start_processing(self, status_fn, progress_fn):
        if self.processing:
            return
        self.processing = True

        import threading
        from engine.processor import process_file

        def run():
            for video in self.selected_files.copy():
                if not self.processing:
                    status_fn("❌ Cancelled")
                    break
                status_fn(f"▶ {os.path.basename(video)}")

                def stop_check(): return not self.processing
                def subprocess_ref(proc): self.current_proc = proc

                process_file(
                    video_path=video,
                    cleanup=self.config["audio_cleanup"],
                    api_key=self.config["deepl_api_key"],
                    status_fn=status_fn,
                    progress_fn=progress_fn,
                    log_fn=self.log,
                    stop_check=stop_check,
                    proc_ref_callback=subprocess_ref
                )
                self.mark_complete(video)
            self.processing = False
            status_fn("🎉 Done")

        threading.Thread(target=run, daemon=True).start()

    def stop_processing(self, status_fn, progress_fn):
        self.processing = False
        try:
            self.current_proc.terminate()
            self.log("⚠️ Subprocess forcibly terminated.")
        except Exception:
            pass
        status_fn("❌ Cancelled")
        progress_fn(0, "Aborted")
