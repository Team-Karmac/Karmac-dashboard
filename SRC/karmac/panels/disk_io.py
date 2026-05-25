"""
Karmac Dashboard — Disk I/O Panel
Displays real-time disk read/write speeds for all physical drives.
"""

import psutil
import time
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


GREEN  = "#06d6a0"
YELLOW = "#ffd000"
RED    = "#ff4d6d"

# Store previous readings for delta calculation
_last_io     = None
_last_io_time = None


def get_disk_io() -> dict:
    """Calculate disk read/write speeds since last call."""
    global _last_io, _last_io_time

    try:
        current    = psutil.disk_io_counters(perdisk=False)
        now        = time.monotonic()

        if _last_io is not None and _last_io_time is not None:
            delta_time  = now - _last_io_time
            if delta_time > 0:
                read_speed  = (current.read_bytes  - _last_io.read_bytes)  / delta_time
                write_speed = (current.write_bytes - _last_io.write_bytes) / delta_time
                _last_io      = current
                _last_io_time = now
                return {
                    "read_bps":   max(0, read_speed),
                    "write_bps":  max(0, write_speed),
                    "read_count": current.read_count,
                    "write_count":current.write_count,
                    "success":    True,
                }

        _last_io      = current
        _last_io_time = now
        return {"read_bps": 0, "write_bps": 0, "success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


def format_speed(bps: float) -> str:
    """Format bytes per second into human readable string."""
    if bps >= 1024 ** 3:
        return f"{bps / (1024 ** 3):.2f} GB/s"
    elif bps >= 1024 ** 2:
        return f"{bps / (1024 ** 2):.1f} MB/s"
    elif bps >= 1024:
        return f"{bps / 1024:.1f} KB/s"
    else:
        return f"{bps:.0f} B/s"


def io_color(bps: float) -> str:
    """Color based on I/O speed."""
    mb = bps / (1024 ** 2)
    if mb >= 1000:
        return RED
    elif mb >= 100:
        return YELLOW
    else:
        return GREEN


class DiskIoPanel(BasePanel):
    """Displays real-time disk read/write speeds."""

    REFRESH_INTERVAL = 1000
    ACCENT_COLOR = "#2ec4b6"

    def __init__(self, settings: Settings, parent=None):
        self._read_label  = None
        self._write_label = None
        self._read_val    = None
        self._write_val   = None
        super().__init__(settings, title="Disk I/O", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        # Read speed
        read_row = QWidget()
        read_layout = QHBoxLayout(read_row)
        read_layout.setContentsMargins(0, 0, 0, 4)
        read_layout.setSpacing(8)

        read_icon = QLabel("↓")
        read_icon.setStyleSheet("color: #06d6a0; font-size: 20px; font-weight: bold;")
        read_label = QLabel("Read")
        read_label.setObjectName("panel-subtitle")

        self._read_val = QLabel("--")
        self._read_val.setObjectName("panel-value")
        font = self._read_val.font()
        font.setPointSize(26)
        self._read_val.setFont(font)
        self._read_val.setAlignment(Qt.AlignRight)
        self._read_val.setStyleSheet(f"color: {GREEN}; font-size: 26px; font-weight: 300;")

        read_layout.addWidget(read_icon)
        read_layout.addWidget(read_label)
        read_layout.addStretch()
        read_layout.addWidget(self._read_val)

        # Write speed
        write_row = QWidget()
        write_layout = QHBoxLayout(write_row)
        write_layout.setContentsMargins(0, 0, 0, 4)
        write_layout.setSpacing(8)

        write_icon = QLabel("↑")
        write_icon.setStyleSheet("color: #4361ee; font-size: 20px; font-weight: bold;")
        write_label = QLabel("Write")
        write_label.setObjectName("panel-subtitle")

        self._write_val = QLabel("--")
        self._write_val.setObjectName("panel-value")
        self._write_val.setFont(font)
        self._write_val.setAlignment(Qt.AlignRight)
        self._write_val.setStyleSheet(f"color: {GREEN}; font-size: 26px; font-weight: 300;")

        write_layout.addWidget(write_icon)
        write_layout.addWidget(write_label)
        write_layout.addStretch()
        write_layout.addWidget(self._write_val)

        layout.addWidget(read_row)
        layout.addWidget(write_row)
        layout.addSpacing(8)

        # Drive info
        self._drive_label = self.make_unit_label("nvme0n1")
        layout.addWidget(self._drive_label)

    def refresh(self):
        if self._read_val is None:
            return

        info = get_disk_io()
        if not info.get("success"):
            return

        read_bps  = info["read_bps"]
        write_bps = info["write_bps"]

        self._read_val.setText(format_speed(read_bps))
        self._read_val.setStyleSheet(
            f"color: {io_color(read_bps)}; font-size: 26px; font-weight: 300;"
        )

        self._write_val.setText(format_speed(write_bps))
        self._write_val.setStyleSheet(
            f"color: {io_color(write_bps)}; font-size: 26px; font-weight: 300;"
        )