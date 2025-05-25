import logging
import os
import platform
from datetime import datetime
import tempfile
TEMP_DIR = os.getenv('TEMP') or os.getenv('TMP') or tempfile.gettempdir()

# Внешний вид и тема
APPEARANCE_MODE = "light"  # "light" | "dark" | "system"
COLOR_THEME = "blue"       # "blue" | "green" | "dark-blue"

# Информация о продукте
PROGRAM_NAME = "KassaWrapper"
ARCHIVE_NAME = "kassawrapper.zip"
VERSION = "1.0.0"

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
LOGO_PATH = os.path.normpath(os.path.join(PROJECT_ROOT, 'assets', 'icons', 'logo-juie.ico'))
SPLASH_IMAGE = os.path.normpath(os.path.join(PROJECT_ROOT, 'assets', 'images', 'logo-juie.png'))
QR_IMAGE = os.path.normpath(os.path.join(PROJECT_ROOT, 'assets', 'images', 'qr_support.png'))

# Локализация
LOCALIZATION_DIR = os.path.normpath(os.path.join(PROJECT_ROOT, 'localization'))
SUPPORTED_LANGUAGES = ['ru', 'kz', 'en']
DEFAULT_LANGUAGE = 'ru'
LOCALE_FILES = {
    lang: os.path.normpath(os.path.join(LOCALIZATION_DIR, f"{lang}.txt"))
    for lang in SUPPORTED_LANGUAGES
}

# Файл лицензионного соглашения
LICENSE_FILE = os.path.normpath(os.path.join(PROJECT_ROOT, 'license.txt'))

# Функции для работы с локализацией
def get_locale_file(language: str = None) -> str:
    lang = language or DEFAULT_LANGUAGE
    path = LOCALE_FILES.get(lang, LOCALE_FILES[DEFAULT_LANGUAGE])
    return path if os.path.exists(path) else LOCALE_FILES[DEFAULT_LANGUAGE]


def load_localization(language: str = None) -> dict:
    file_path = get_locale_file(language)
    translations = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, val = line.split('=', 1)
                translations[key.strip()] = val.strip()
    except Exception:
        pass
    return translations

# Установка
MIN_FREE_SPACE_MB = 100  # минимальный размер свободного места в МБ

# Логи
TEMP_DIR = os.getenv('TEMP') or os.getenv('TMP') or PROJECT_ROOT
LOG_FILE = os.path.normpath(os.path.join(TEMP_DIR, 'install_log.txt'))

# Системная информация
SYSTEM_INFO = {
    'os': platform.system(),
    'release': platform.release(),
    'arch': platform.architecture()[0],
    'user': os.environ.get('USERNAME', 'unknown'),
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}



def get_log_path() -> str:
    dir_ = os.path.dirname(LOG_FILE)
    if not os.path.exists(dir_):
        try:
            os.makedirs(dir_, exist_ok=True)
        except OSError as e:
            logging.error(f"Не удалось создать директорию для логов: {e}")
            raise
    return LOG_FILE

def get_install_path(drive_letter: str = 'C') -> str:
    raw = os.path.join(f"{drive_letter}:/", "Program Files", PROGRAM_NAME)
    return os.path.normpath(raw)
