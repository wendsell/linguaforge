
# 🧠 LinguaForge

**LinguaForge** is a local video translator and subtitle muxing tool that uses Whisper (via Vulkan GPU acceleration) to automatically transcribe and translate foreign-language videos into English, clean their audio, and output final MKV files with embedded subtitles.

## 🚀 Features

- 🔊 Automatic audio cleanup using FFmpeg (loudnorm)
- 🌍 Multilingual transcription and translation with whisper.cpp (ggml-medium.bin)
- 💨 GPU acceleration via Vulkan (Radeon and AMD-friendly)
- 🧹 Filename and folder sanitization (Unicode-safe)
- 📄 Subtitle generation in `.srt` format with smooth pacing (ideal for spoken/ASMR content)
- 🎥 Subtitle muxing into MKV using mkvmerge
- 📁 Drag-and-drop GUI with queue, per-file logs, and progress indicators
- 🔒 DeepL API key management (hidden after saving)
- 🛑 Stop button for mid-queue cancellation
- 💾 Local-only, offline-capable (no cloud dependencies)

## 📦 How It Works

1. Drop in one or more video files into the GUI.
2. The app cleans the audio and converts it to mono 16KHz WAV.
3. It passes the audio through Whisper CLI with translation enabled.
4. It muxes the resulting `.srt` into an MKV using mkvmerge.
5. Clean folders remain — logs, translated MKVs, and nothing else.

## 📄 License

LinguaForge is licensed under the [GNU General Public License v3.0](LICENSE).  
See [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) for attributions.
