"""
Karmac Dashboard — GPU Usage Panel
Displays AMD GPU usage percentage and related stats.
"""

import glob
import os
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


def get_gpu_usage() -> dict:
    """Read GPU usage from sysfs."""
    result = {"success": False, "usage": 0, "vram_used": 0, "vram_total": 0, "power": 0}
    try:
        # GPU busy percent
        for path in glob.glob("/sys/class/drm/card*/device/gpu_busy_percent"):
            with open(path) as f:
                result["usage"] = int(f.read().strip())
            result["success"] = True
            card_path = os.path.dirname(path)

            # VRAM usage
            vram_used_path  = os.path.join(card_path, "mem_info_vram_used")
            vram_total_path = os.path.join(card_path, "mem_info_vram_total")
            if os.path.exists(vram_used_path) and os.path.exists(vram_total_path):
                with open(vram_used_path) as f:
                    result["vram_used"] = int(f.read().strip())
                with open(vram_total_path) as f:
                    result["vram_total"] = int(f.read().strip())

            # Power usage
            power_path = os.path.join(card_path, "hwmon")
            for hwmon in glob.glob(os.path.join(power_path, "hwmon*")):
                for power_file in glob.glob(os.path.join(hwmon, "power1_average")):
                    with open(power_file) as f:
                        result["power"] = int(f.read().strip()) // 1_000_000  # Convert to watts
            break
    except Exception:
        pass
    return result


def format_vram(bytes_val: int) -> str:
    """Format VRAM bytes to MB or GB."""
    if bytes_val >= 1024 ** 3:
        return f"{bytes_val / (1024 ** 3):.1f} GB"
    return f"{bytes_val / (1024 ** 2):.0f} MB"


def usage_color(pct: float) -> str:
    if pct >= 90:
        return "#ff4d6d"
    elif pct >= 70:
        return "#ffd000"
    else:
        return "#c77dff"


class GpuUsagePanel(BasePanel):
    """Displays AMD GPU usage percentage and VRAM."""

    REFRESH_INTERVAL = 2000
    ACCENT_COLOR = "#c77dff"

    def __init__(self, settings: Settings, parent=None):
        self._usage_label = None
        self._vram_label  = None
        self._power_label = None
        self._bar_label   = None
        super().__init__(settings, title="GPU Usage", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        # Main usage row
        main_row = QWidget()
        main_layout = QHBoxLayout(main_row)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        self._usage_label = self.make_value_label("--%")
        font = self._usage_label.font()
        font.setPointSize(34)
        self._usage_label.setFont(font)

        main_layout.addWidget(self._usage_label)
        main_layout.addStretch()

        self._vram_label  = self.make_subtitle_label("")
        self._power_label = self.make_unit_label("")

        layout.addWidget(main_row)
        layout.addWidget(self._vram_label)
        layout.addWidget(self._power_label)

    def refresh(self):
        if self._usage_label is None:
            return

        info = get_gpu_usage()

        if not info.get("success"):
            self._usage_label.setText("N/A")
            self._vram_label.setText("GPU usage not available")
            return

        pct = info["usage"]
        color = usage_color(pct)

        self._usage_label.setText(f"{pct}%")
        self._usage_label.setStyleSheet(f"color: {color}; font-size: 34px; font-weight: 300;")

        # VRAM
        if info["vram_total"] > 0:
            vram_pct = (info["vram_used"] / info["vram_total"]) * 100
            self._vram_label.setText(
                f"VRAM  {format_vram(info['vram_used'])} / {format_vram(info['vram_total'])}  ({vram_pct:.0f}%)"
            )

        # Power
        if info["power"] > 0:
            self._power_label.setText(f"Power  {info['power']} W")