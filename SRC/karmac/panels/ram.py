"""
Karmac Dashboard — RAM Usage Panel
Displays current RAM usage with used/available/total breakdown.
"""

import psutil
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QProgressBar
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


def get_ram_info() -> dict:
    """Read current RAM usage from the system."""
    try:
        mem = psutil.virtual_memory()
        return {
            "total":     mem.total,
            "used":      mem.used,
            "available": mem.available,
            "percent":   mem.percent,
            "success":   True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_bytes(b: int) -> str:
    """Format bytes into a human readable string."""
    if b >= 1024 ** 3:
        return f"{b / (1024 ** 3):.1f} GB"
    elif b >= 1024 ** 2:
        return f"{b / (1024 ** 2):.0f} MB"
    else:
        return f"{b / 1024:.0f} KB"


class RamPanel(BasePanel):
    """Displays current RAM usage."""

    REFRESH_INTERVAL = 2000
    ACCENT_COLOR = "#00f5d4"

    def __init__(self, settings: Settings, parent=None):
        self._used_label    = None
        self._total_label   = None
        self._avail_label   = None
        self._percent_label = None
        super().__init__(settings, title="RAM Usage", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        # Main value row: used / total
        main_row = QWidget()
        main_layout = QHBoxLayout(main_row)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)

        self._used_label = self.make_value_label("--")
        font = self._used_label.font()
        font.setPointSize(28)
        self._used_label.setFont(font)

        separator = QLabel("/")
        separator.setObjectName("panel-subtitle")
        separator.setStyleSheet("color: rgba(240,240,255,0.3); font-size: 22px;")

        self._total_label = QLabel("--")
        self._total_label.setObjectName("panel-subtitle")
        self._total_label.setStyleSheet("color: rgba(240,240,255,0.5); font-size: 18px;")
        self._total_label.setAlignment(Qt.AlignBottom)

        self._percent_label = QLabel("--%")
        self._percent_label.setObjectName("panel-subtitle")
        self._percent_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self._percent_label.setStyleSheet("color: #00f5d4; font-size: 18px;")

        main_layout.addWidget(self._used_label)
        main_layout.addWidget(separator)
        main_layout.addWidget(self._total_label)
        main_layout.addStretch()
        main_layout.addWidget(self._percent_label)

        self._avail_label = self.make_unit_label("")

        layout.addWidget(main_row)
        layout.addWidget(self._avail_label)

    def refresh(self):
        if self._used_label is None:
            return

        info = get_ram_info()

        if not info.get("success"):
            self._used_label.setText("--")
            return

        self._used_label.setText(format_bytes(info["used"]))
        self._total_label.setText(format_bytes(info["total"]))
        self._percent_label.setText(f"{info['percent']:.0f}%")
        self._avail_label.setText(f"{format_bytes(info['available'])} available")

        # Color percent based on usage
        pct = info["percent"]
        if pct >= 90:
            color = "#ff4d6d"
        elif pct >= 70:
            color = "#ffd000"
        else:
            color = "#00f5d4"
        self._percent_label.setStyleSheet(f"color: {color}; font-size: 18px;")