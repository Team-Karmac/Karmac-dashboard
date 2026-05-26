"""
Karmac Dashboard — Hard Drive Space Panel
Displays used/available/total space for all detected drives.
"""

import psutil
import os
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


def get_drive_info() -> list:
    """Read disk usage for all mounted drives, deduplicating by physical device."""
    seen_devices = {}
    try:
        partitions = psutil.disk_partitions()
        for p in partitions:
            # Skip virtual filesystems
            if any(skip in p.fstype for skip in (
                'squash', 'tmpfs', 'devtmpfs', 'proc', 'sysfs', 'overlay',
                'fuse', 'fusectl', 'cgroup', 'pstore', 'bpf', 'tracefs',
                'debugfs', 'configfs', 'hugetlbfs', 'mqueue', 'ramfs'
            )):
                continue
            # Only show real physical drives
            if not p.device.startswith('/dev/'):
                continue
            # Skip system/boot/Flatpak paths
            skip_paths = (
                '/snap/', '/boot', '/run/', '/etc/', '/usr/',
                '/var/', '/lib', '/bin', '/sbin', '/opt', '/srv',
                '/tmp', '/lost+found', '/cdrom', '/swapfile', '/timeshift'
            )
            if any(skip in p.mountpoint for skip in skip_paths):
                continue
            try:
                usage = psutil.disk_usage(p.mountpoint)

                if p.mountpoint == "/":
                    name = "System Drive"
                    priority = 0
                elif p.mountpoint == "/home":
                    name = "Home"
                    priority = 1
                elif p.mountpoint.startswith("/media") or p.mountpoint.startswith("/mnt"):
                    name = os.path.basename(p.mountpoint) or "External Drive"
                    priority = 2
                else:
                    name = p.mountpoint
                    priority = 3

                # Keep only the best mount point per physical device
                if p.device not in seen_devices or priority < seen_devices[p.device]['priority']:
                    seen_devices[p.device] = {
                        "name":       name,
                        "mountpoint": p.mountpoint,
                        "device":     p.device.split("/")[-1],
                        "total":      usage.total,
                        "used":       usage.used,
                        "free":       usage.free,
                        "percent":    usage.percent,
                        "priority":   priority,
                    }
            except (PermissionError, OSError):
                continue
    except Exception:
        pass
    return list(seen_devices.values())


def format_bytes(b: int) -> str:
    if b >= 1024 ** 4:
        return f"{b / (1024 ** 4):.1f} TB"
    elif b >= 1024 ** 3:
        return f"{b / (1024 ** 3):.1f} GB"
    elif b >= 1024 ** 2:
        return f"{b / (1024 ** 2):.0f} MB"
    else:
        return f"{b / 1024:.0f} KB"


class DrivesPanel(BasePanel):
    """Displays disk space usage for all detected drives."""

    REFRESH_INTERVAL = 30000
    ACCENT_COLOR = "#b5e800"

    def __init__(self, settings: Settings, parent=None):
        self._drive_widgets = []
        self._no_drives_label = None
        super().__init__(settings, title="Hard Drives", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        self._drive_container = QVBoxLayout()
        self._drive_container.setSpacing(12)
        self._drive_container.setContentsMargins(0, 4, 0, 4)
        layout.addLayout(self._drive_container)

        self._no_drives_label = self.make_subtitle_label("No drives detected")
        self._no_drives_label.hide()
        layout.addWidget(self._no_drives_label)

    def refresh(self):
        if not hasattr(self, '_drive_container'):
            return

        for w in self._drive_widgets:
            w.setParent(None)
            w.deleteLater()
        self._drive_widgets.clear()

        hidden = self.settings._data.get("drives", {}).get("hidden", [])
        drives = [d for d in get_drive_info() if d["mountpoint"] not in hidden]

        if not drives:
            self._no_drives_label.show()
            return

        self._no_drives_label.hide()

        drives_cfg = self.settings._data.get("drives_thresholds", {})
        warn = drives_cfg.get("warning", 75)
        crit = drives_cfg.get("critical", 90)

        for drive in drives:
            row = self._make_drive_row(drive, warn, crit)
            self._drive_container.addWidget(row)
            self._drive_widgets.append(row)

    def _make_drive_row(self, drive: dict, warn: float, crit: float) -> QWidget:
        row = QWidget()
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(5)

        pct = drive["percent"]
        if pct >= crit:
            color = "#ff4d6d"
        elif pct >= warn:
            color = "#ffd000"
        else:
            color = "#06d6a0"

        top = QWidget()
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        name_label = QLabel(drive["name"])
        name_label.setObjectName("panel-subtitle")
        name_label.setStyleSheet("font-weight: 600;")

        pct_label = QLabel(f"{pct:.0f}%")
        pct_label.setObjectName("panel-subtitle")
        pct_label.setAlignment(Qt.AlignRight)
        pct_label.setStyleSheet(f"color: {color}; font-weight: 600;")

        top_layout.addWidget(name_label)
        top_layout.addStretch()
        top_layout.addWidget(pct_label)

        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(4)

        used_label = QLabel(f"{format_bytes(drive['used'])} used of {format_bytes(drive['total'])}")
        used_label.setObjectName("panel-unit")

        free_label = QLabel(f"{format_bytes(drive['free'])} free")
        free_label.setObjectName("panel-unit")
        free_label.setAlignment(Qt.AlignRight)
        free_label.setStyleSheet(f"color: {color};")

        bottom_layout.addWidget(used_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(free_label)

        layout.addWidget(top)
        layout.addWidget(bottom)

        return row