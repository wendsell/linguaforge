# engine/core.py — Environment and Config Utilities
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

FOLDERS = {
    "input": os.path.join(ROOT, "input"),
    "temp": os.path.join(ROOT, "temp"),
    "output": os.path.join(ROOT, "translated-output"),
    "srt": os.path.join(ROOT, "built-srt"),
    "logs": os.path.join(ROOT, "logs"),
    "bin": os.path.join(ROOT, "bin"),
    "model": os.path.join(ROOT, "model")
}

CONFIG_PATH = os.path.join(ROOT, "config.json")

DEFAULT_CONFIG = {
    "deepl_api_key": "",
    "enable_audio_cleanup": True,
    "translate_filenames": True
}

def setup_environment():
    for folder in FOLDERS.values():
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def sanitize_filename(name):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

def get_paths_for_video(filename):
    from os.path import join, basename, splitext
    name = splitext(basename(filename))[0]
    safe = sanitize_filename(name)
    return {
        "wav": join(FOLDERS["temp"], f"{safe}.wav"),
        "srt": join(FOLDERS["srt"], f"{safe}.srt"),
        "output": join(FOLDERS["output"], f"{safe}_translated.mkv"),
        "log": join(FOLDERS["logs"], f"{safe}.log")
    }
