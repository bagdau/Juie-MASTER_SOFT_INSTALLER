import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk, UnidentifiedImageError
import logging
try:
    import winshell
    from win32com.client import Dispatch
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
# === Настройки и константы ===
PROGRAM_NAME = "KassaWrapper"
LOGO_PATH = "logo-juie.png"
ARCHIVE_NAME = "kassawrapper.zip"

# ВАЖНО! ui/install.py лежит в SoftwareInstaller/ui/
# Архив в SoftwareInstaller/builds/
# Нужно подняться на уровень выше!
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
archive_path = os.path.join(PROJECT_ROOT, "builds", ARCHIVE_NAME)

print("Путь к архиву:", archive_path)
MIN_FREE_SPACE_MB = 500

def get_install_path():
    return os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), PROGRAM_NAME)

def disk_usage(path):
    import shutil
    return shutil.disk_usage(path)

# === Импорт движка установки ===
from installer_core.installer import InstallerEngine

class InstallPage(ctk.CTkToplevel):
    def __init__(self, on_success, on_cancel, options=None):
        super().__init__()
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.options = options or {}

        self.title(f"Установка {PROGRAM_NAME}")
        self.geometry("750x600")
        self.resizable(False, False)

        # --- Логотип ---
        logo_frame = ctk.CTkFrame(self)
        logo_frame.pack(pady=(20, 10))
        if os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH)
                img = img.resize((80, 80), Image.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(img)
                ctk.CTkLabel(logo_frame, image=self._logo_img, text="").pack()
            except UnidentifiedImageError:
                ctk.CTkLabel(logo_frame, text=PROGRAM_NAME, font=("Segoe UI", 24, "bold")).pack()
        else:
            ctk.CTkLabel(logo_frame, text=PROGRAM_NAME, font=("Segoe UI", 24, "bold")).pack()



        # --- Прогресс-бар ---
        self.progress_bar = ctk.CTkProgressBar(self, width=600)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(10, 5))

        # --- Статус установки ---
        self.status_label = ctk.CTkLabel(self, text="Готов к установке.")
        self.status_label.pack(pady=(0, 20))

        # --- Выбор папки установки ---
        path_frame = ctk.CTkFrame(self)
        path_frame.pack(pady=(0, 20), padx=20)
        ctk.CTkLabel(path_frame, text="Папка установки:").pack(side="left", padx=(0, 10))
        default_path = get_install_path()
        self.path_var = ctk.StringVar(value=default_path)
        self.path_entry = ctk.CTkEntry(path_frame, width=500, textvariable=self.path_var)
        self.path_entry.pack(side="left", padx=(0, 10))
        browse_btn = ctk.CTkButton(path_frame, text="Обзор...", width=100, command=self.browse_folder)
        browse_btn.pack(side="left")

        # --- Кнопки действий ---
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=(20, 0))
        self.install_btn = ctk.CTkButton(btn_frame, text="Установить", width=150, command=self.start_install)
        self.install_btn.pack(side="left", padx=10)
        self.cancel_btn = ctk.CTkButton(btn_frame, text="Отмена", width=150, command=self.cancel_install)
        self.cancel_btn.pack(side="left")

        # --- Мини-терминал ---
        terminal_frame = ctk.CTkFrame(self)
        terminal_frame.pack(pady=(20, 10), padx=20, fill="both", expand=True)
        self.terminal = ScrolledText(terminal_frame, height=12, state="disabled", wrap="word")
        self.terminal.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.cancel_install)

    def browse_folder(self):
        selected = filedialog.askdirectory(initialdir=self.path_var.get())
        if selected:
            self.path_var.set(selected)

    def start_install(self):
        install_dir = self.path_var.get().strip()
        drive = os.path.splitdrive(install_dir)[0]
        if not drive or not os.path.exists(drive + os.sep):
            messagebox.showerror("Ошибка", f"Диск {drive} не найден.")
            return
        try:
            free_mb = disk_usage(drive + os.sep).free / (1024 * 1024)
        except Exception:
            free_mb = 0
        if free_mb < MIN_FREE_SPACE_MB:
            messagebox.showerror(
                "Ошибка",
                f"На диске {drive} недостаточно места: {int(free_mb)} МБ, требуется {MIN_FREE_SPACE_MB} МБ."
            )
            return

        self.install_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")
        self.status_label.configure(text="Подготовка...")
        self.progress_bar.set(0)
        self._clear_terminal()

        # Используй именно ТОТ archive_path, который определён ГЛОБАЛЬНО в файле!
        if not os.path.exists(archive_path):
            self._update_terminal(f"Ошибка: архив не найден: {archive_path}")
            messagebox.showerror("Ошибка", f"Архив не найден: {archive_path}")
            self.install_btn.configure(state="normal")
            self.cancel_btn.configure(state="normal")
            return

        self.engine = InstallerEngine(
            archive_path=archive_path,
            install_dir=install_dir,
            options=self.options
        )
        thread = threading.Thread(target=self._run_install, daemon=True)
        thread.start()

    def _run_install(self):
        try:
            def progress_callback(percent, filename=None, full_path=None):
                self.after(0, self._update_progress, percent, filename, full_path)

            success = self.engine.install(progress_callback=progress_callback)
            if getattr(self.engine, '_cancelled', False):  # Добавим такой флаг
                self.after(0, self._install_cancel)
            elif success:
                self.after(0, self._install_success)
            else:
                self.after(0, self._install_error, "Неизвестная ошибка установки")
        except Exception as e:
            self.after(0, self._install_error, e)


    def create_desktop_shortcut(self):
        """Создаёт ярлык на рабочем столе для установленного EXE."""
        if not HAS_WIN32:
            logging.warning("pywin32 или winshell не установлены, ярлык не будет создан.")
            return
        exe = os.path.join(self.install_dir, f"{PROGRAM_NAME}.exe")
        if not os.path.exists(exe):
            logging.warning(f"EXE-файл не найден для ярлыка: {exe}")
            return
        try:
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{PROGRAM_NAME}.lnk")
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = exe
            shortcut.WorkingDirectory = self.install_dir
            shortcut.IconLocation = exe
            shortcut.Description = f"Запуск {PROGRAM_NAME}"
            shortcut.Save()
            logging.info(f"Создан ярлык: {shortcut_path}")
        except Exception as e:
            logging.error(f"Ошибка создания ярлыка: {e}")


    def _update_progress(self, percent, filename, full_path):
        self.progress_bar.set(percent)
        if filename and full_path:
            msg = f"Устанавливается: {filename}"
            self.status_label.configure(text=msg)
            self._update_terminal(f"Установлен файл: {full_path}")
        elif full_path and not filename:
            # Например, создание папки
            self._update_terminal(full_path)
        elif not filename and not full_path:
            self.status_label.configure(text=f"{int(percent * 100)}%")
        if percent >= 1.0:
            self.status_label.configure(text="Установка завершена.")

    def _update_terminal(self, message):
        self.terminal.configure(state="normal")
        self.terminal.insert("end", message + "\n")
        self.terminal.configure(state="disabled")
        self.terminal.see("end")

    def _clear_terminal(self):
        self.terminal.configure(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.configure(state="disabled")

    def _install_success(self):
        self.status_label.configure(text="Установка завершена.")
        self._update_terminal("Установка завершена.")
        self.after(800, self.on_success)

    def _install_cancel(self):
        messagebox.showinfo("Отмена", "Установка отменена или прервана.")
        self._update_terminal("Установка отменена или прервана.")
        self.after(300, self.on_cancel)

    def _install_error(self, e):
        messagebox.showerror("Ошибка", f"Непредвиденная ошибка: {e}")
        self._update_terminal(f"Ошибка: {e}")
        self.after(400, self.on_cancel)

    def cancel_install(self):
        if hasattr(self, 'engine') and getattr(self.engine, '_running', False):
            self.engine._running = False
            self.engine._cancelled = True
        else:
            self.on_cancel()

