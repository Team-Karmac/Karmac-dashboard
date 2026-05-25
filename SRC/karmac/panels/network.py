"""
Karmac Dashboard — Network Status Panel
Displays upload/download speeds, connection info, ping/latency, and speed test.
"""

import psutil
import time
import subprocess
import threading
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from karmac.panels.base import BasePanel
from karmac.settings import Settings


def get_network_info() -> dict:
    """Read current network stats."""
    result = {
        "upload_speed":   0.0,
        "download_speed": 0.0,
        "interface":      "Unknown",
        "is_connected":   False,
    }
    try:
        counters1 = psutil.net_io_counters(pernic=False)
        time.sleep(0.5)
        counters2 = psutil.net_io_counters(pernic=False)
        interval = 0.5
        result["upload_speed"]   = (counters2.bytes_sent - counters1.bytes_sent) / interval
        result["download_speed"] = (counters2.bytes_recv - counters1.bytes_recv) / interval
        net_if_stats = psutil.net_if_stats()
        for iface, stats in net_if_stats.items():
            if stats.isup and iface != "lo":
                result["interface"]    = iface
                result["is_connected"] = True
                break
    except Exception:
        pass
    return result


def get_ping(host: str = "8.8.8.8") -> dict:
    """Ping a host and return latency in ms."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", host],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "time=" in line:
                    ms = float(line.split("time=")[1].split()[0])
                    if ms < 20:
                        quality = "Excellent"
                        color   = "#06d6a0"
                    elif ms < 50:
                        quality = "Good"
                        color   = "#06d6a0"
                    elif ms < 100:
                        quality = "Fair"
                        color   = "#ffd000"
                    else:
                        quality = "Poor"
                        color   = "#ff4d6d"
                    return {"ms": ms, "quality": quality, "color": color, "success": True}
        return {"success": False, "error": "No response"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_speed(bytes_per_sec: float) -> str:
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    else:
        return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"


class SpeedTestWorker(QObject):
    """Runs speed test in background thread."""
    finished = Signal(dict)

    def run(self):
        try:
            import speedtest
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1_000_000  # Convert to Mbps
            upload   = st.upload() / 1_000_000
            self.finished.emit({
                "success":  True,
                "download": round(download, 1),
                "upload":   round(upload, 1),
            })
        except Exception as e:
            self.finished.emit({"success": False, "error": str(e)})


class NetworkPanel(BasePanel):
    """Displays network upload/download speeds, ping, and speed test."""

    REFRESH_INTERVAL = 2000
    ACCENT_COLOR = "#9b5de5"

    def __init__(self, settings: Settings, parent=None):
        self._download_label  = None
        self._upload_label    = None
        self._interface_label = None
        self._status_label    = None
        self._ping_label      = None
        self._ping_host_label = None
        self._speed_down      = None
        self._speed_up        = None
        self._speed_time      = None
        self._speed_btn       = None
        self._speed_worker    = None
        self._ping_timer      = None
        super().__init__(settings, title="Network", parent=parent)
        # Delay ping start to allow network to be ready
        from PySide6.QtCore import QTimer
        QTimer.singleShot(3000, self._start_ping_timer)

    def build_content(self, layout: QVBoxLayout):
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

        # Interface + status
        self._interface_label = self.make_unit_label("")
        self._status_label    = self.make_unit_label("")

        layout.addWidget(dl_row)
        layout.addWidget(ul_row)
        layout.addWidget(self._interface_label)
        layout.addWidget(self._status_label)
        layout.addSpacing(8)

        # Ping section
        ping_header = QLabel("PING")
        ping_header.setStyleSheet(
            "color: rgba(240,240,255,0.35); font-size: 10px;"
            "font-weight: 700; letter-spacing: 0.1em;"
        )

        ping_row = QWidget()
        ping_layout = QHBoxLayout(ping_row)
        ping_layout.setContentsMargins(0, 0, 0, 0)
        ping_layout.setSpacing(8)

        ping_host = self.settings._data.get("network", {}).get("ping_host", "8.8.8.8")
        self._ping_host_label = QLabel(ping_host)
        self._ping_host_label.setObjectName("panel-subtitle")

        self._ping_label = QLabel("-- ms")
        self._ping_label.setObjectName("panel-subtitle")
        self._ping_label.setAlignment(Qt.AlignRight)
        self._ping_label.setStyleSheet("color: #06d6a0;")

        ping_layout.addWidget(self._ping_host_label)
        ping_layout.addStretch()
        ping_layout.addWidget(self._ping_label)

        layout.addWidget(ping_header)
        layout.addWidget(ping_row)
        layout.addSpacing(8)

        # Speed test section
        speed_header = QLabel("SPEED TEST")
        speed_header.setStyleSheet(
            "color: rgba(240,240,255,0.35); font-size: 10px;"
            "font-weight: 700; letter-spacing: 0.1em;"
        )

        speed_results = QWidget()
        speed_layout  = QHBoxLayout(speed_results)
        speed_layout.setContentsMargins(0, 0, 0, 0)
        speed_layout.setSpacing(16)

        self._speed_down = QLabel("↓ --")
        self._speed_down.setObjectName("panel-subtitle")
        self._speed_down.setStyleSheet("color: #06d6a0;")

        self._speed_up = QLabel("↑ --")
        self._speed_up.setObjectName("panel-subtitle")
        self._speed_up.setStyleSheet("color: #4361ee;")

        speed_layout.addWidget(self._speed_down)
        speed_layout.addWidget(self._speed_up)
        speed_layout.addStretch()

        self._speed_time = self.make_unit_label("")
        self._speed_btn  = QPushButton("Run Test")
        self._speed_btn.setFixedHeight(28)
        self._speed_btn.setFixedWidth(90)
        self._speed_btn.clicked.connect(self._run_speed_test)

        layout.addWidget(speed_header)
        layout.addWidget(speed_results)
        layout.addWidget(self._speed_time)
        layout.addWidget(self._speed_btn)

    def _start_ping_timer(self):
        """Start a separate timer for ping updates every 5 seconds."""
        self._ping_timer = QTimer(self)
        self._ping_timer.timeout.connect(self._update_ping)
        self._ping_timer.start(5000)
        self._update_ping()

    def _update_ping(self):
        """Update ping in a background thread."""
        host = self.settings._data.get("network", {}).get("ping_host", "8.8.8.8")
        def ping_thread():
            result = get_ping(host)
            if result.get("success"):
                self._ping_label.setText(f"{result['ms']:.0f} ms  {result['quality']}")
                self._ping_label.setStyleSheet(f"color: {result['color']};")
            else:
                self._ping_label.setText("Timeout")
                self._ping_label.setStyleSheet("color: rgba(240,240,255,0.3);")
        t = threading.Thread(target=ping_thread, daemon=True)
        t.start()

    def _run_speed_test(self):
        """Run internet speed test in background."""
        if self._speed_btn is None:
            return
        self._speed_btn.setEnabled(False)
        self._speed_btn.setText("Testing...")
        self._speed_down.setText("↓ --")
        self._speed_up.setText("↑ --")
        self._speed_time.setText("Running speed test...")

        self._speed_worker = SpeedTestWorker()
        self._speed_worker.finished.connect(self._on_speed_test_done)
        t = threading.Thread(target=self._speed_worker.run, daemon=True)
        t.start()

    def _on_speed_test_done(self, result: dict):
        """Update UI with speed test results."""
        if self._speed_btn is None:
            return
        self._speed_btn.setEnabled(True)
        self._speed_btn.setText("Run Test")
        if result.get("success"):
            self._speed_down.setText(f"↓ {result['download']} Mbps")
            self._speed_up.setText(f"↑ {result['upload']} Mbps")
            from PySide6.QtCore import QDateTime
            self._speed_time.setText(f"Last tested: {QDateTime.currentDateTime().toString('h:mm AP')}")
        else:
            self._speed_time.setText(f"Test failed: {result.get('error', 'Unknown error')}")

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