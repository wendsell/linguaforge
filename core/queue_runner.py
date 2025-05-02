import os
import time
import threading

class QueueRunner:
    def __init__(self, config, file_list_manager, processor_fn, logger_fn, status_fn, progress_fn, eta_fn):
        self.config = config
        self.file_list = file_list_manager
        self.processor = processor_fn
        self.logger = logger_fn
        self.status = status_fn
        self.progress = progress_fn
        self.eta = eta_fn
        self.thread = None
        self.stop_flag = False
        self.current_proc = None

    def is_running(self):
        return self.thread and self.thread.is_alive()

    def start(self):
        if self.is_running():
            return
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.stop_flag = True
        if self.current_proc:
            try:
                self.current_proc.terminate()
                self.logger("⛔ Subprocess terminated")
            except Exception as e:
                self.logger(f"❌ Failed to terminate: {e}")
        self.current_proc = None

    def _run(self):
        self.stop_flag = False
        while not self.stop_flag:
            video = self.file_list.pop_next()
            if not video:
                break
            self.status(f"▶ {os.path.basename(video)}")

            def stop_check():
                return self.stop_flag

            def subprocess_ref(p):
                self.current_proc = p

            start_time = time.time()

            self.processor(
                video_path=video,
                cleanup=self.config["audio_cleanup"],
                api_key=self.config["deepl_api_key"],
                status_fn=self.status,
                progress_fn=self.progress,
                log_fn=self.logger,
                stop_check=stop_check,
                proc_ref_callback=subprocess_ref
            )

            elapsed = time.time() - start_time
            self.eta(None)

            if self.stop_flag:
                self.status("❌ Cancelled")
                self.progress(0, "Aborted")
                return

            # Post-job cleanup
            if self.config.get("move_processed_to_archive"):
                try:
                    os.makedirs("archive", exist_ok=True)
                    base = os.path.basename(video)
                    os.rename(video, os.path.join("archive", base))
                    self.logger(f"📦 Archived: {base}")
                except Exception as e:
                    self.logger(f"⚠️ Archive failed: {e}")
            elif self.config.get("delete_original_after_process"):
                try:
                    os.remove(video)
                    self.logger(f"🗑️ Deleted: {os.path.basename(video)}")
                except Exception as e:
                    self.logger(f"⚠️ Delete failed: {e}")

        self.status("🎉 Done")
