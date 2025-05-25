import customtkinter as ctk
import os
from PIL import Image, ImageTk, UnidentifiedImageError
from config.settings import PROGRAM_NAME, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, LOGO_PATH

class WelcomeScreen(ctk.CTkToplevel):
    """
    Приветственный экран мастера установки.
    Отображает логотип, выбор языка и кнопку продолжения.
    """
    def __init__(self, on_continue):
        super().__init__()
        self.on_continue = on_continue

        self.title(f"Вас приветсвует в {PROGRAM_NAME} Installer")
        self.geometry("600x400")
        self.resizable(False, False)

        # Логотип
        logo_frame = ctk.CTkFrame(self)
        logo_frame.pack(pady=(20, 10))
        if os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH)
                img = img.resize((120, 120), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                logo_label = ctk.CTkLabel(logo_frame, image=photo, text="")
                logo_label.image = photo
                logo_label.pack()
            except UnidentifiedImageError:
                ctk.CTkLabel(logo_frame, text=PROGRAM_NAME, font=("Segoe UI", 24, "bold")).pack()
        else:
            ctk.CTkLabel(logo_frame, text=PROGRAM_NAME, font=("Segoe UI", 24, "bold")).pack()

        # Заголовок и описание
        ctk.CTkLabel(self, text=f" Мастер установщик {PROGRAM_NAME}!", 
                     font=("Segoe UI", 18, "bold")).pack(pady=(10,5))
        ctk.CTkLabel(self, text="Нажмите 'Далее' чтобы продолжить установку.", 
                     font=("Segoe UI", 14)).pack(pady=(0,20))

        # Выбор языка (только если поддерживается больше одного языка)
        if len(SUPPORTED_LANGUAGES) > 1:
            lang_frame = ctk.CTkFrame(self)
            lang_frame.pack(pady=(0,20))
            ctk.CTkLabel(lang_frame, text="Язык интерфейса:", font=("Segoe UI", 12)).pack(side="left", padx=(0,10))
            self.lang_var = ctk.StringVar(value=DEFAULT_LANGUAGE)
            self.lang_menu = ctk.CTkOptionMenu(
            lang_frame, variable=self.lang_var, values=SUPPORTED_LANGUAGES,
            command=self.change_language
            )
            self.lang_menu.pack(side="left")

        # Тема (light/dark/system)
        theme_frame = ctk.CTkFrame(self)
        theme_frame.pack(pady=(0,20))
        ctk.CTkLabel(theme_frame, text="Тема оформления:", font=("Segoe UI", 12)).pack(side="left", padx=(0,10))
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame, variable=self.theme_var,
            values=["light","dark","system"], command=ctk.set_appearance_mode
        )
        self.theme_menu.pack(side="left")

        # Кнопка "Далее"
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=(20,10))
        self.continue_btn = ctk.CTkButton(
            button_frame, text="Далее", width=120,
            command=self._on_continue
        )
        self.continue_btn.pack()

        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def change_language(self, lang_code):
        # TODO: применить загрузку локализации по lang_code
        pass

    def _on_continue(self):
        self.destroy()
        if callable(self.on_continue):
            self.on_continue()

    def _on_cancel(self):
        self.destroy()
        ctk.CTk().quit()
