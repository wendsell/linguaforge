# engine/processor.py — Cleanup temp + built-srt
import os
import subprocess
import time
import glob
import shutil
from engine.core import get_paths_for_video, FOLDERS
from engine.logger import open_log

def run_command(cmd, desc, log_fn, status_fn=None, progress_fn=None):
    log_fn("\n▶ " + desc)
    if status_fn:
        status_fn(desc)
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            log_fn(line.strip())
        proc.wait()
        if proc.returncode != 0:
            log_fn(f"❌ Failed: {desc}")
            return False
    except Exception as e:
        log_fn(f"💥 Exception during {desc}: {e}")
        return False
    return True

def find_latest_srt():
    srts = glob.glob(os.path.join(FOLDERS["srt"], "*.srt"))
    if not srts:
        return None
    return max(srts, key=os.path.getmtime)

def process_file(video_path, config, log_fn, status_fn, progress_fn):
    from os.path import join, exists
    paths = get_paths_for_video(video_path)
    os.makedirs(FOLDERS["temp"], exist_ok=True)
    os.makedirs(FOLDERS["srt"], exist_ok=True)
    os.makedirs(FOLDERS["output"], exist_ok=True)

    ffmpeg = join(FOLDERS["bin"], "ffmpeg.exe")
    whisper = join(FOLDERS["bin"], "whisper-cli.exe")
    mkvmerge = join(FOLDERS["bin"], "mkvmerge.exe")
    model = join(FOLDERS["model"], "ggml-medium.bin")

    with open_log(paths["log"]) as logf:
        def logall(msg):
            log_fn(msg + "\n")
            logf.write(msg + "\n")

        # Extract or clean audio
        progress_fn(10, "Extracting audio...")
        if config.get("cleanup_enabled"):
            cmd = [ffmpeg, "-y", "-i", video_path, "-af", "loudnorm", "-ar", "16000", "-ac", "1", paths["wav"]]
        else:
            cmd = [ffmpeg, "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", paths["wav"]]
        if not run_command(cmd, "Preparing audio", logall, status_fn, progress_fn):
            return

        # Whisper translation with natural flowing segments
        progress_fn(40, "Running Whisper translation...")
        whisper_cmd = [
            whisper,
            "--model", model,
            "--file", paths["wav"],
            "--language", "auto",
            "--translate",
            "--output-srt",
            "--output-file", paths["srt"],
            "--temperature", "0",
            "--no-fallback",
            "--suppress-nst",
            "--word-thold", "0.4",
            "--beam-size", "5",
            "--best-of", "5",
            "--max-len", "64"
        ]
        if not run_command(whisper_cmd, "Translating via Whisper", logall, status_fn, progress_fn):
            return

        # Mux subtitles
        srt_path = find_latest_srt()
        if not srt_path or not exists(srt_path):
            logall("❌ No subtitle file created. Skipping mux.")
            return

        progress_fn(90, "Merging subtitles into MKV...")
        mux_cmd = [
            mkvmerge, "-o", paths["output"], video_path,
            "--language", "0:eng", srt_path
        ]
        if not run_command(mux_cmd, "Muxing subtitles", logall, status_fn, progress_fn):
            return

        progress_fn(100, "✅ Complete!")
        logall(f"✅ Done: {os.path.basename(paths['output'])}")

        # Clean up temp and built-srt folders
        try:
            if os.path.exists(FOLDERS["temp"]):
                shutil.rmtree(FOLDERS["temp"])
                os.makedirs(FOLDERS["temp"], exist_ok=True)
                logall("🧹 Temp files cleaned.")
            if os.path.exists(FOLDERS["srt"]):
                for f in glob.glob(os.path.join(FOLDERS["srt"], "*.srt")):
                    os.remove(f)
                logall("🧽 Subtitle files removed from built-srt.")
        except Exception as cleanup_error:
            logall(f"⚠️ Cleanup failed: {cleanup_error}")
