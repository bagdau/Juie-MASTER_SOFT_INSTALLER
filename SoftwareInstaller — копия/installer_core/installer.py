import os
import zipfile
import shutil
import time
import logging
import subprocess
from shutil import disk_usage
from config.settings import (
    MIN_FREE_SPACE_MB,
    ARCHIVE_NAME,
    get_log_path,
    PROJECT_ROOT,
    get_install_path
)

# --- pip install pywin32 winshell для работы ярлыков ---
try:
    from win32com.client import Dispatch
    import winshell
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# === НАСТРОЙКИ ===
PROGRAM_NAME = "KassaWrapper"
ARCHIVE_NAME = "kassawrapper.zip"
MIN_FREE_SPACE_MB = 500

def get_log_path():
    return os.path.join(os.getcwd(), "installer.log")

def get_install_path():
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    return os.path.join(pf, PROGRAM_NAME)

PROJECT_ROOT = os.getcwd()

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    filename=get_log_path(),
    filemode='a',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)

class InstallerError(Exception):
    pass

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


class InstallerEngine:
    def _rollback(self):
        """Откат установки: удаляет установленную папку, если что-то пошло не так."""
        try:
            if os.path.exists(self.install_dir):
                shutil.rmtree(self.install_dir)
                logging.info(f"Откат: удалена папка {self.install_dir}")
        except Exception as e:
            logging.error(f"Ошибка при откате установки: {e}")
            
    def __init__(self, archive_path=None, install_dir=None, options=None):
        self.archive_path = archive_path or os.path.join(PROJECT_ROOT, ARCHIVE_NAME)
        self.install_dir = install_dir or get_install_path()
        if not self.install_dir or self.install_dir.lower() == "none":
            self.install_dir = get_install_path()
        self.options = options or {}
        self._steps = []
        self._running = False
        self.exe_path = None
        self._cancelled = False
        self.last_error = None  # <-- для хранения текста последней ошибки

    def install(self, progress_callback=None, silent=False):
        self._running = True
        self._cancelled = False
        self.last_error = None  # сбрасываем ошибку перед стартом
        logging.info(f"Установка: {self.archive_path} -> {self.install_dir}")
        try:
            # Проверка свободного места
            drive = os.path.splitdrive(self.install_dir)[0]
            if not drive:
                self.install_dir = get_install_path()
                drive = os.path.splitdrive(self.install_dir)[0]
            free = disk_usage(drive + os.sep).free
            if free < MIN_FREE_SPACE_MB * 1024 * 1024:
                raise InstallerError(f"Недостаточно места: нужно {MIN_FREE_SPACE_MB} МБ")

            # --- Распаковка архива ---
            if not os.path.exists(self.install_dir):
                os.makedirs(self.install_dir, exist_ok=True)

            with zipfile.ZipFile(self.archive_path, 'r') as zip_ref:
                files = zip_ref.namelist()
                total = len(files)
                for idx, member in enumerate(files, 1):
                    if not self._running:
                        self._cancelled = True
                        logging.info("Установка отменена пользователем.")
                        return False
                    zip_ref.extract(member, self.install_dir)
                    full_path = os.path.join(self.install_dir, member)
                    if progress_callback:
                        progress_callback(idx / total, member, full_path)
                    logging.info(f"Установлен файл: {full_path}")
                    # Сохраняем путь к exe, если нашли
                    if member.lower().endswith(".exe"):
                        self.exe_path = full_path

            if progress_callback:
                progress_callback(1.0, None, None)

            # Создание ярлыка
            self.create_desktop_shortcut()

            return True

        except InstallerError as err:
            self.last_error = str(err)
            logging.error(err)
            self._rollback()
            return False
        except Exception as exc:
            self.last_error = f"{exc}"
            logging.exception(exc)
            self._rollback()
            return False
        finally:
            self._running = False

    


    @property
    def installed_folder(self):
        """Путь к установленной папке"""
        return self.install_dir

    @property
    def installed_exe(self):
        """Путь к EXE-файлу"""
        return self.exe_path

    def show_install_folder(self):
        """Открывает Проводник с установленной папкой"""
        folder = self.installed_folder
        if folder and os.path.exists(folder):
            subprocess.Popen(f'explorer "{folder}"')
            logging.info(f"Показана папка установки: {folder}")
        else:
            logging.warning(f"Папка установки не найдена: {folder}")

    def show_exe_file(self):
        """Выделяет EXE-файл в Проводнике"""
        exe = self.installed_exe
        if exe and os.path.exists(exe):
            subprocess.Popen(f'explorer /select,"{exe}"')
            logging.info(f"Показан EXE-файл: {exe}")
        else:
            logging.warning(f"EXE-файл не найден: {exe}")

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

    def uninstall(self, silent=False):
        logging.info(f"Деинсталляция: {self.install_dir}")
        try:
            if os.path.exists(self.install_dir):
                shutil.rmtree(self.install_dir)
            else:
                logging.info(f"Папка {self.install_dir} уже удалена.")
            return True
        except Exception as e:
            logging.error(f"Ошибка деинсталляции: {e}")
            if not silent:
                raise InstallerError("Не удалось удалить приложение.")
            return False

    def silent_install(self):
        return self.install(silent=True)

    def silent_uninstall(self):
        return self.uninstall(silent=True)

# ======= Пример использования =======
if __name__ == "__main__":
    def progress(p, filename, path):
        if filename and path:
            print(f"[{int(p*100)}%] {filename} -> {path}")
        elif path:
            print(path)
        else:
            print(f"[{int(p*100)}%] Завершено!")

    installer = InstallerEngine()
    ok = installer.install(progress_callback=progress)
    if ok:
        print("Установка завершена.")
        print("Папка:", installer.installed_folder)
        print("EXE:", installer.installed_exe)
        installer.show_install_folder()
        installer.show_exe_file()
    else:
        print("Ошибка установки! См. installer.log")
