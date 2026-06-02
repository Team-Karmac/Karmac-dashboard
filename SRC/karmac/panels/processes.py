"""
Karmac Dashboard — Process Monitor Panel
Displays top processes by CPU and RAM usage.
"""

import psutil
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QStackedWidget, QPushButton
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


FRIENDLY_NAMES = {
    "isolated web co": "Firefox (Web)",
    "webcontentprocess": "Firefox (Web)",
    "web content": "Firefox (Web)",
    "plugin-container": "Firefox Plugin",
    "gnome-shell": "GNOME Shell",
    "kwin_x11": "KWin",
    "plasmashell": "Plasma Shell",
    "cinnamon": "Cinnamon",
    "xorg": "Xorg",
    "pulseaudio": "PulseAudio",
    "pipewire": "PipeWire",
    "systemd": "Systemd",
    "steam": "Steam",
    "steamwebhelper": "Steam Web",
    "discord": "Discord",
    "spotify": "Spotify",
    "code": "VS Code",
    "chrome": "Chrome",
    "chromium": "Chromium",
    "python3": "Python",
    "karmac": "Karmac",
}


def friendly_name(name: str) -> str:
    """Return a friendly display name for known processes."""
    lower = name.lower()
    for key, friendly in FRIENDLY_NAMES.items():
        if key in lower:
            return friendly
    return name


def get_top_processes(count: int = 5, sort_by: str = "cpu") -> list:
    """Get top processes sorted by CPU or RAM usage."""
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        try:
            if p.info['status'] == psutil.STATUS_ZOMBIE:
                continue
            mem_mb = p.info['memory_info'].rss / (1024 * 1024)
            cpu    = p.info['cpu_percent'] or 0.0
            name   = p.info['name'] or "Unknown"
            # Clean up and apply friendly names
            name = name.replace("-bin", "").replace(".bin", "")
            name = friendly_name(name)
            if len(name) > 20:
                name = name[:19] + "…"
            procs.append({
                "name":   name,
                "cpu":    cpu,
                "mem_mb": mem_mb,
                "pid":    p.info['pid'],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if sort_by == "cpu":
        procs.sort(key=lambda x: -x["cpu"])
    else:
        procs.sort(key=lambda x: -x["mem_mb"])

    return procs[:count]


GREEN  = "#06d6a0"
YELLOW = "#ffd000"
RED    = "#ff4d6d"

def cpu_color(pct: float, warning: float = 50, critical: float = 80) -> str:
    if pct >= critical:
        return RED
    elif pct >= warning:
        return YELLOW
    else:
        return GREEN


def mem_color(mb: float, warning: float = 512, critical: float = 2048) -> str:
    if mb >= critical:
        return RED
    elif mb >= warning:
        return YELLOW
    else:
        return GREEN


class ProcessesPanel(BasePanel):
    """Displays top processes by CPU and RAM usage."""

    REFRESH_INTERVAL = 2000
    ACCENT_COLOR = "#e040fb"

    def __init__(self, settings: Settings, parent=None):
        self._sort_by     = "cpu"
        self._proc_widgets = []
        self._cpu_btn     = None
        self._ram_btn     = None
        self._proc_container = None
        super().__init__(settings, title="Processes", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        # Toggle buttons — CPU / RAM
        toggle_row = QWidget()
        toggle_layout = QHBoxLayout(toggle_row)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(8)

        self._cpu_btn = QPushButton("CPU")
        self._cpu_btn.setFixedHeight(26)
        self._cpu_btn.clicked.connect(lambda: self._set_sort("cpu"))

        self._ram_btn = QPushButton("RAM")
        self._ram_btn.setFixedHeight(26)
        self._ram_btn.clicked.connect(lambda: self._set_sort("ram"))

        toggle_layout.addWidget(self._cpu_btn)
        toggle_layout.addWidget(self._ram_btn)

        layout.addWidget(toggle_row)
        layout.addSpacing(6)

        # Column headers
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        proc_hdr = QLabel("PROCESS")
        proc_hdr.setStyleSheet("color: rgba(240,240,255,0.35); font-size: 9px; font-weight: 700; letter-spacing: 0.1em;")

        cpu_hdr = QLabel("CPU")
        cpu_hdr.setStyleSheet("color: rgba(224,64,251,0.5); font-size: 9px; font-weight: 700; letter-spacing: 0.1em;")
        cpu_hdr.setAlignment(Qt.AlignRight)
        cpu_hdr.setFixedWidth(45)

        ram_hdr = QLabel("RAM")
        ram_hdr.setStyleSheet("color: rgba(224,64,251,0.5); font-size: 9px; font-weight: 700; letter-spacing: 0.1em;")
        ram_hdr.setAlignment(Qt.AlignRight)
        ram_hdr.setFixedWidth(60)

        header_layout.addWidget(proc_hdr)
        header_layout.addStretch()
        header_layout.addWidget(cpu_hdr)
        header_layout.addWidget(ram_hdr)

        layout.addWidget(header)
        layout.addSpacing(4)

        # Process list container
        self._proc_container = QVBoxLayout()
        self._proc_container.setSpacing(5)
        layout.addLayout(self._proc_container)

        self._update_button_styles()

    def _set_sort(self, sort_by: str):
        self._sort_by = sort_by
        self._update_button_styles()
        self.refresh()

    def _update_button_styles(self):
        if self._cpu_btn is None:
            return
        active   = "background-color: #e040fb; color: #ffffff; border: none; border-radius: 6px; font-size: 11px; font-weight: 600;"
        inactive = "background-color: rgba(224,64,251,0.12); color: rgba(100,0,120,0.7); border: 1px solid rgba(224,64,251,0.4); border-radius: 6px; font-size: 11px;"
        if self._sort_by == "cpu":
            self._cpu_btn.setStyleSheet(active)
            self._ram_btn.setStyleSheet(inactive)
        else:
            self._cpu_btn.setStyleSheet(inactive)
            self._ram_btn.setStyleSheet(active)

    def refresh(self):
        if self._proc_container is None:
            return

        # Clear existing rows
        for w in self._proc_widgets:
            w.setParent(None)
            w.deleteLater()
        self._proc_widgets.clear()

        count = self.settings._data.get("processes", {}).get("count", 5)
        procs = get_top_processes(count=count, sort_by=self._sort_by)

        for proc in procs:
            row = self._make_proc_row(proc)
            self._proc_container.addWidget(row)
            self._proc_widgets.append(row)

    def _make_proc_row(self, proc: dict) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(8)

        name = QLabel(proc["name"])
        name.setObjectName("panel-subtitle")

        cpu = QLabel(f"{proc['cpu']:.1f}%")
        cpu.setObjectName("panel-unit")
        cpu.setAlignment(Qt.AlignRight)
        cpu.setFixedWidth(45)
        cpu.setStyleSheet(f"color: {cpu_color(proc['cpu'])};")

        mem_mb = proc["mem_mb"]
        if mem_mb >= 1024:
            mem_str = f"{mem_mb / 1024:.1f} GB"
        else:
            mem_str = f"{mem_mb:.0f} MB"

        ram = QLabel(mem_str)
        ram.setObjectName("panel-unit")
        ram.setAlignment(Qt.AlignRight)
        ram.setFixedWidth(60)
        ram.setStyleSheet(f"color: {mem_color(mem_mb)};")

        layout.addWidget(name)
        layout.addStretch()
        layout.addWidget(cpu)
        layout.addWidget(ram)

        return row