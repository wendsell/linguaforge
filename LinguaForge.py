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

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

config = load_config()

# Ensure all expected config keys exist
for key in DEFAULT_CONFIG:
    if key not in config:
        config[key] = DEFAULT_CONFIG[key]

# Apply theme and window size
ctk.set_appearance_mode(config["theme"])
app_width = config.get("window_width", 920)
app_height = config.get("window_height", 820)

ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("LinguaForge")
app.geometry(f"{app_width}x{app_height}")
app.resizable(False, False)

# === LANG FLAG ===
def get_flag_emoji(lang_code):
    flags = {
        "en": ("🇺🇸", "English"),
        "de": ("🇩🇪", "German"),
        "fr": ("🇫🇷", "French"),
        "es": ("🇪🇸", "Spanish"),
        "it": ("🇮🇹", "Italian"),
        "pt": ("🇵🇹", "Portuguese"),
        "ja": ("🇯🇵", "Japanese"),
        "ko": ("🇰🇷", "Korean"),
        "zh": ("🇨🇳", "Chinese"),
        "ru": ("🇷🇺", "Russian")
    }
    return flags.get(lang_code[:2], ("🏳️", "Unknown"))

selected_files = []
file_widgets = []
selected_widget_index = None
processing_thread = None
stop_flag = False
current_proc = None

# === STYLING ===
BG_CARD = "#ffffff"
BTN_COLOR = "#4f6cf7"
BTN_HOVER = "#3d55c3"
HIGHLIGHT = "#e0e7ff"
LIST_BG = "#f7f9fb"
LOG_BG = "#f1f5f9"
TEXT_COLOR = "#1f2937"

btn_style = {
    "fg_color": BTN_COLOR,
    "hover_color": BTN_HOVER,
    "corner_radius": 10,
    "text_color": "white",
    "font": ("Segoe UI Semibold", 13)
}
frame_style = {"fg_color": BG_CARD, "corner_radius": 10}

# === DIALOGS ===
def open_audio_options():
    win = ctk.CTkToplevel(app)
    win.transient(app)
    win.grab_set()
    win.update_idletasks()
    x = app.winfo_x() + 100
    y = app.winfo_y() + 100
    win.geometry(f"350x150+{x}+{y}")
    win.title("Advanced Processing")
    win.geometry("350x150")
    win.resizable(False, False)
    ctk.CTkCheckBox(win, text="Enable Audio Cleanup", command=toggle_audio_cleanup,
                    variable=ctk.StringVar(value=str(config["audio_cleanup"]))).pack(pady=10)
    ctk.CTkCheckBox(win, text="Translate Filenames", command=toggle_translate_filenames,
                    variable=ctk.StringVar(value=str(config["translate_filenames"]))).pack(pady=10)

def open_preferences():
    win = ctk.CTkToplevel(app)
    win.transient(app)
    win.grab_set()
    win.update_idletasks()
    x = app.winfo_x() + 120
    y = app.winfo_y() + 120
    win.geometry(f"400x200+{x}+{y}")
    win.title("Preferences")
    win.geometry("400x200")
    win.resizable(False, False)

    ctk.CTkLabel(win, text="DeepL API Key:").pack(pady=(20, 5))
    api_field = ctk.CTkEntry(win, width=300)
    api_field.insert(0, config["deepl_api_key"])
    api_field.pack()

    def save():
        config["deepl_api_key"] = api_field.get()
        save_config(config)
        win.destroy()

    ctk.CTkButton(win, text="Save", command=save, **btn_style).pack(pady=20)

# === FILE LIST ===
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
        label = ctk.CTkLabel(file_list_frame, text=display_name, anchor="w", width=580, height=30, text_color=TEXT_COLOR)
        label.pack(fill="x", padx=5, pady=2)
        label.configure(cursor="hand2")
        label.bind("<Enter>", lambda e, w=label: w.configure(fg_color=HIGHLIGHT))
        label.bind("<Leave>", lambda e, w=label: w.configure(fg_color="transparent" if file_widgets.index(w) != selected_widget_index else HIGHLIGHT))
        label.bind("<Button-1>", lambda e, idx=i: select_file_widget(idx))
        file_widgets.append(label)

def select_file_widget(index):
    global selected_widget_index
    selected_widget_index = index
    for i, w in enumerate(file_widgets):
        w.configure(fg_color=HIGHLIGHT if i == index else "transparent")

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

# === PROCESSING ===
def update_status(text):
    if "Detected language:" in text:
        parts = text.split(":")
        lang = parts[-1].strip().lower()
        flag, langname = get_flag_emoji(lang)
        language_flag_label.configure(text=f"{flag} {langname}")
    status_label.configure(text=text)

def update_progress(percent, step=""):
    if percent == 0:
        progress_bar.set(0)
    else:
        progress_bar.set(percent / 100)
    progress_label.configure(text=f"{percent:.0f}% - {step}")

def log_to_gui(msg):
    log_output.configure(state="normal")
    log_output.insert("end", msg + "\n")
    log_output.see("end")
    log_output.configure(state="disabled")

def run_queue():
    global stop_flag, current_proc
    stop_flag = False
    for video in selected_files.copy():
        if stop_flag:
            update_status("❌ Cancelled")
            progress_bar.set(0)
            progress_label.configure(text="Aborted")
            status_label.configure(text="❌ Aborted")
            break
        update_status(f"▶ {os.path.basename(video)}")

        def stop_check(): return stop_flag
        def subprocess_ref(proc): global current_proc; current_proc = proc

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
    progress_bar.set(0)
    progress_label.configure(text="0%")
    update_status("🎉 Done")

def start_processing():
    global processing_thread
    if processing_thread and processing_thread.is_alive(): return
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

def toggle_audio_cleanup():
    config["audio_cleanup"] = cleanup_checkbox.get()
    save_config(config)

def toggle_translate_filenames():
    config["translate_filenames"] = translate_checkbox.get()
    save_config(config)



# === UI LAYOUT ===
main_frame = ctk.CTkFrame(app, fg_color="#f9fafb")
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

file_section = ctk.CTkFrame(main_frame, fg_color=LIST_BG, corner_radius=16)
file_section.pack(fill="x", pady=10, padx=10)

file_list_column = ctk.CTkFrame(file_section, fg_color=LIST_BG, corner_radius=12)
file_list_column.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

file_controls_column = ctk.CTkFrame(file_section, fg_color=BG_CARD, corner_radius=12)
file_controls_column.pack(side="right", fill="y", padx=(0, 10), pady=10)

file_list_scroll = ctk.CTkScrollableFrame(file_list_column, fg_color=LIST_BG, width=600, height=200, corner_radius=0)
file_list_scroll.pack(fill="both", expand=True)
file_list_frame = file_list_scroll

ctk.CTkButton(file_controls_column, text="📂 Add Files", command=browse_files, **btn_style).pack(fill="x", padx=10, pady=5)
ctk.CTkButton(file_controls_column, text="🗑 Remove Selected", command=remove_selected, **btn_style).pack(fill="x", padx=10, pady=5)
ctk.CTkButton(file_controls_column, text="❌ Clear List", command=clear_files, **btn_style).pack(fill="x", padx=10, pady=5)
ctk.CTkButton(file_controls_column, text="⚙️ Advanced Processing", command=open_audio_options, **btn_style).pack(fill="x", padx=10, pady=5)
ctk.CTkButton(file_controls_column, text="🔧 Preferences", command=open_preferences, **btn_style).pack(fill="x", padx=10, pady=5)

run_controls = ctk.CTkFrame(main_frame, fg_color="#e2e8f0", corner_radius=16)
run_controls.pack(pady=10, padx=10)
ctk.CTkButton(run_controls, text="▶ Start", command=start_processing, width=120, **btn_style).pack(side="left", padx=10)
ctk.CTkButton(run_controls, text="⛔ Stop", command=stop_processing, width=120, **btn_style).pack(side="left", padx=10)

progress_frame = ctk.CTkFrame(main_frame, fg_color="#f1f5f9", corner_radius=16)
progress_frame.pack(fill="x", padx=10, pady=(5, 10))
progress_bar = ctk.CTkProgressBar(progress_frame, height=20, mode="determinate")
progress_bar.set(0)
progress_bar.pack(fill="x", pady=(10, 5), padx=10)





progress_label = ctk.CTkLabel(progress_frame, text="0%", font=("Segoe UI", 14))

# Flag display for detected language
language_flag_label = ctk.CTkLabel(progress_frame, text="", font=("Segoe UI", 18), text_color="#4b5563")
language_flag_label.pack(pady=(5, 5))
progress_label.pack()
status_label = ctk.CTkLabel(progress_frame, text="Idle", font=("Segoe UI", 14))
status_label.pack(pady=(2, 10))




log_frame = ctk.CTkFrame(main_frame, fg_color="#e5e7eb", corner_radius=16)
log_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)
log_output = ctk.CTkTextbox(log_frame, height=250)
log_output.pack(fill="both", expand=True, padx=10, pady=10)
log_output.configure(state="disabled")

app.mainloop()
