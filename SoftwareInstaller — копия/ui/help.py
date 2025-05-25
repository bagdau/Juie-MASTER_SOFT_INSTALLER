import customtkinter as ctk
import os
import webbrowser
from config.settings import PROGRAM_NAME
from tkinter import messagebox

class HelpScreen(ctk.CTkToplevel):
    """
    Окно справки и поддержки.
    Отображает контактные данные, ссылку на документацию и QR-код поддержки.
    """
    def __init__(self, on_close=None):
        super().__init__()
        self.title(f"Справка и поддержка {PROGRAM_NAME}")
        self.geometry("500x400")
        self.resizable(False, False)

        # Заголовок
        ctk.CTkLabel(self, text="Справка и поддержка", font=("Segoe UI", 18, "bold")).pack(pady=(20,10))

        # Контактная информация
        contact_frame = ctk.CTkFrame(self)
        contact_frame.pack(padx=20, pady=(0,10), fill="x")
        ctk.CTkLabel(contact_frame, text="Техническая поддержка:", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        ctk.CTkLabel(contact_frame, text="Email: support@example.com", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(contact_frame, text="Телефон: +7 (700) 123-45-67", font=("Segoe UI", 12)).grid(row=2, column=0, sticky="w")

        # Ссылка на документацию
        def open_docs():
            url = "https://example.com/docs"
            try:
                webbrowser.open(url)
            except Exception:
                messagebox.showerror("Ошибка", f"Не удалось открыть {url}")

        ctk.CTkButton(self, text="Открыть документацию", command=open_docs).pack(pady=(0,20))

        # QR-код поддержки
        img_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'qr_support.png')
        if os.path.exists(img_path):
            from PIL import Image, ImageTk
            img = Image.open(img_path)
            img = img.resize((150,150), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(img)
            qrlabel = ctk.CTkLabel(self, image=photo, text="")
            qrlabel.image = photo
            qrlabel.pack(pady=(0,10))
            ctk.CTkLabel(self, text="Сканируйте QR для чата поддержки", font=("Segoe UI", 12)).pack()

        # Закрыть
        ctk.CTkButton(self, text="Закрыть", command=self._on_close).pack(pady=(20,10))
        self.on_close = on_close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        if self.on_close:
            self.on_close()
        self.destroy()
