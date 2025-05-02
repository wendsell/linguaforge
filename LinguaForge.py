import customtkinter as ctk
import os
import json
import threading
from tkinter import filedialog
from engine.processor import process_file
from engine.logger import open_log
from engine.deepl_translate import translate_filename

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "deepl_api_key": "",
    "audio_cleanup": True,
    "translate_filenames": False,
    "theme": "Light",
    "window_width": 920,
    "window_height": 820
}

ATTRIBUTIONS = [
    "Heroicons (MIT License) — https://heroicons.com"
]

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

config = load_config()
for key in DEFAULT_CONFIG:
    if key not in config:
        config[key] = DEFAULT_CONFIG[key]

ctk.set_appearance_mode(config["theme"])
app_width = config.get("window_width", 920)
app_height = config.get("window_height", 820)
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry(f"{app_width}x{app_height}")
app.resizable(False, False)
status_text = "Idle"
app.title(f"LinguaForge — {status_text}")

BG_CARD = "#ffffff"
BTN_COLOR = "#a8edea"
BTN_HOVER = "#fed6e3"
HIGHLIGHT = "#f0f4f8"
LIST_BG = "#f9fafb"
LOG_BG = "#f0f4f8"
TEXT_COLOR = "#1e293b"

btn_style = {
    "fg_color": BTN_COLOR,
    "hover_color": BTN_HOVER,
    "corner_radius": 12,
    "text_color": "black",
    "font": ("Segoe UI", 14),
    "anchor": "center",
    "height": 36
}
frame_style = {"fg_color": BG_CARD, "corner_radius": 16}

selected_files = []
file_widgets = []
selected_widget_index = None
processing_thread = None
stop_flag = False
current_proc = None

# === File Handlers ===
def refresh_file_list():
    for w in file_widgets:
        w.destroy()
    file_widgets.clear()
    for i, path in enumerate(selected_files):
        name = os.path.basename(path)
        display_name = name
        if config.get("translate_filenames") and config.get("deepl_api_key"):
            translated = translate_filename(name, config["deepl_api_key"])
            display_name = f"{name} ➔ {translated}"
        label = ctk.CTkLabel(file_list_frame, text=display_name, anchor="w", width=580, height=32, text_color=TEXT_COLOR, font=("Segoe UI", 12))
        label.pack(fill="x", padx=5, pady=2)
        label.configure(cursor="hand2")
        file_widgets.append(label)

def browse_files():
    files = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4;*.mkv;*.mov")])
    for f in files:
        if f not in selected_files:
            selected_files.append(f)
    refresh_file_list()

def clear_files():
    selected_files.clear()
    refresh_file_list()

def remove_selected():
    global selected_widget_index
    if selected_widget_index is not None and 0 <= selected_widget_index < len(selected_files):
        selected_files.pop(selected_widget_index)
        selected_widget_index = None
        refresh_file_list()

# === UI Feedback ===
def update_status(text):
    global status_text
    status_text = text
    app.title(f"LinguaForge — {status_text}")
    status_label.configure(text=text)
    if text.lower() in ["idle", "❌ cancelled", "🎉 done"]:
        progress_frame.pack_forget()
    else:
        progress_frame.pack(fill="x", padx=10, pady=(5, 10))

def update_progress(percent, step=""):
    progress_bar.set(percent / 100)
    progress_label.configure(text=f"{percent:.0f}% - {step}")

def log_to_gui(msg):
    log_output.configure(state="normal")
    log_output.insert("end", msg + "\n")
    log_output.see("end")
    log_output.configure(state="disabled")

# === Processing Thread ===
def run_queue():
    global stop_flag, current_proc
    stop_flag = False
    for video in selected_files.copy():
        if stop_flag:
            update_status("❌ Cancelled")
            break
        update_status(f"▶ {os.path.basename(video)}")

        def stop_check(): return stop_flag
        def subprocess_ref(proc):
            global current_proc
            current_proc = proc

        process_file(
            video_path=video,
            cleanup=config["audio_cleanup"],
            api_key=config["deepl_api_key"],
            status_fn=update_status,
            progress_fn=update_progress,
            log_fn=log_to_gui,
            stop_check=stop_check,
            proc_ref_callback=subprocess_ref
        )

        selected_files.remove(video)
        refresh_file_list()
    update_status("🎉 Done")

def start_processing():
    global processing_thread
    if processing_thread and processing_thread.is_alive():
        return
    processing_thread = threading.Thread(target=run_queue)
    processing_thread.start()

def stop_processing():
    global stop_flag, current_proc
    stop_flag = True
    if current_proc:
        try:
            current_proc.terminate()
            log_to_gui("⚠️ Subprocess forcibly terminated.")
        except Exception as e:
            log_to_gui(f"❌ Failed to terminate subprocess: {e}")
        current_proc = None
    update_status("❌ Cancelled")
    update_progress(0, "Aborted")

# === UI Layout ===
main_frame = ctk.CTkFrame(app)
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

file_section = ctk.CTkFrame(main_frame, fg_color=LIST_BG, corner_radius=16)
file_section.pack(fill="x", pady=10, padx=10)

file_list_column = ctk.CTkFrame(file_section, fg_color=LIST_BG, corner_radius=16)
file_list_column.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

file_controls_column = ctk.CTkFrame(file_section, fg_color=BG_CARD, corner_radius=16)
file_controls_column.pack(side="right", fill="y", padx=(0, 10), pady=10)

file_list_scroll = ctk.CTkScrollableFrame(file_list_column, fg_color=LIST_BG, width=600, height=200, corner_radius=0)
file_list_scroll.pack(fill="both", expand=True)
file_list_frame = file_list_scroll

button_texts = [
    ("➕", "Add Files", browse_files),
    ("➖", "Remove Selected", remove_selected),
    ("🗑️", "Clear List", clear_files),
    ("⚙️", "Advanced Processing", lambda: print("Audio options")),
    ("🔧", "Preferences", lambda: print("Preferences"))
]

for icon, text, cmd in button_texts:
    btn = ctk.CTkButton(file_controls_column, text=f"{icon}  {text}", command=cmd, **btn_style)
    btn.pack(fill="x", padx=10, pady=6)

run_controls = ctk.CTkFrame(main_frame, **frame_style)
run_controls.pack(pady=12, padx=10, anchor="w")
ctk.CTkButton(run_controls, text="▶ Start", command=start_processing, width=120, **btn_style).pack(side="left", padx=10)
ctk.CTkButton(run_controls, text="⛔ Stop", command=stop_processing, width=120, **btn_style).pack(side="left", padx=10)

progress_frame = ctk.CTkFrame(main_frame, **frame_style)
progress_bar = ctk.CTkProgressBar(progress_frame, height=16, corner_radius=10)
progress_bar.pack(fill="x", pady=(10, 5), padx=10)
progress_bar.set(0)
progress_label = ctk.CTkLabel(progress_frame, text="0%", font=("Segoe UI", 12))
progress_label.pack()
status_label = ctk.CTkLabel(progress_frame, text="Idle", font=("Segoe UI", 13, "bold"))
status_label.pack(pady=(2, 10))

log_frame = ctk.CTkFrame(main_frame, fg_color=LOG_BG, corner_radius=16)
log_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)
log_output = ctk.CTkTextbox(log_frame, height=250, font=("Consolas", 11))
log_output.pack(fill="both", expand=True, padx=10, pady=10)
log_output.configure(state="disabled")

update_status("Idle")

app.mainloop()
