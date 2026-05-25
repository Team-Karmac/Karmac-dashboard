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
from karmac.panels.temperature import TemperaturePanel
from karmac.panels.ram import RamPanel
from karmac.panels.drives import DrivesPanel
from karmac.panels.cpu_cores import CpuCoresPanel
from karmac.panels.hardware import HardwarePanel, get_cpu_name, get_gpu_name, get_ram_details, get_ram_total, get_ram_speed, get_storage_total, get_motherboard, get_os_info, get_kernel_version, get_desktop_environment, get_display_info, get_drive_details
from karmac.panels.gpu_usage import GpuUsagePanel
from karmac.panels.power import PowerPanel
from karmac.panels.fps import FpsPanel
from karmac.panels.net_traffic import NetTrafficPanel
from karmac.panels.processes import ProcessesPanel
from karmac.panels.disk_io import DiskIoPanel
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
        self._settings_view = SettingsView(self.settings, main_window=self, parent=self)

        content_layout.addWidget(self._dashboard_view)
        content_layout.addWidget(self._settings_view)
        self._settings_view.hide()

        root_layout.addWidget(self._content_stack)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)

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
        layout.addSpacing(8)

        # Hardware section in sidebar
        layout.addSpacing(12)

        # Brown accent bar
        hw_bar = QWidget()
        hw_bar.setFixedHeight(3)
        hw_bar.setStyleSheet("""
            background-color: #c17c3a;
            border-radius: 2px;
            margin: 0 6px;
        """)
        layout.addWidget(hw_bar)
        layout.addSpacing(10)

        # Hardware section title
        hw_title = QLabel("HARDWARE")
        hw_title.setStyleSheet(
            "color: #c17c3a;"
            "font-size: 10px;"
            "font-weight: 700;"
            "letter-spacing: 0.14em;"
            "padding-left: 6px;"
        )
        layout.addWidget(hw_title)
        layout.addSpacing(4)

        # Hardware info
        hw_specs = self._build_sidebar_hardware()
        for label, value in hw_specs:
            row = QWidget()
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(6, 3, 6, 3)
            row_layout.setSpacing(1)

            lbl = QLabel(label.upper())
            lbl.setStyleSheet(
                "color: rgba(240,240,255,0.35);"
                "font-size: 9px;"
                "font-weight: 700;"
                "letter-spacing: 0.1em;"
            )
            val = QLabel(value)
            val.setStyleSheet(
                "color: rgba(240,240,255,0.85);"
                "font-size: 11px;"
            )
            val.setWordWrap(True)

            row_layout.addWidget(lbl)
            row_layout.addWidget(val)
            layout.addWidget(row)

        layout.addStretch()

        # Version
        ver = QLabel("V 3.0.0")
        ver.setObjectName("version-label")
        ver.setAlignment(Qt.AlignCenter)
        layout.addWidget(ver)

        return sidebar

    def _build_sidebar_hardware(self) -> list:
        """Build hardware specs list for sidebar display."""
        try:
            ram_sticks = get_ram_details()
            if ram_sticks:
                stick    = ram_sticks[0]
                total    = get_ram_total()
                ram_type = stick.get("type", "").strip()
                speed    = stick.get("configured_memory_speed") or stick.get("speed", "")
                speed    = speed.strip() if speed else ""
                mfr      = stick.get("manufacturer", "").strip()
                mfr_map  = {"G-Skill": "G.Skill", "Kingston": "Kingston", "Corsair": "Corsair",
                            "Crucial": "Crucial", "Samsung": "Samsung", "Hynix": "SK Hynix"}
                mfr      = mfr_map.get(mfr, mfr)
                parts    = [p for p in [mfr, total, ram_type, speed] if p and p not in ("Unknown","")]
                ram_str  = "  ".join(parts)
            else:
                ram_str = get_ram_total()

            drive_details = get_drive_details()
            if drive_details:
                d = drive_details[0]
                mfr = ""
                from karmac.panels.hardware import get_drive_manufacturer
                mfr = get_drive_manufacturer(d["model"])
                model = d["model"]
                import re
                for strip in ("nvme", "NVMe", "NVME", "ssd", "SSD"):
                    model = re.sub(rf"\b{strip}\b", "", model, flags=re.IGNORECASE).strip()
                model = re.sub(r"\s+", " ", model).strip()
                if mfr and mfr.upper() not in model.upper():
                    drive_str = f"{mfr} {model}  ({d['type']}  {d['size']})"
                else:
                    drive_str = f"{model}  ({d['type']}  {d['size']})"
            else:
                drive_str = get_storage_total()

            displays = get_display_info()
            display_str = displays[0] if displays else "Unknown"

            gpu_name = get_gpu_name()
            import re
            gpu_name = re.split(r"\s+OEM|\s*/", gpu_name)[0].strip()

            return [
                ("CPU",     get_cpu_name()),
                ("GPU",     gpu_name),
                ("Board",   get_motherboard()),
                ("OS",      get_os_info()),
                ("Kernel",  get_kernel_version()),
                ("Desktop", get_desktop_environment()),
                ("RAM",     ram_str),
                ("Drive",   drive_str),
                ("Display", display_str),
            ]
        except Exception as e:
            return [("Error", str(e))]

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
            "clock":       ClockPanel,
            "weather":     WeatherPanel,
            "fan_speeds":  FanSpeedsPanel,
            "network":     NetworkPanel,
            "uptime":      UptimePanel,
            "temperature": TemperaturePanel,
            "ram":         RamPanel,
            "drives":      DrivesPanel,
            "cpu_cores":   CpuCoresPanel,
            "hardware":    HardwarePanel,
            "gpu_usage":   GpuUsagePanel,
            "power":       PowerPanel,
            "fps":         FpsPanel,
            "net_traffic": NetTrafficPanel,
            "processes":   ProcessesPanel,
            "disk_io":     DiskIoPanel,
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

            if col % 3 == 0:
                row_widget = QWidget()
                row_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(14)
                row_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                self._grid.addWidget(row_widget)

            panel = panel_classes[panel_name](self.settings)
            panel.setObjectName("panel")
            panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            row_layout.addWidget(panel)
            self._panels[panel_name] = panel
            col += 1

        # Balance last row
        remainder = col % 3
        if remainder != 0 and row_layout:
            for _ in range(3 - remainder):
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