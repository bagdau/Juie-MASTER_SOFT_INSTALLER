import os
import logging
from tkinter import messagebox, filedialog
import customtkinter as ctk
from config.settings import PROGRAM_NAME, get_install_path, LOG_FILE


class FinishScreen(ctk.CTkToplevel):
    """
    Финальный экран по завершении установки.
    Показывает путь установки, предлагает запустить программу и открыть папку.
    """
    def __init__(self, on_close, install_path=None):
        super().__init__()
        self.on_close = on_close
        self.install_path = install_path or self._get_install_path_from_log()
        logging.info(f"Install Path: {install_path}")

        self.title("Завершено")
        self.geometry("600x400")
        self.resizable(False, False)

        # Сообщение об успешной установке
        ctk.CTkLabel(
            self,
            text=f"{PROGRAM_NAME} успешно установлен в:\n{self.install_path}",
            font=("Segoe UI", 14),
            justify="center"
        ).pack(pady=(20, 10))

        # Поле для выбора пути установки
        path_frame = ctk.CTkFrame(self)
        path_frame.pack(pady=(10, 20), padx=20, fill="x")

        ctk.CTkLabel(path_frame, text="Папка установки:").pack(side="left", padx=(0, 10))
        self.path_var = ctk.StringVar(value=self.install_path)
        self.path_entry = ctk.CTkEntry(path_frame, width=400, textvariable=self.path_var)
        self.path_entry.pack(side="left", padx=(0, 10))

        browse_btn = ctk.CTkButton(
            path_frame,
            text="Обзор...",
            command=self.browse_folder,
            width=100
        )
        browse_btn.pack(side="left")

        # Кнопки действий
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=(20, 0))

        run_btn = ctk.CTkButton(
            btn_frame,
            text="Запустить программу",
            command=self.run_program,
            width=180
        )
        run_btn.pack(side="left", padx=10)

        open_btn = ctk.CTkButton(
            btn_frame,
            text="Открыть папку установки",
            command=self.open_folder,
            width=180
        )
        open_btn.pack(side="left", padx=10)

        close_btn = ctk.CTkButton(
            self,
            text="Закрыть",
            command=self._on_close
        )
        close_btn.pack(pady=(20, 0))

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def browse_folder(self):
        """Открывает диалог выбора папки."""
        selected = filedialog.askdirectory(initialdir=self.install_path)
        if selected:
            self.path_var.set(selected)
            self.install_path = selected

    def run_program(self):
        """Запускает установленную программу."""
        exe_path = os.path.join(self.install_path, f"{PROGRAM_NAME}.exe")
        if os.path.exists(exe_path):
            try:
                os.startfile(exe_path)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось запустить программу:\n{e}")
        else:
            messagebox.showerror("Ошибка", "Файл программы не найден.")

    def open_folder(self):
        """Открывает папку установки."""
        print(f"Путь к папке установки: {self.install_path}")
        print(f"Существует ли папка: {os.path.exists(self.install_path)}")
        if os.path.exists(self.install_path):
            try:
                os.startfile(self.install_path)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{e}")
        else:
            messagebox.showerror("Ошибка", "Папка установки не найдена.")

    def _on_close(self):
        """Закрывает окно."""
        if callable(self.on_close):
            self.on_close()
        self.destroy()

    def _get_install_path_from_log(self):
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as log:
                    for line in log:
                        if "Install Path:" in line:
                            install_path = line.split(":", 1)[1].strip()
                            if not install_path or install_path.lower() == "none":
                                continue
                            print(f"Путь к папке установки: {install_path}")
                            print(f"Существует ли папка: {os.path.exists(install_path)}")
                            return install_path
            except Exception as e:
                print(f"Ошибка чтения лог-файла: {e}")
        return get_install_path()
