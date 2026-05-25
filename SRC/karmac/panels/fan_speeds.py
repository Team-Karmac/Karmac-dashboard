"""
Karmac Dashboard — Fan Speeds Panel
Displays RPM readings for all detected system fans, grouped by hardware chip.
"""

import psutil
import glob
import os
import re
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


GPU_CHIP_PREFIXES = ("amdgpu", "nvidia", "radeon", "nouveau")

CHIP_FRIENDLY_NAMES = {
    "nzxtsmart2":  "NZXT Smart Device",
    "nzxtsmart":   "NZXT Smart Device",
    "k10temp":     "AMD CPU",
    "coretemp":    "Intel CPU",
    "amdgpu":      "AMD GPU",
    "nvidia":      "NVIDIA GPU",
    "radeon":      "AMD Radeon",
    "nouveau":     "NVIDIA (nouveau)",
    "asus":        "ASUS Motherboard",
    "it8":         "Motherboard",
    "nct6":        "Motherboard",
    "w83":         "Motherboard",
}


def friendly_chip_name(raw_name: str) -> str:
    lower = raw_name.lower()
    for key, friendly in CHIP_FRIENDLY_NAMES.items():
        if lower.startswith(key):
            return friendly
    return raw_name.upper()


def is_gpu_chip(chip_name: str) -> bool:
    lower = chip_name.lower()
    return any(lower.startswith(prefix) for prefix in GPU_CHIP_PREFIXES)


def get_fan_speeds() -> dict:
    grouped = {}

    try:
        sensors = psutil.sensors_fans()
        if sensors:
            for chip_name, entries in sensors.items():
                fans = []
                for entry in entries:
                    fans.append({
                        "label": entry.label or "Fan",
                        "rpm":   int(entry.current),
                    })
                if fans:
                    grouped[chip_name] = fans
            if grouped:
                return grouped
    except (AttributeError, Exception):
        pass

    try:
        for hwmon_path in glob.glob("/sys/class/hwmon/hwmon*"):
            name_file = os.path.join(hwmon_path, "name")
            chip_name = "unknown"
            if os.path.exists(name_file):
                with open(name_file) as f:
                    chip_name = f.read().strip()

            fans = []
            for fan_input in sorted(glob.glob(os.path.join(hwmon_path, "fan*_input"))):
                try:
                    with open(fan_input) as f:
                        rpm = int(f.read().strip())
                    label_file = fan_input.replace("_input", "_label")
                    if os.path.exists(label_file):
                        with open(label_file) as f:
                            label = f.read().strip()
                    else:
                        m = re.search(r"fan(\d+)_input", fan_input)
                        label = f"Fan {m.group(1)}" if m else "Fan"
                    fans.append({"label": label, "rpm": rpm})
                except (ValueError, IOError):
                    continue

            if fans:
                grouped[chip_name] = fans

    except Exception:
        pass

    return grouped


class FanSpeedsPanel(BasePanel):
    """Displays RPM readings for all detected system fans, grouped by chip."""

    REFRESH_INTERVAL = 3000
    ACCENT_COLOR = "#ffd000"

    def __init__(self, settings: Settings, parent=None):
        self._fan_widgets = []
        self._no_fans_label = None
        super().__init__(settings, title="Fan Speeds", parent=parent)
        # Ensure the panel is tall enough to show all fans comfortably
        self.setMinimumHeight(240)

    def build_content(self, layout: QVBoxLayout):
        self._fan_container = QVBoxLayout()
        self._fan_container.setSpacing(8)
        self._fan_container.setContentsMargins(0, 4, 0, 4)
        layout.addLayout(self._fan_container)

        self._no_fans_label = self.make_subtitle_label("No fans detected")
        self._no_fans_label.hide()
        layout.addWidget(self._no_fans_label)

    def refresh(self):
        if not hasattr(self, '_fan_container'):
            return

        for w in self._fan_widgets:
            w.setParent(None)
            w.deleteLater()
        self._fan_widgets.clear()

        grouped = get_fan_speeds()

        if not grouped:
            self._no_fans_label.show()
            return

        self._no_fans_label.hide()
        first_group = True

        for chip_name, fans in grouped.items():
            if not first_group:
                spacer = QWidget()
                spacer.setFixedHeight(8)
                self._fan_container.addWidget(spacer)
                self._fan_widgets.append(spacer)

            # Chip header
            header = QLabel(friendly_chip_name(chip_name))
            header.setStyleSheet(
                "color: rgba(240,240,255,0.35);"
                "font-size: 10px;"
                "font-weight: 700;"
                "letter-spacing: 0.1em;"
                "padding-bottom: 2px;"
            )
            self._fan_container.addWidget(header)
            self._fan_widgets.append(header)

            for fan in fans:
                row = self._make_fan_row(fan["label"], fan["rpm"], chip_name)
                self._fan_container.addWidget(row)
                self._fan_widgets.append(row)

            first_group = False

    def _make_fan_row(self, label: str, rpm: int, chip_name: str) -> QWidget:
        rpm_warning  = self.settings.fans.get('rpm_warning', 2000)
        rpm_critical = self.settings.fans.get('rpm_critical', 3000)
        row = QWidget()
        row.setMinimumHeight(24)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(8)

        custom_label = self.settings.get_fan_label(label)
        name = QLabel(custom_label.title())
        name.setObjectName("panel-subtitle")
        name.setMinimumWidth(80)

        gpu = is_gpu_chip(chip_name)

        if rpm == 0 and gpu:
            display = "Zero RPM"
            color = "#06d6a0"
        elif rpm == 0:
            display = "Off"
            color = "rgba(240,240,255,0.25)"
        elif rpm < rpm_warning:
            display = f"{rpm:,} RPM"
            color = "#06d6a0"
        elif rpm < rpm_critical:
            display = f"{rpm:,} RPM"
            color = "#ffd000"
        else:
            display = f"{rpm:,} RPM"
            color = "#ff4d6d"

        rpm_label = QLabel(display)
        rpm_label.setObjectName("panel-subtitle")
        rpm_label.setAlignment(Qt.AlignRight)
        rpm_label.setMinimumWidth(90)
        rpm_label.setStyleSheet(f"color: {color};")

        layout.addWidget(name)
        layout.addStretch()
        layout.addWidget(rpm_label)

        return row