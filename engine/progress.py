# engine/progress.py — Output Parsing for Visual Feedback
import re
import time

_ffmpeg_start = None
_whisper_start = None

ffmpeg_total_seconds = 0
whisper_last_timestamp = 0

def parse_ffmpeg_progress(line, log, update_progress=None):
    global _ffmpeg_start, ffmpeg_total_seconds
    match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
    if match:
        h, m, s = map(float, match.groups())
        current = h * 3600 + m * 60 + s
        if _ffmpeg_start is None:
            _ffmpeg_start = time.time()
        if ffmpeg_total_seconds > 0:
            pct = int((current / ffmpeg_total_seconds) * 100)
            eta = estimate_remaining_time(_ffmpeg_start, pct)
            log(f"[ffmpeg] {pct}% done — ETA {eta}")
            if update_progress:
                update_progress(min(pct, 99))

def parse_whisper_progress(line, log, update_progress=None):
    global _whisper_start, whisper_last_timestamp
    match = re.search(r'\[(\d{2}):(\d{2})\.(\d{2}) -->', line)
    if match:
        m, s, ms = map(int, match.groups())
        current = m * 60 + s + ms / 100
        if _whisper_start is None:
            _whisper_start = time.time()
        whisper_last_timestamp = current
        # Heuristic: assume whisper is 90% done at 21 minutes
        est_total = 21 * 60
        pct = int((current / est_total) * 100)
        eta = estimate_remaining_time(_whisper_start, pct)
        log(f"[whisper] {pct}% — ETA {eta}")
        if update_progress:
            update_progress(min(pct, 99))

def estimate_remaining_time(start_time, percent_complete):
    if percent_complete == 0:
        return "calculating..."
    elapsed = time.time() - start_time
    total_est = elapsed / (percent_complete / 100)
    remaining = int(total_est - elapsed)
    mins, secs = divmod(remaining, 60)
    return f"{mins}m {secs}s"
