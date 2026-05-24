"""
Karmac Dashboard — Network Status Panel
Displays upload/download speeds, connection type, and network name.
"""

import psutil
import time
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


def get_network_info() -> dict:
    """
    Read current network stats.
    Returns upload/download speeds in KB/s and active interface info.
    """
    result = {
        "upload_speed":   0.0,
        "download_speed": 0.0,
        "interface":      "Unknown",
        "is_connected":   False,
    }

    try:
        # Get bytes sent/received
        counters1 = psutil.net_io_counters(pernic=False)
        time.sleep(0.5)
        counters2 = psutil.net_io_counters(pernic=False)

        interval = 0.5
        upload   = (counters2.bytes_sent - counters1.bytes_sent) / interval
        download = (counters2.bytes_recv - counters1.bytes_recv) / interval

        result["upload_speed"]   = upload
        result["download_speed"] = download

        # Find active network interface
        net_if_stats = psutil.net_if_stats()
        net_if_addrs = psutil.net_if_addrs()

        for iface, stats in net_if_stats.items():
            if stats.isup and iface != "lo":
                result["interface"]    = iface
                result["is_connected"] = True
                break

    except Exception:
        pass

    return result


def format_speed(bytes_per_sec: float) -> str:
    """Format bytes/sec into a human-readable string."""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    else:
        return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"


class NetworkPanel(BasePanel):
    """Displays network upload/download speeds and connection info."""

    REFRESH_INTERVAL = 2000  # Refresh every 2 seconds
    ACCENT_COLOR = "#9b5de5"

    def __init__(self, settings: Settings, parent=None):
        self._download_label = None
        self._upload_label = None
        self._interface_label = None
        self._status_label = None
        super().__init__(settings, title="Network", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        """Build the network display."""
        # Download row
        dl_row = QWidget()
        dl_layout = QHBoxLayout(dl_row)
        dl_layout.setContentsMargins(0, 0, 0, 0)
        dl_layout.setSpacing(10)

        dl_icon = QLabel("↓")
        dl_icon.setStyleSheet("color: #06d6a0; font-size: 20px; font-weight: bold;")

        dl_label = QLabel("Download")
        dl_label.setObjectName("panel-subtitle")

        self._download_label = QLabel("-- KB/s")
        self._download_label.setObjectName("panel-subtitle")
        self._download_label.setAlignment(Qt.AlignRight)
        self._download_label.setStyleSheet("color: #06d6a0;")

        dl_layout.addWidget(dl_icon)
        dl_layout.addWidget(dl_label)
        dl_layout.addStretch()
        dl_layout.addWidget(self._download_label)

        # Upload row
        ul_row = QWidget()
        ul_layout = QHBoxLayout(ul_row)
        ul_layout.setContentsMargins(0, 0, 0, 0)
        ul_layout.setSpacing(10)

        ul_icon = QLabel("↑")
        ul_icon.setStyleSheet("color: #4361ee; font-size: 20px; font-weight: bold;")

        ul_label = QLabel("Upload")
        ul_label.setObjectName("panel-subtitle")

        self._upload_label = QLabel("-- KB/s")
        self._upload_label.setObjectName("panel-subtitle")
        self._upload_label.setAlignment(Qt.AlignRight)
        self._upload_label.setStyleSheet("color: #4361ee;")

        ul_layout.addWidget(ul_icon)
        ul_layout.addWidget(ul_label)
        ul_layout.addStretch()
        ul_layout.addWidget(self._upload_label)

        # Interface label
        self._interface_label = self.make_unit_label("")
        self._status_label = self.make_unit_label("")

        layout.addWidget(dl_row)
        layout.addWidget(ul_row)
        layout.addWidget(self._interface_label)
        layout.addWidget(self._status_label)

    def refresh(self):
        """Update network speed display."""
        if self._download_label is None:
            return

        info = get_network_info()

        self._download_label.setText(format_speed(info["download_speed"]))
        self._upload_label.setText(format_speed(info["upload_speed"]))

        if info["is_connected"]:
            self._interface_label.setText(f"Interface: {info['interface']}")
            self._status_label.setText("● Connected")
            self._status_label.setStyleSheet("color: #06d6a0; font-size: 12px;")
        else:
            self._interface_label.setText("")
            self._status_label.setText("● Disconnected")
            self._status_label.setStyleSheet("color: #ff4d6d; font-size: 12px;")