# engine/logger.py — GUI-Aware Logger

def setup_logger(log_fn):
    """Set up a basic logger that logs via provided callback."""
    def log(msg):
        log_fn(msg + '\n')
    return log

def open_log(path):
    return open(path, "w", encoding="utf-8")
