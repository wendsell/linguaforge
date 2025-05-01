# LinguaForge

**LinguaForge** is a desktop tool that automatically transcribes and translates videos into subtitle files (SRT), then muxes them into the original video. It’s designed to work offline using OpenAI Whisper, FFmpeg, and MKVToolNix — fully GPU-accelerated and optimized for AMD Vulkan-based systems (like the RX 7900 XT).

## Features

- 🎥 Drag-and-drop or batch load videos
- 🧼 Optional audio cleanup (via FFmpeg)
- 🌍 Auto language detection and translation to English
- 📜 Subtitle generation in `.srt` format
- 🧠 GPU-accelerated Whisper translation (via Vulkan)
- 🎞️ Mux subtitles directly into `.mkv` files
- 🗂️ Organized folder structure for input/output/logs
- 🔑 DeepL API key support to translate filenames (not content)
- 📉 Real-time logs and progress bar during processing
- ❌ Cancel button to stop processing queue
- ✅ Automatic cleanup of temp files
- 🔒 Saved config with masked API key

## Folder Structure

```plaintext
bin/                # whisper-cli, ffmpeg, mkvmerge, etc.
built-srt/          # temporary subtitles
engine/             # core processor and helpers
input/              # put your source videos here
logs/               # logs per run
model/              # your whisper model (.bin)
temp/               # audio/intermediate files
translated-output/  # final videos with embedded subtitles
theme/              # UI styling
LinguaForge.py      # main script
```

## Requirements
- Python 3.10 or newer
- Vulkan-compatible GPU (AMD RDNA2/3 or NVIDIA)
- FFmpeg, MKVToolNix, and whisper-cli in the `bin` folder

Install dependencies:
```bash
pip install -r requirements.txt
```

## License
This project is licensed under the [GNU GPLv3 License](LICENSE).

## Attribution
See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for included tools and their licenses.

---

**Made for local nerds who want subtitles done fast, clean, and offline.**
