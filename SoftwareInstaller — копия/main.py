import sys
import customtkinter as ctk
from config.settings import (
    APPEARANCE_MODE,
    COLOR_THEME,
    ARCHIVE_NAME,
    get_install_path
)
from installer_core.installer import InstallerEngine, InstallerError
from ui.splash import SplashScreen
from ui.welcome import WelcomeScreen
from ui.license import LicenseScreen
from ui.install import InstallPage
from ui.finish import FinishScreen


def parse_args():
    args = sys.argv[1:]
    opts = {'silent': False, 'uninstall': False, 'install_dir': None}
    for arg in args:
        lower = arg.lower()
        if lower in ('/silent', '/s', '--silent'):
            opts['silent'] = True
        elif lower in ('/uninstall', '/u', '--uninstall'):
            opts['uninstall'] = True
        elif lower.startswith('/dir=') or lower.startswith('--dir='):
            opts['install_dir'] = arg.split('=', 1)[1]
    return opts


def run_gui():
    ctk.set_appearance_mode(APPEARANCE_MODE)
    ctk.set_default_color_theme(COLOR_THEME)

    app = ctk.CTk()
    app.withdraw()

    def finish_app():
        app.quit()

    def run_welcome():
        w = WelcomeScreen(on_continue=lambda: on_welcome(w))
        w.mainloop()

    def on_welcome(win):
        win.destroy()
        run_license()

    def run_license():
        l = LicenseScreen(on_accept=lambda: on_license(l))
        l.mainloop()

    def on_license(win):
        win.destroy()
        run_splash()

    def run_splash():
        s = SplashScreen(callback=lambda: on_splash(s))
        s.mainloop()

    def on_splash(win):
        win.destroy()
        run_install()

    def run_install():
        page = InstallPage(
            on_success=lambda: on_install_success(page),
            on_cancel=lambda: on_install_cancel(page)
        )
        page.mainloop()

    def on_install_success(page):
        page.destroy()
        run_finish()

    def on_install_cancel(page):
        page.destroy()
        finish_app()

    def run_finish():
        f = FinishScreen(on_close=lambda: finish_app())
        f.mainloop()

    run_welcome()
    app.mainloop()


def run_cli(opts):
    # Установочный каталог: либо из аргументов, либо стандартный
    install_dir = opts.get('install_dir') or get_install_path()
    engine = InstallerEngine(
        archive_path=ARCHIVE_NAME,
        install_dir=install_dir,
        options={}
    )
    try:
        if opts['uninstall']:
            success = engine.silent_uninstall()
        else:
            success = engine.silent_install()
        sys.exit(0 if success else 1)
    except InstallerError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    opts = parse_args()
    if opts['silent'] or opts['uninstall']:
        run_cli(opts)
    else:
        run_gui()