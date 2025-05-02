# engine/deepl_translate.py
import requests
import os
import json

def translate_filename(filename, api_key):
    base = os.path.splitext(os.path.basename(filename))[0]
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "auth_key": api_key,
        "text": base,
        "target_lang": "EN"
    }
    try:
        res = requests.post("https://api-free.deepl.com/v2/translate", headers=headers, data=data)
        res.raise_for_status()
        translated = res.json()["translations"][0]["text"]
        return translated.strip().replace(" ", "_")
    except Exception as e:
        return base  # fallback to original if failed
