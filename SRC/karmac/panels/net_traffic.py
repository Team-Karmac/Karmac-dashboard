"""
Karmac Dashboard — Network Traffic Panel
Displays per-process network bandwidth using nethogs.
"""

import subprocess
import threading
import re
import os
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from karmac.panels.base import BasePanel
from karmac.settings import Settings


def format_speed(kbps: float) -> str:
    """Format KB/s into human readable string."""
    if kbps >= 1024:
        return f"{kbps / 1024:.1f} MB/s"
    elif kbps >= 0.1:
        return f"{kbps:.1f} KB/s"
    else:
        return "0 B/s"


# Rolling average storage
_traffic_history = {}


def clean_proc_name(proc_path: str) -> str:
    """Extract and clean process name from nethogs path."""
    # Skip IP addresses
    import re
    if re.match(r"^\d+\.\d+\.\d+\.\d+", proc_path):
        return None
    # Skip unknown
    if proc_path.startswith("unknown"):
        return None
    # Handle Windows/Wine/Steam paths (backslashes)
    if "\\" in proc_path or proc_path.endswith(".exe"):
        # Extract just the filename
        # Handle paths like S:\common\mechabellum\mechabellum.exe
        parts = proc_path.replace("\\", "/").split("/")
        name = parts[-1].replace(".exe", "").replace(".EXE", "")
        if not name or name.isdigit():
            return None
        return name.capitalize()

    # Extract name from path like /usr/lib/firefox/firefox/PID/UID
    path_parts = proc_path.split("/")
    name = None
    for i, part in enumerate(path_parts):
        if part.isdigit() and i > 0:
            name = path_parts[i-1]
            break
    if not name:
        name = os.path.basename(proc_path) or proc_path

    # Clean up
    name = name.replace("-bin", "").replace(".bin", "").replace("-", " ")
    return name.capitalize()


def parse_nethogs_output(output: str) -> list:
    """Parse nethogs tracing output into list of process dicts."""
    global _traffic_history
    current = {}

    for line in output.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("Adding") or line.startswith("Ethernet") or line.startswith("Refreshing"):
            continue
        if "TCP/0/0" in line:
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            try:
                proc_path = parts[0].strip()
                sent = float(parts[1])
                recv = float(parts[2])
                name = clean_proc_name(proc_path)
                if name and (sent > 0 or recv > 0):
                    current[name] = {"sent": sent, "recv": recv}
            except (ValueError, IndexError):
                continue

    # Update rolling average history
    for name, data in current.items():
        if name not in _traffic_history:
            _traffic_history[name] = []
        _traffic_history[name].append(data)
        # Keep last 5 readings
        _traffic_history[name] = _traffic_history[name][-5:]

    # Decay old entries — reduce by 50% each cycle if not seen
    for name in list(_traffic_history.keys()):
        if name not in current:
            last = _traffic_history[name][-1]
            decayed = {"sent": last["sent"] * 0.5, "recv": last["recv"] * 0.5}
            _traffic_history[name].append(decayed)
            _traffic_history[name] = _traffic_history[name][-5:]
            # Remove if effectively zero
            if decayed["sent"] < 0.01 and decayed["recv"] < 0.01:
                del _traffic_history[name]

    # Blacklist of invalid process names
    BLACKLIST = {"Exe", "Unknown", "0", "", "Tcp"}

    # Build averaged results
    results = []
    for name, readings in _traffic_history.items():
        if name in BLACKLIST:
            continue
        avg_sent = sum(r["sent"] for r in readings) / len(readings)
        avg_recv = sum(r["recv"] for r in readings) / len(readings)
        if avg_sent > 0.05 or avg_recv > 0.05:  # Higher threshold to filter noise
            results.append({
                "name": name,
                "sent": avg_sent,
                "recv": avg_recv,
                "total": avg_sent + avg_recv,
            })

    return sorted(results, key=lambda x: -x["total"])


class NethogsFetcher(QObject):
    """Runs nethogs in background and emits results."""
    data_ready = Signal(list)

    def __init__(self, interface: str = "", max_procs: int = 5):
        super().__init__()
        self.interface = interface
        self.max_procs = max_procs
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        while self._running:
            try:
                cmd = ["sudo", "nethogs", "-t", "-c", "2", "-d", "1"]
                if self.interface:
                    cmd.append(self.interface)

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                procs = parse_nethogs_output(result.stdout)[:self.max_procs]
                self.data_ready.emit(procs)
            except Exception:
                self.data_ready.emit([])

            # Wait before next sample
            import time
            time.sleep(2)


class NetTrafficPanel(BasePanel):
    """Displays per-process network bandwidth."""

    REFRESH_INTERVAL = 0  # We handle our own refresh via NethogsFetcher
    ACCENT_COLOR = "#ff9500"

    def __init__(self, settings: Settings, parent=None):
        self._proc_widgets = []
        self._no_traffic_label = None
        self._fetcher = None
        super().__init__(settings, title="Network Traffic", parent=parent)
        self._start_fetcher()

    def build_content(self, layout: QVBoxLayout):
        # Column headers
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        proc_header = QLabel("PROCESS")
        proc_header.setStyleSheet("color: rgba(240,240,255,0.35); font-size: 9px; font-weight: 700; letter-spacing: 0.1em;")
        proc_header.setMinimumWidth(100)

        recv_header = QLabel("↓ DOWN")
        recv_header.setStyleSheet("color: rgba(6,214,160,0.5); font-size: 9px; font-weight: 700; letter-spacing: 0.1em;")
        recv_header.setAlignment(Qt.AlignRight)

        sent_header = QLabel("↑ UP")
        sent_header.setStyleSheet("color: rgba(67,97,238,0.5); font-size: 9px; font-weight: 700; letter-spacing: 0.1em;")
        sent_header.setAlignment(Qt.AlignRight)
        sent_header.setMinimumWidth(70)

        header_layout.addWidget(proc_header)
        header_layout.addStretch()
        header_layout.addWidget(recv_header)
        header_layout.addWidget(sent_header)

        layout.addWidget(header)
        layout.addSpacing(4)

        # Process container
        self._proc_container = QVBoxLayout()
        self._proc_container.setSpacing(5)
        layout.addLayout(self._proc_container)

        self._no_traffic_label = self.make_subtitle_label("No active traffic detected")
        self._no_traffic_label.setStyleSheet("color: rgba(240,240,255,0.3); font-style: italic;")
        self._no_traffic_label.hide()
        layout.addWidget(self._no_traffic_label)

    def _start_fetcher(self):
        """Start nethogs background fetcher."""
        net_cfg = self.settings._data.get("network", {})
        max_procs = net_cfg.get("traffic_count", 5)

        self._fetcher = NethogsFetcher(max_procs=max_procs)
        self._fetcher.data_ready.connect(self._update_display)
        self._fetcher.start()

    def _update_display(self, procs: list):
        """Update the process list display."""
        if not hasattr(self, '_proc_container'):
            return

        # Clear existing
        for w in self._proc_widgets:
            w.setParent(None)
            w.deleteLater()
        self._proc_widgets.clear()

        if not procs:
            self._no_traffic_label.show()
            return

        self._no_traffic_label.hide()

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
        name.setMinimumWidth(100)

        recv = QLabel(format_speed(proc["recv"]))
        recv.setObjectName("panel-unit")
        recv.setAlignment(Qt.AlignRight)
        recv.setStyleSheet("color: #06d6a0;")
        recv.setMinimumWidth(75)

        sent = QLabel(format_speed(proc["sent"]))
        sent.setObjectName("panel-unit")
        sent.setAlignment(Qt.AlignRight)
        sent.setStyleSheet("color: #4361ee;")
        sent.setMinimumWidth(70)

        layout.addWidget(name)
        layout.addStretch()
        layout.addWidget(recv)
        layout.addWidget(sent)

        return row

    def refresh(self):
        pass  # NethogsFetcher handles its own refresh cycle

    def closeEvent(self, event):
        if self._fetcher:
            self._fetcher.stop()
        super().closeEvent(event)