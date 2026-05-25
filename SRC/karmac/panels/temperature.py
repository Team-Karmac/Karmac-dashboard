"""
Karmac Dashboard — CPU & GPU Temperature Panel
Displays real-time CPU and GPU temperatures with configurable thresholds.
"""

import psutil
import glob
import os
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


# Known CPU chip prefixes
CPU_CHIP_PREFIXES = ("k10temp", "coretemp", "zenpower", "cpu")

# Known GPU chip prefixes
GPU_CHIP_PREFIXES = ("amdgpu", "nvidia", "radeon", "nouveau")

# Known temperature sensor keys for each chip type
CPU_TEMP_KEYS = ("Tctl", "Tdie", "Package id 0", "Core 0", "temp1")
GPU_TEMP_KEYS = ("edge", "junction", "temp1", "GPU Temperature")


def get_temperatures() -> dict:
    """
    Read CPU and GPU temperatures from the system.
    Returns dict with 'cpu' and 'gpu' keys, each containing
    a list of {label, temp_c} dicts.
    """
    result = {"cpu": [], "gpu": []}

    try:
        sensors = psutil.sensors_temperatures()
        if not sensors:
            return result

        for chip_name, entries in sensors.items():
            lower = chip_name.lower()

            is_cpu = any(lower.startswith(p) for p in CPU_CHIP_PREFIXES)
            is_gpu = any(lower.startswith(p) for p in GPU_CHIP_PREFIXES)

            if not is_cpu and not is_gpu:
                continue

            for entry in entries:
                label = entry.label or "Temp"
                temp  = entry.current

                if temp is None or temp <= 0:
                    continue

                reading = {"label": label, "temp_c": round(temp, 1), "chip": chip_name}

                if is_cpu:
                    result["cpu"].append(reading)
                elif is_gpu:
                    result["gpu"].append(reading)

    except Exception:
        pass

    return result


def c_to_f(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return round(celsius * 9 / 5 + 32, 1)


def format_temp(celsius: float, units: str) -> str:
    """Format temperature in the requested units."""
    if units == "fahrenheit":
        return f"{c_to_f(celsius)}°F"
    return f"{celsius}°C"


class TemperaturePanel(BasePanel):
    """Displays CPU and GPU temperatures."""

    REFRESH_INTERVAL = 3000
    ACCENT_COLOR = "#ff6d00"

    def __init__(self, settings: Settings, parent=None):
        self._temp_widgets = []
        super().__init__(settings, title="Temperature", parent=parent)
        self.setMinimumHeight(180)

    def build_content(self, layout: QVBoxLayout):
        self._temp_container = QVBoxLayout()
        self._temp_container.setSpacing(8)
        self._temp_container.setContentsMargins(0, 4, 0, 4)
        layout.addLayout(self._temp_container)

        self._no_temp_label = self.make_subtitle_label("No temperature sensors detected")
        self._no_temp_label.hide()
        layout.addWidget(self._no_temp_label)

    def refresh(self):
        if not hasattr(self, '_temp_container'):
            return

        for w in self._temp_widgets:
            w.setParent(None)
            w.deleteLater()
        self._temp_widgets.clear()

        data = get_temperatures()
        temp_cfg = self.settings._data.get("temperature", {})
        units = temp_cfg.get("units", "celsius")
        show  = temp_cfg.get("show", "celsius")
        warn  = temp_cfg.get("warning", 70)
        crit  = temp_cfg.get("critical", 90)

        if not data["cpu"] and not data["gpu"]:
            self._no_temp_label.show()
            return

        self._no_temp_label.hide()

        # CPU section
        if data["cpu"]:
            header = self._make_header("CPU")
            self._temp_container.addWidget(header)
            self._temp_widgets.append(header)

            # Show the most relevant CPU temp readings
            shown = []
            for reading in data["cpu"]:
                if reading["label"] in CPU_TEMP_KEYS:
                    shown.append(reading)
            if not shown:
                shown = data["cpu"][:2]

            for reading in shown[:3]:  # Max 3 CPU readings
                row = self._make_temp_row(
                    reading["label"], reading["temp_c"], units, warn, crit
                )
                self._temp_container.addWidget(row)
                self._temp_widgets.append(row)

        # Spacer between CPU and GPU
        if data["cpu"] and data["gpu"]:
            spacer = QWidget()
            spacer.setFixedHeight(8)
            self._temp_container.addWidget(spacer)
            self._temp_widgets.append(spacer)

        # GPU section
        if data["gpu"]:
            header = self._make_header("GPU")
            self._temp_container.addWidget(header)
            self._temp_widgets.append(header)

            # Show edge/junction temps for GPU
            shown = []
            for reading in data["gpu"]:
                if reading["label"] in GPU_TEMP_KEYS:
                    shown.append(reading)
            if not shown:
                shown = data["gpu"][:2]

            for reading in shown[:2]:  # Max 2 GPU readings
                row = self._make_temp_row(
                    reading["label"], reading["temp_c"], units, warn, crit
                )
                self._temp_container.addWidget(row)
                self._temp_widgets.append(row)

    def _make_header(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "color: rgba(240,240,255,0.35);"
            "font-size: 10px;"
            "font-weight: 700;"
            "letter-spacing: 0.1em;"
            "padding-bottom: 2px;"
        )
        return label

    def _make_temp_row(self, label: str, temp_c: float, units: str,
                       warn: float, crit: float) -> QWidget:
        row = QWidget()
        row.setMinimumHeight(24)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(8)

        name = QLabel(label)
        name.setObjectName("panel-subtitle")
        name.setMinimumWidth(80)

        # Primary temp in chosen units
        primary = format_temp(temp_c, units)

        # Secondary temp in other units
        if units == "fahrenheit":
            secondary = f"{temp_c}°C"
        else:
            secondary = f"{c_to_f(temp_c)}°F"

        # Color based on thresholds
        if temp_c >= crit:
            color = "#ff4d6d"
        elif temp_c >= warn:
            color = "#ffd000"
        else:
            color = "#06d6a0"

        temp_label = QLabel(f"{primary}  {secondary}")
        temp_label.setObjectName("panel-subtitle")
        temp_label.setAlignment(Qt.AlignRight)
        temp_label.setMinimumWidth(140)
        temp_label.setStyleSheet(f"color: {color};")

        layout.addWidget(name)
        layout.addStretch()
        layout.addWidget(temp_label)

        return row