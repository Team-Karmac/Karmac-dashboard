"""
Karmac Dashboard — Power Usage Panel
Displays CPU and GPU power consumption in watts.
"""

import time
import glob
import os
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


RAPL_CPU_PATH  = "/sys/class/powercap/intel-rapl:0/energy_uj"
RAPL_CORE_PATH = "/sys/class/powercap/intel-rapl:0:0/energy_uj"

# Store previous readings for delta calculation
_last_cpu_energy  = None
_last_cpu_time    = None
_last_core_energy = None
_last_core_time   = None


def get_cpu_power() -> float:
    """Calculate CPU package power in watts using RAPL energy delta."""
    global _last_cpu_energy, _last_cpu_time
    try:
        with open(RAPL_CPU_PATH) as f:
            energy = int(f.read().strip())
        now = time.monotonic()

        if _last_cpu_energy is not None and _last_cpu_time is not None:
            delta_energy = energy - _last_cpu_energy
            delta_time   = now - _last_cpu_time
            if delta_time > 0 and delta_energy >= 0:
                watts = delta_energy / 1_000_000 / delta_time
                _last_cpu_energy = energy
                _last_cpu_time   = now
                return round(watts, 1)

        _last_cpu_energy = energy
        _last_cpu_time   = now
    except Exception:
        pass
    return 0.0


def get_gpu_power() -> float:
    """Read GPU power from hwmon."""
    try:
        for path in glob.glob("/sys/class/hwmon/hwmon*/power1_average"):
            with open(path) as f:
                return round(int(f.read().strip()) / 1_000_000, 1)
    except Exception:
        pass
    return 0.0


GREEN  = "#06d6a0"
YELLOW = "#ffd000"
RED    = "#ff4d6d"

def power_color(watts: float, warning: float = 150, critical: float = 250) -> str:
    if watts >= critical:
        return RED
    elif watts >= warning:
        return YELLOW
    else:
        return GREEN


class PowerPanel(BasePanel):
    """Displays system power consumption."""

    REFRESH_INTERVAL = 2000
    ACCENT_COLOR = "#00b4d8"

    def __init__(self, settings: Settings, parent=None):
        self._total_label = None
        self._cpu_label   = None
        self._gpu_label   = None
        super().__init__(settings, title="Power Usage", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        # Total power — large display
        total_row = QWidget()
        total_layout = QHBoxLayout(total_row)
        total_layout.setContentsMargins(0, 0, 0, 0)

        self._total_label = self.make_value_label("-- W")
        font = self._total_label.font()
        font.setPointSize(34)
        self._total_label.setFont(font)

        total_label = QLabel("Total")
        total_label.setObjectName("panel-subtitle")
        total_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        total_label.setStyleSheet("color: rgba(240,240,255,0.4); padding-bottom: 6px;")

        total_layout.addWidget(self._total_label)
        total_layout.addStretch()
        total_layout.addWidget(total_label)

        layout.addWidget(total_row)
        layout.addSpacing(8)

        # CPU row
        cpu_row = QWidget()
        cpu_layout = QHBoxLayout(cpu_row)
        cpu_layout.setContentsMargins(0, 0, 0, 0)
        cpu_layout.setSpacing(8)

        cpu_name = QLabel("CPU Package")
        cpu_name.setObjectName("panel-subtitle")

        self._cpu_label = QLabel("-- W")
        self._cpu_label.setObjectName("panel-subtitle")
        self._cpu_label.setAlignment(Qt.AlignRight)
        self._cpu_label.setObjectName("panel-subtitle")

        cpu_layout.addWidget(cpu_name)
        cpu_layout.addStretch()
        cpu_layout.addWidget(self._cpu_label)

        # GPU row
        gpu_row = QWidget()
        gpu_layout = QHBoxLayout(gpu_row)
        gpu_layout.setContentsMargins(0, 0, 0, 0)
        gpu_layout.setSpacing(8)

        gpu_name = QLabel("GPU")
        gpu_name.setObjectName("panel-subtitle")

        self._gpu_label = QLabel("-- W")
        self._gpu_label.setObjectName("panel-subtitle")
        self._gpu_label.setAlignment(Qt.AlignRight)
        self._gpu_label.setObjectName("panel-subtitle")

        gpu_layout.addWidget(gpu_name)
        gpu_layout.addStretch()
        gpu_layout.addWidget(self._gpu_label)

        layout.addWidget(cpu_row)
        layout.addWidget(gpu_row)

    def refresh(self):
        if self._total_label is None:
            return

        cpu_w = get_cpu_power()
        gpu_w = get_gpu_power()
        total = round(cpu_w + gpu_w, 1)

        self._cpu_label.setText(f"{cpu_w} W")
        self._gpu_label.setText(f"{gpu_w} W")

        if total > 0:
            self._total_label.setText(f"{total} W")
            power_cfg = self.settings._data.get("power", {})
            warn = power_cfg.get("warning", 150)
            crit = power_cfg.get("critical", 250)
            color = power_color(total, warn, crit)
            self._total_label.setStyleSheet(f"color: {color}; font-size: 34px; font-weight: 300;")
        else:
            self._total_label.setText("-- W")