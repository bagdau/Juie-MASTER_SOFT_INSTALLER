import customtkinter as ctk
import threading
import time
import os
from PIL import Image, ImageTk, UnidentifiedImageError
from config.settings import SPLASH_IMAGE
from installer_core.installer import ProgressManager

class SplashScreen(ctk.CTkToplevel):
    """
    Анимированный splash-скрин перед началом установки.
    Плавная индикация загрузки и проверка среды.
    """
    def __init__(self, master=None, callback=None):
        super().__init__(master)
        self.callback = callback
        self.overrideredirect(True)
        self.title("")
        width, height = 600, 400
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Splash image or fallback text
        if os.path.exists(SPLASH_IMAGE):
            try:
                img = Image.open(SPLASH_IMAGE)
                img = img.convert("RGBA")
                img = img.resize((300, 205), Image.LANCZOS)
                self._photo = ImageTk.PhotoImage(img)
                ctk.CTkLabel(self, image=self._photo, text="").pack(pady=(20, 10))
            except UnidentifiedImageError:
                ctk.CTkLabel(self, text="Загрузка...", font=("Segoe UI", 20, "bold")).pack(pady=60)
        else:
            ctk.CTkLabel(self, text="Загрузка...", font=("Segoe UI", 20, "bold")).pack(pady=60)

        # Progress bar and status
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=(10, 5))

        self.status = ctk.CTkLabel(self, text="Подготовка...")
        self.status.pack(pady=(0, 20))

        # Prevent closing
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # Start animation
        self.after(100, self.start_loading)

    def start_loading(self):
        thread = threading.Thread(target=self._load_sequence, daemon=True)
        thread.start()

    def _load_sequence(self):
        pm = ProgressManager(self.progress, self.status)
        pm.run_sequence([
            ("Инициализация компонентов...", 0.3, 0.5),
            ("Загрузка UI-модулей...", 0.7, 0.7),
            ("Подготовка установщика...", 1.0, 0.5),
        ])
        time.sleep(0.3)
        self.after(0, self._complete)

    def _complete(self):
        self.destroy()
        if callable(self.callback):
            self.callback()
