"""
Karmac Dashboard
Everything you need. Nothing you don't.
"""

import sys
import traceback
import logging
from pathlib import Path

# Set up logging to file
log_dir = Path.home() / ".config" / "karmac"
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_dir / "karmac.log",
    level=logging.ERROR,
    format="%(asctime)s — %(levelname)s — %(message)s"
)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler — log crashes instead of silent exit."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    traceback.print_exception(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception


from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from pathlib import Path
from karmac.window import KarmacWindow
from karmac.settings import Settings


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Karmac Dashboard")
    app.setApplicationVersion("3.0.0")
    app.setOrganizationName("Team Karmac")

    # Set app icon
    icon_path = Path.home() / ".local" / "share" / "icons" / "Karmac_Logo.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    settings = Settings()

    from karmac.theme import apply_theme
    apply_theme(app, settings.theme, settings.font_size)

    window = KarmacWindow(settings)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()