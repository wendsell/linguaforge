# LinguaForge.py — Fix Stop, Queue, and API Visibility
import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
from threading import Thread
from engine.processor import process_file
from engine.logger import setup_logger

CONFIG_PATH = "config.json"
stopping = False
processing_thread = None

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {
        "deepL_api_key": "",
        "cleanup_enabled": True,
        "translate_filenames": True
    }

def save_config():
    config["deepL_api_key"] = api_entry.get()
    config["cleanup_enabled"] = cleanup_var.get()
    config["translate_filenames"] = filename_var.get()
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)
    api_entry.config(show="*")

def add_files():
    paths = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.mkv *.mov")])
    for path in paths:
        file_list.insert(tk.END, path)

def remove_selected():
    selected = file_list.curselection()
    for i in reversed(selected):
        file_list.delete(i)

def clear_queue():
    file_list.delete(0, tk.END)

def update_status(text):
    status_label.config(text=text)
    root.update_idletasks()

def update_progress(value, text=""):
    progress["value"] = value
    progress_label.config(text=f"{int(value)}% {text}")
    root.update_idletasks()

def run_queue():
    global stopping, processing_thread
    stopping = False

    files = list(file_list.get(0, tk.END))
    if not files:
        messagebox.showwarning("No Files", "Please add video files to process.")
        return

    api_key = api_entry.get().strip()
    if not api_key:
        messagebox.showwarning("Missing API Key", "Please enter your DeepL API key.")
        return

    start_btn.config(state="disabled")
    clear_btn.config(state="disabled")
    remove_btn.config(state="disabled")
    stop_btn.config(state="normal")
    update_progress(0, "Starting...")
    update_status("Running...")

    def log_to_gui(msg):
        log_output.insert(tk.END, msg)
        log_output.see(tk.END)

    def worker():
        total = len(files)
        for i in range(total):
            if stopping:
                update_status("⛔ Stopped by user")
                break
            current = file_list.get(0)
            update_status(f"Processing file {i + 1} of {total}")
            update_progress((i / total) * 100, "🕐 Extracting audio...")
            process_file(
                video_path=current,
                config=config,
                log_fn=log_to_gui,
                status_fn=update_status,
                progress_fn=update_progress
            )
            file_list.delete(0)

        update_progress(100, "Complete")
        update_status("✅ All done.")
        start_btn.config(state="normal")
        clear_btn.config(state="normal")
        remove_btn.config(state="normal")
        stop_btn.config(state="disabled")

    processing_thread = Thread(target=worker)
    processing_thread.start()

def stop_processing():
    global stopping
    stopping = True

# GUI SETUP
config = load_config()
root = ThemedTk(theme="radiance")
root.title("🧠 LinguaForge — Translate & Subtitle")
root.geometry("850x600")

title = ttk.Label(root, text="🧠 LinguaForge — Translate & Subtitle", font=("Segoe UI", 14, "bold"))
title.pack(pady=5)

file_list = tk.Listbox(root, height=5, selectmode=tk.EXTENDED, font=("Consolas", 10))
file_list.pack(fill=tk.X, padx=10)

btn_frame = ttk.Frame(root)
btn_frame.pack(pady=3)
ttk.Button(btn_frame, text="Add Videos", command=add_files).pack(side=tk.LEFT, padx=5)
remove_btn = ttk.Button(btn_frame, text="Remove Selected", command=remove_selected)
remove_btn.pack(side=tk.LEFT, padx=5)
clear_btn = ttk.Button(btn_frame, text="Clear Queue", command=clear_queue)
clear_btn.pack(side=tk.LEFT)

cleanup_var = tk.BooleanVar(value=config.get("cleanup_enabled", True))
filename_var = tk.BooleanVar(value=config.get("translate_filenames", True))

ttk.Checkbutton(root, text="Enable Audio Cleanup", variable=cleanup_var).pack(anchor="w", padx=12)
ttk.Checkbutton(root, text="Translate Filenames", variable=filename_var).pack(anchor="w", padx=12)

ttk.Label(root, text="DeepL API Key").pack(anchor="w", padx=12)
api_entry = ttk.Entry(root, show="*")
api_entry.pack(fill=tk.X, padx=10)
api_entry.insert(0, config.get("deepL_api_key", ""))

ttk.Button(root, text="💾 Save Config", command=save_config).pack(anchor="e", padx=10, pady=5)

btn_run = ttk.Frame(root)
btn_run.pack(pady=5)
start_btn = ttk.Button(btn_run, text="🛠️ Start Processing", command=run_queue)
start_btn.pack(side=tk.LEFT, padx=5)
stop_btn = ttk.Button(btn_run, text="⛔ Stop", command=stop_processing, state="disabled")
stop_btn.pack(side=tk.LEFT)

status_label = ttk.Label(root, text="Idle", font=("Segoe UI", 10))
status_label.pack()

progress = ttk.Progressbar(root, mode="determinate", maximum=100)
progress.pack(fill=tk.X, padx=10, pady=(2, 0))

progress_label = ttk.Label(root, text="0%", anchor="center")
progress_label.pack()

ttk.Label(root, text="Log Output").pack(anchor="w", padx=10)
log_output = tk.Text(root, height=12, bg="black", fg="lime", font=("Consolas", 9))
log_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

setup_logger(log_output.insert)
root.mainloop()
