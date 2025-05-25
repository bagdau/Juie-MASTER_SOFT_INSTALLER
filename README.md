# Juie-MASTER_SOFT_INSTALLER
Make koroche minau soft tek juiege gana emes basqada softardy ustanovka zhasaugada arnalgan

# KassaWrapper Software Installer

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)]()
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()

---

## Описание

**KassaWrapper Software Installer** — это полноценный графический установщик для Windows-приложений.
Проект написан на Python с использованием [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), поддерживает установку в любую директорию, проверку свободного места, красивый прогрессбар и подробный мини-терминал (лог событий).

---

## Особенности

- Выбор пути установки на любой диск (`C:`, `D:`, `E:` и т.д.), в любые папки (например, `Program Files`).
- Проверка свободного места и предупреждение о нехватке.
- Графический интерфейс с логотипом, прогресс-баром, статусами и терминалом событий.
- Полная поддержка установки из ZIP-архива.
- Создание ярлыка на рабочем столе после установки (требует `pywin32` и `winshell`).
- Поддержка отмены установки.
- Логирование событий установки.
- Совместимость с Windows 10/11.

---

## Структура проекта

SoftwareInstaller/
├── assets/
├── builds/
│ └── kassawrapper.zip # Архив с устанавливаемым приложением
├── config/
├── installer_core/
│ ├── installer.py # Основной движок установки
│ └── progress_manager.py
├── localization/
├── logs/
├── ui/
│ └── install.py # GUI-интерфейс установщика
├── main.py # Точка входа
├── requirements.txt
├── license.txt
└── README.md

yaml
Копировать
Редактировать

---

## Установка зависимостей

```bash
pip install -r requirements.txt
В requirements.txt должны быть:

txt
Копировать
Редактировать
customtkinter
pillow
pywin32
winshell
Запуск установщика
Важно: Перед запуском убедитесь, что builds/kassawrapper.zip существует!

bash
Копировать
Редактировать
python main.py
Возможные проблемы
Нет прав на запись в папку (например, Program Files):

Запустите установщик от имени администратора.

Архив kassawrapper.zip не найден:

Убедитесь, что архив лежит в папке builds на одном уровне с main.py.

Сборка и структура архива
Все файлы приложения должны быть упакованы в builds/kassawrapper.zip.

Архив должен содержать все необходимые .exe и ресурсные файлы.

Советы по разработке
Все пути к архиву пишутся так, чтобы искать архив на уровень выше, если скрипт лежит в подпапке (ui/install.py).

Для правильной работы используйте:

python
Копировать
Редактировать
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
archive_path = os.path.join(PROJECT_ROOT, "builds", "kassawrapper.zip")
Проверяйте права на запись заранее, особенно при установке в C:\Program Files.

Контакты для связи и поддержки
Разработчик: Бағдаулет Көптілеу
Почта: b.koptileu@amanbay.tech
Telegram: @t.me.TheProgrammist

Лицензия
Все права защищены © 2024 Бағдаулет Көптілеу / Amanbay tech
