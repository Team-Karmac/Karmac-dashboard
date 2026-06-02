"""
Karmac Dashboard — FPS Panel
Displays live FPS and gaming stats from MangoHud log files.
"""

import os
import glob
import time
from pathlib import Path
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


MANGOHUD_LOG_DIR = Path.home() / ".local" / "share" / "MangoHud"


def get_latest_log() -> Path | None:
    """Find the most recently modified MangoHud log file."""
    try:
        logs = list(MANGOHUD_LOG_DIR.glob("*.csv"))
        if not logs:
            return None
        # Get most recently modified
        latest = max(logs, key=lambda p: p.stat().st_mtime)
        # Only consider it active if modified in the last 5 seconds
        if time.time() - latest.stat().st_mtime > 5:
            return None
        return latest
    except Exception:
        return None


def read_latest_frame(log_path: Path) -> dict | None:
    """Read the most recent frame data from the log file."""
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()

        # Find the header line (starts with "fps")
        header_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("fps,"):
                header_idx = i
                break

        if header_idx is None:
            return None

        headers = lines[header_idx].strip().split(",")

        # Get last data line
        data_lines = [l for l in lines[header_idx+1:] if l.strip() and not l.startswith("os")]
        if not data_lines:
            return None

        values = data_lines[-1].strip().split(",")
        if len(values) != len(headers):
            return None

        return dict(zip(headers, values))
    except Exception:
        return None


GREEN  = "#06d6a0"
YELLOW = "#ffd000"
RED    = "#ff4d6d"

def fps_color(fps: float, warning: float = 60, critical: float = 30) -> str:
    """FPS is inverse — lower is worse."""
    if fps >= warning:
        return GREEN
    elif fps >= critical:
        return YELLOW
    else:
        return RED


class FpsPanel(BasePanel):
    """Displays live FPS and gaming stats from MangoHud."""

    REFRESH_INTERVAL = 1000
    ACCENT_COLOR = "#ff6b6b"

    def __init__(self, settings: Settings, parent=None):
        self._fps_label       = None
        self._frametime_label = None
        self._game_label      = None
        self._gpu_load_label  = None
        self._cpu_load_label  = None
        self._gpu_temp_label  = None
        self._status_label    = None
        super().__init__(settings, title="FPS", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        # Game name
        self._game_label = self.make_unit_label("No active game")
        self._game_label.setObjectName("panel-unit")
        self._game_label.setStyleSheet("font-style: italic;")
        layout.addWidget(self._game_label)

        # Main FPS display
        fps_row = QWidget()
        fps_layout = QHBoxLayout(fps_row)
        fps_layout.setContentsMargins(0, 0, 0, 0)

        self._fps_label = self.make_value_label("--")
        font = self._fps_label.font()
        font.setPointSize(40)
        self._fps_label.setFont(font)

        fps_unit = QLabel("FPS")
        fps_unit.setObjectName("panel-subtitle")
        fps_unit.setAlignment(Qt.AlignBottom)
        fps_unit.setStyleSheet("color: rgba(240,240,255,0.4); padding-bottom: 8px;")

        fps_layout.addWidget(self._fps_label)
        fps_layout.addWidget(fps_unit)
        fps_layout.addStretch()

        self._frametime_label = self.make_unit_label("")
        layout.addWidget(fps_row)
        layout.addWidget(self._frametime_label)
        layout.addSpacing(8)

        # Stats grid
        stats_row = QWidget()
        stats_layout = QHBoxLayout(stats_row)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(16)

        # CPU load
        cpu_block = QWidget()
        cpu_layout = QVBoxLayout(cpu_block)
        cpu_layout.setContentsMargins(0, 0, 0, 0)
        cpu_layout.setSpacing(1)
        cpu_title = QLabel("CPU")
        cpu_title.setStyleSheet("color: rgba(240,240,255,0.35); font-size: 9px; font-weight: 700; letter-spacing: 0.1em;")
        self._cpu_load_label = QLabel("-- %")
        self._cpu_load_label.setObjectName("panel-subtitle")
        cpu_layout.addWidget(cpu_title)
        cpu_layout.addWidget(self._cpu_load_label)

        # GPU load
        gpu_block = QWidget()
        gpu_layout = QVBoxLayout(gpu_block)
        gpu_layout.setContentsMargins(0, 0, 0, 0)
        gpu_layout.setSpacing(1)
        gpu_title = QLabel("GPU")
        gpu_title.setStyleSheet("color: rgba(240,240,255,0.35); font-size: 9px; font-weight: 700; letter-spacing: 0.1em;")
        self._gpu_load_label = QLabel("-- %")
        self._gpu_load_label.setObjectName("panel-subtitle")
        gpu_layout.addWidget(gpu_title)
        gpu_layout.addWidget(self._gpu_load_label)

        # GPU temp
        temp_block = QWidget()
        temp_layout = QVBoxLayout(temp_block)
        temp_layout.setContentsMargins(0, 0, 0, 0)
        temp_layout.setSpacing(1)
        temp_title = QLabel("GPU TEMP")
        temp_title.setStyleSheet("color: rgba(240,240,255,0.35); font-size: 9px; font-weight: 700; letter-spacing: 0.1em;")
        self._gpu_temp_label = QLabel("-- °C")
        self._gpu_temp_label.setObjectName("panel-subtitle")
        temp_layout.addWidget(temp_title)
        temp_layout.addWidget(self._gpu_temp_label)

        stats_layout.addWidget(cpu_block)
        stats_layout.addWidget(gpu_block)
        stats_layout.addWidget(temp_block)
        stats_layout.addStretch()

        layout.addWidget(stats_row)

    def refresh(self):
        if self._fps_label is None:
            return

        log = get_latest_log()

        if log is None:
            self._fps_label.setText("--")
            self._fps_label.setStyleSheet("color: rgba(240,240,255,0.3); font-size: 40px; font-weight: 300;")
            self._game_label.setText("No active game")
            self._frametime_label.setText("")
            self._cpu_load_label.setText("-- %")
            self._gpu_load_label.setText("-- %")
            self._gpu_temp_label.setText("-- °C")
            return

        # Extract game name from filename
        game_name = log.stem.split("_")[0].replace("-", " ").title()
        self._game_label.setText(game_name)
        self._game_label.setStyleSheet("color: #ff6b6b; font-size: 11px; font-weight: 600;")

        frame = read_latest_frame(log)
        if not frame:
            return

        try:
            fps = float(frame.get("fps", 0))
            frametime = float(frame.get("frametime", 0))
            cpu_load  = frame.get("cpu_load", "--")
            gpu_load  = frame.get("gpu_load", "--")
            gpu_temp  = frame.get("gpu_temp", "--")

            self._fps_label.setText(f"{fps:.0f}")
            fps_cfg = self.settings._data.get("fps", {})
            fps_warn = fps_cfg.get("warning", 60)
            fps_crit = fps_cfg.get("critical", 30)
            self._fps_label.setStyleSheet(f"color: {fps_color(fps, fps_warn, fps_crit)}; font-size: 40px; font-weight: 300;")
            self._frametime_label.setText(f"{frametime:.1f} ms frametime")
            self._cpu_load_label.setText(f"{cpu_load} %")
            self._gpu_load_label.setText(f"{gpu_load} %")
            self._gpu_temp_label.setText(f"{gpu_temp} °C")

        except (ValueError, TypeError):
            pass