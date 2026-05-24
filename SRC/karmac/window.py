"""
Karmac Dashboard — Main Window
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtSvgWidgets import QSvgWidget

from karmac.settings import Settings
from karmac.panels.clock import ClockPanel
from karmac.panels.weather import WeatherPanel
from karmac.panels.fan_speeds import FanSpeedsPanel
from karmac.panels.network import NetworkPanel
from karmac.panels.uptime import UptimePanel
from karmac.settings_view import SettingsView

import os


class KarmacWindow(QMainWindow):

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self._panels = {}
        self._setup_window()
        self._build_ui()
        self._restore_geometry()

    def _setup_window(self):
        self.setWindowTitle("Karmac Dashboard")
        self.setMinimumSize(820, 580)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "Karmac_Logo.svg")
        if os.path.exists(icon_path):
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_sidebar())

        # Content stack
        self._content_stack = QWidget()
        content_layout = QVBoxLayout(self._content_stack)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._dashboard_view = self._build_dashboard()
        self._settings_view = SettingsView(self.settings, self)

        content_layout.addWidget(self._dashboard_view)
        content_layout.addWidget(self._settings_view)
        self._settings_view.hide()

        root_layout.addWidget(self._content_stack)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 24, 14, 20)
        layout.setSpacing(2)

        # Logo + name
        logo_row = QWidget()
        logo_layout = QHBoxLayout(logo_row)
        logo_layout.setContentsMargins(6, 0, 0, 0)
        logo_layout.setSpacing(10)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "Karmac_Logo.svg")
        if os.path.exists(icon_path):
            logo = QSvgWidget(icon_path)
            logo.setFixedSize(36, 36)
            logo_layout.addWidget(logo)

        name_block = QWidget()
        name_layout = QVBoxLayout(name_block)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(1)

        title = QLabel("Karmac")
        title.setObjectName("sidebar-title")

        tagline = QLabel("Everything you need. Nothing you don't.")
        tagline.setObjectName("sidebar-tagline")

        name_layout.addWidget(title)
        tagline.setWordWrap(True)
        tagline.setStyleSheet("font-size: 9px; color: rgba(240,240,255,0.28); font-style: italic; letter-spacing: 0.03em;")
        name_layout.addWidget(tagline)
        logo_layout.addWidget(name_block)
        logo_layout.addStretch()

        layout.addWidget(logo_row)
        layout.addSpacing(20)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color: rgba(255,255,255,0.07); margin: 0 6px;")
        layout.addWidget(div)
        layout.addSpacing(12)

        # Nav buttons
        self._nav_dashboard = self._nav_btn("  Dashboard", checked=True)
        self._nav_settings  = self._nav_btn("  Settings")

        self._nav_dashboard.clicked.connect(lambda: self._switch_view("dashboard"))
        self._nav_settings.clicked.connect(lambda: self._switch_view("settings"))

        layout.addWidget(self._nav_dashboard)
        layout.addWidget(self._nav_settings)
        layout.addStretch()

        # Version
        ver = QLabel("V 1.0.0")
        ver.setObjectName("version-label")
        ver.setAlignment(Qt.AlignCenter)
        layout.addWidget(ver)

        return sidebar

    def _nav_btn(self, text: str, checked: bool = False) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("nav-button")
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def _build_dashboard(self) -> QWidget:
        container = QWidget()
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        self._grid = QVBoxLayout(inner)
        self._grid.setContentsMargins(24, 24, 24, 24)
        self._grid.setSpacing(14)
        self._grid.setAlignment(Qt.AlignTop)

        self._build_panels()

        scroll.setWidget(inner)
        outer.addWidget(scroll)
        return container

    def _build_panels(self):
        panel_classes = {
            "clock":      ClockPanel,
            "weather":    WeatherPanel,
            "fan_speeds": FanSpeedsPanel,
            "network":    NetworkPanel,
            "uptime":     UptimePanel,
        }

        panel_order = sorted(
            self.settings.panels.items(),
            key=lambda x: x[1].get("position", 99)
        )

        row_widget = None
        row_layout = None
        col = 0

        for panel_name, panel_cfg in panel_order:
            if not panel_cfg.get("enabled", True):
                continue
            if panel_name not in panel_classes:
                continue

            if col % 2 == 0:
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(14)
                row_layout.setAlignment(Qt.AlignTop)
                self._grid.addWidget(row_widget)

            panel = panel_classes[panel_name](self.settings)
            panel.setObjectName("panel")
            panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            row_layout.addWidget(panel)
            self._panels[panel_name] = panel
            col += 1

        # Balance last row
        if col % 2 == 1 and row_layout:
            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row_layout.addWidget(spacer)

    def _switch_view(self, view: str):
        self._nav_dashboard.setChecked(view == "dashboard")
        self._nav_settings.setChecked(view == "settings")
        if view == "dashboard":
            self._dashboard_view.show()
            self._settings_view.hide()
        else:
            self._dashboard_view.hide()
            self._settings_view.show()

    def _restore_geometry(self):
        w = self.settings.window
        width  = w.get("width", 1100)
        height = w.get("height", 700)
        self.resize(width, height)
        x, y = w.get("x"), w.get("y")
        if x is not None and y is not None:
            self.move(x, y)
        else:
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            self.move((screen.width() - width) // 2, (screen.height() - height) // 2)

    def closeEvent(self, event):
        geo = self.geometry()
        self.settings.update_window_geometry(geo.x(), geo.y(), geo.width(), geo.height())
        super().closeEvent(event)

    def apply_theme(self, theme: str):
        from karmac.theme import apply_theme
        from PySide6.QtWidgets import QApplication
        apply_theme(QApplication.instance(), theme, self.settings.font_size)