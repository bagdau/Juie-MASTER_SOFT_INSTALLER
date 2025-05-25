import logging
import time

class ProgressManager:
    """Управление прогресс-баром и статусом для отображения"""
    def __init__(self, progressbar=None, label=None):
        self.progressbar = progressbar
        self.label = label
        self._running = True

    def stop(self):
        self._running = False

    def set_text(self, text: str):
        if self.label and hasattr(self.label, 'configure'):
            self.label.configure(text=text)
        logging.info(f"STATUS: {text}")

    def set_progress(self, value: float):
        if self.progressbar and hasattr(self.progressbar, 'set'):
            self.progressbar.set(value)

    def run_sequence(self, steps: list):
        for text, target, duration in steps:
            if not self._running:
                break
            self.set_text(text)
            self._animate_to(target, duration)
        self.set_text("✅ Завершено.")

    def _animate_to(self, target: float, duration: float):
        try:
            current = self.progressbar.get()
        except Exception:
            current = 0.0
        steps = 100
        delay = duration / steps if steps else 0.01
        for i in range(steps):
            if not self._running:
                break
            progress = current + (target - current) * (i + 1) / steps
            self.set_progress(progress)
            time.sleep(delay)
