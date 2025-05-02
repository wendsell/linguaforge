import os
import shutil

# === CONFIG ===
LEGACY_PATHS = [
    "built-srt",
    "translated-output",
    "banner.png",
    ".gitattributes"
]
STAGING_DIRS = [
    "dialogs",
    "theme",
    "assets/icons"
]
MODULE_TEMPLATES = {
    "dialogs/preferences.py": '''
import customtkinter as ctk

def open_preferences_dialog(parent, config, save_config_fn):
    win = ctk.CTkToplevel(parent)
    win.title("Preferences")
    win.geometry("400x200")
    win.resizable(False, False)

    ctk.CTkLabel(win, text="DeepL API Key:").pack(pady=(20, 5))
    api_field = ctk.CTkEntry(win, width=300)
    api_field.insert(0, config.get("deepl_api_key", ""))
    api_field.pack()

    def save():
        config["deepl_api_key"] = api_field.get()
        save_config_fn(config)
        win.destroy()

    ctk.CTkButton(win, text="Save", command=save).pack(pady=20)
''',

    "dialogs/advanced.py": '''
import customtkinter as ctk

def open_advanced_processing(parent, config, save_config_fn):
    win = ctk.CTkToplevel(parent)
    win.title("Advanced Processing")
    win.geometry("300x150")
    win.resizable(False, False)

    cleanup_var = ctk.BooleanVar(value=config.get("audio_cleanup", True))
    translate_var = ctk.BooleanVar(value=config.get("translate_filenames", False))

    cleanup_box = ctk.CTkCheckBox(win, text="Enable Audio Cleanup", variable=cleanup_var)
    translate_box = ctk.CTkCheckBox(win, text="Translate Filenames", variable=translate_var)

    cleanup_box.pack(pady=10)
    translate_box.pack(pady=10)

    def save():
        config["audio_cleanup"] = cleanup_var.get()
        config["translate_filenames"] = translate_var.get()
        save_config_fn(config)
        win.destroy()

    ctk.CTkButton(win, text="Save", command=save).pack(pady=10)
''',

    "theme/manager.py": '''
import customtkinter as ctk

def apply_theme(mode):
    if mode in ["Light", "Dark", "System"]:
        ctk.set_appearance_mode(mode)
    else:
        print(f"Unsupported theme: {mode}")
'''
}


# === EXECUTION ===

# 1. Backup
os.makedirs("backup_legacy", exist_ok=True)
for item in LEGACY_PATHS:
    if os.path.exists(item):
        shutil.move(item, os.path.join("backup_legacy", os.path.basename(item)))
        print(f"Moved {item} to backup_legacy/")

# 2. Create missing folders
for path in STAGING_DIRS:
    os.makedirs(path, exist_ok=True)
    print(f"Ensured folder exists: {path}/")

# 3. Write module templates
for filepath, content in MODULE_TEMPLATES.items():
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
            print(f"Created module stub: {filepath}")

print("\n✅ Cleanup complete. Your project is now tidy and modular-ready!")
