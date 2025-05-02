import os
import threading

class QueueRunner:
    def __init__(self, config, file_list_manager, process_file_fn, log_fn=None, status_fn=None, progress_fn=None):
        self.config = config
        self.file_list_manager = file_list_manager
        self.process_file = process_file_fn

        self.log = log_fn or (lambda msg: None)
        self.set_status = status_fn or (lambda msg: None)
        self.set_progress = progress_fn or (lambda pct, msg="": None)

        self.processing_thread = None
        self.stop_flag = False
        self.current_proc = None

    def is_running(self):
        return self.processing_thread and self.processing_thread.is_alive()

    def start(self):
        if self.is_running():
            return
        self.stop_flag = False
        self.processing_thread = threading.Thread(target=self._run_queue)
        self.processing_thread.start()

    def stop(self):
        self.stop_flag = True
        if self.current_proc:
            try:
                self.current_proc.terminate()
                self.log("⚠️ Subprocess forcibly terminated.")
            except Exception as e:
                self.log(f"❌ Failed to terminate subprocess: {e}")
            self.current_proc = None
        self.set_status("❌ Cancelled")
        self.set_progress(0, "Aborted")

    def _run_queue(self):
        while self.file_list_manager.selected_files:
            video = self.file_list_manager.selected_files[0]
            if self.stop_flag:
                self.set_status("❌ Cancelled")
                break

            self.set_status(f"▶ {os.path.basename(video)}")

            def stop_check():
                return self.stop_flag

            def proc_ref(p):
                self.current_proc = p

            self.process_file(
                video_path=video,
                cleanup=self.config.get("audio_cleanup", True),
                api_key=self.config.get("deepl_api_key", ""),
                status_fn=self.set_status,
                progress_fn=self.set_progress,
                log_fn=self.log,
                stop_check=stop_check,
                proc_ref_callback=proc_ref
            )

            self.file_list_manager.selected_files.pop(0)
            self.file_list_manager.refresh()

        if not self.stop_flag:
            self.set_status("🎉 Done")
