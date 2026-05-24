"""
Karmac Dashboard
Everything you need. Nothing you don't.
"""

import sys
from PySide6.QtWidgets import QApplication
from karmac.window import KarmacWindow
from karmac.settings import Settings


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Karmac Dashboard")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Team Karmac")

    settings = Settings()

    from karmac.theme import apply_theme
    apply_theme(app, settings.theme, settings.font_size)

    window = KarmacWindow(settings)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()