"""
Karmac Dashboard — System Uptime Panel
Displays how long the system has been running since last boot.
"""

import psutil
import time
from datetime import datetime, timezone
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from karmac.panels.base import BasePanel
from karmac.settings import Settings


def get_uptime() -> dict:
    """
    Get system uptime information.
    Returns dict with days, hours, minutes, seconds, and boot_time string.
    """
    try:
        boot_timestamp = psutil.boot_time()
        boot_dt = datetime.fromtimestamp(boot_timestamp)
        now = datetime.now()

        delta = now - boot_dt
        total_seconds = int(delta.total_seconds())

        days    = delta.days
        hours   = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return {
            "days":      days,
            "hours":     hours,
            "minutes":   minutes,
            "seconds":   seconds,
            "boot_time": boot_dt.strftime("%A, %b %d at %I:%M %p"),
            "success":   True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_uptime(days: int, hours: int, minutes: int, seconds: int) -> str:
    """Format uptime into a clean human-readable string."""
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    if days == 0:
        parts.append(f"{seconds}s")
    return " ".join(parts)


class UptimePanel(BasePanel):
    """Displays system uptime since last boot."""

    REFRESH_INTERVAL = 1000  # Update every second
    ACCENT_COLOR = "#ff4d6d"

    def __init__(self, settings: Settings, parent=None):
        self._uptime_label = None
        self._boot_label = None
        super().__init__(settings, title="System Uptime", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        """Build the uptime display."""
        self._uptime_label = self.make_value_label("--")

        # Slightly smaller than default value label
        font = self._uptime_label.font()
        font.setPointSize(28)
        font.setWeight(QFont.Weight.Light)
        self._uptime_label.setFont(font)

        self._boot_label = self.make_subtitle_label("Last boot: --")

        layout.addWidget(self._uptime_label)
        layout.addWidget(self._boot_label)

    def refresh(self):
        """Update the displayed uptime."""
        if self._uptime_label is None:
            return

        info = get_uptime()

        if info.get("success"):
            uptime_str = format_uptime(
                info["days"], info["hours"],
                info["minutes"], info["seconds"]
            )
            self._uptime_label.setText(uptime_str)
            self._boot_label.setText(f"Since {info['boot_time']}")
        else:
            self._uptime_label.setText("--")
            self._boot_label.setText("Unable to read uptime")