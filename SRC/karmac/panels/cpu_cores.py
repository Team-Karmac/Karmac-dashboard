"""
Karmac Dashboard — CPU Core Activity Panel
Displays overall CPU usage, frequency, and individual core breakdown with frequencies.
"""

import psutil
import os
import glob
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout
from PySide6.QtCore import Qt
from karmac.panels.base import BasePanel
from karmac.settings import Settings


def get_cpu_info() -> dict:
    """Read CPU usage for overall and per core, plus per-core frequencies."""
    try:
        overall   = psutil.cpu_percent(interval=None)
        per_core  = psutil.cpu_percent(interval=None, percpu=True)
        freq      = psutil.cpu_freq()
        count_physical = psutil.cpu_count(logical=False)
        count_logical  = psutil.cpu_count(logical=True)

        # Read per-core frequencies from sysfs
        per_core_freq = []
        for i in range(count_logical):
            path = f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq"
            try:
                with open(path) as f:
                    khz = int(f.read().strip())
                    per_core_freq.append(round(khz / 1_000_000, 2))
            except Exception:
                per_core_freq.append(None)

        return {
            "overall":        overall,
            "per_core":       per_core,
            "per_core_freq":  per_core_freq,
            "freq_mhz":       round(freq.current) if freq else None,
            "count_physical": count_physical,
            "count_logical":  count_logical,
            "success":        True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


GREEN  = "#06d6a0"
YELLOW = "#ffd000"
RED    = "#ff4d6d"

def usage_color(pct: float, warning: float = 70, critical: float = 90) -> str:
    if pct >= critical:
        return RED
    elif pct >= warning:
        return YELLOW
    else:
        return GREEN


def freq_color(ghz: float) -> str:
    """Color based on frequency — higher = warmer color."""
    if ghz >= 4.0:
        return RED
    elif ghz >= 3.5:
        return YELLOW
    else:
        return "rgba(240,240,255,0.45)"


class CpuCoresPanel(BasePanel):
    """Displays overall CPU usage, frequency, and per-core breakdown."""

    REFRESH_INTERVAL = 1000
    ACCENT_COLOR = "#ff006e"

    def __init__(self, settings: Settings, parent=None):
        self._overall_label  = None
        self._freq_label     = None
        self._cores_grid     = None
        self._core_pct_labels  = []
        self._core_freq_labels = []
        super().__init__(settings, title="CPU Cores", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        # Overall usage row
        overall_row = QWidget()
        overall_layout = QHBoxLayout(overall_row)
        overall_layout.setContentsMargins(0, 0, 0, 0)
        overall_layout.setSpacing(8)

        overall_title = QLabel("Overall")
        overall_title.setObjectName("panel-subtitle")

        self._overall_label = QLabel("--%")
        self._overall_label.setObjectName("panel-value")
        font = self._overall_label.font()
        font.setPointSize(28)
        self._overall_label.setFont(font)
        self._overall_label.setAlignment(Qt.AlignRight)

        overall_layout.addWidget(overall_title)
        overall_layout.addStretch()
        overall_layout.addWidget(self._overall_label)

        self._freq_label = self.make_unit_label("")

        layout.addWidget(overall_row)
        layout.addWidget(self._freq_label)
        layout.addSpacing(8)

        # Per core grid — 2 columns, each showing core number, %, and frequency
        self._cores_widget = QWidget()
        self._cores_grid   = QGridLayout(self._cores_widget)
        self._cores_grid.setContentsMargins(0, 0, 0, 0)
        self._cores_grid.setSpacing(4)
        self._cores_grid.setHorizontalSpacing(12)
        layout.addWidget(self._cores_widget)

    def refresh(self):
        if self._overall_label is None:
            return

        info = get_cpu_info()
        if not info.get("success"):
            return

        overall = info["overall"]
        cpu_cfg = self.settings._data.get("cpu", {})
        warn = cpu_cfg.get("warning", 70)
        crit = cpu_cfg.get("critical", 90)
        self._overall_label.setText(f"{overall:.0f}%")
        self._overall_label.setStyleSheet(f"color: {usage_color(overall, warn, crit)}; font-size: 28px; font-weight: 300;")

        if info["freq_mhz"]:
            ghz = info["freq_mhz"] / 1000
            self._freq_label.setText(
                f"{ghz:.2f} GHz  —  {info['count_physical']} cores / {info['count_logical']} threads"
            )

        per_core      = info["per_core"]
        per_core_freq = info["per_core_freq"]

        # Rebuild grid if core count changed
        if len(self._core_pct_labels) != len(per_core):
            for label in self._core_pct_labels + self._core_freq_labels:
                label.setParent(None)
            self._core_pct_labels.clear()
            self._core_freq_labels.clear()

            for i, (pct, freq) in enumerate(zip(per_core, per_core_freq)):
                row = i // 2
                col = (i % 2) * 3  # 3 columns per core: name, pct, freq

                # Core name
                core_name = QLabel(f"C{i}")
                core_name.setObjectName("panel-unit")
                core_name.setFixedWidth(22)
                core_name.setObjectName("panel-unit")

                # Core percentage
                core_pct = QLabel(f"{pct:.0f}%")
                core_pct.setObjectName("panel-unit")
                core_pct.setFixedWidth(32)
                cpu_cfg = self.settings._data.get("cpu", {})
                warn = cpu_cfg.get("warning", 70)
                crit = cpu_cfg.get("critical", 90)
                core_pct.setStyleSheet(f"color: {usage_color(pct, warn, crit)};")

                # Core frequency
                freq_val = f"{freq:.1f}" if freq else "--"
                core_freq = QLabel(f"{freq_val}G")
                core_freq.setObjectName("panel-unit")
                core_freq.setFixedWidth(40)
                core_freq.setStyleSheet(f"color: {freq_color(freq if freq else 0)};")

                self._cores_grid.addWidget(core_name, row, col)
                self._cores_grid.addWidget(core_pct,  row, col + 1)
                self._cores_grid.addWidget(core_freq, row, col + 2)

                self._core_pct_labels.append(core_pct)
                self._core_freq_labels.append(core_freq)
        else:
            for i, (pct_label, freq_label, pct, freq) in enumerate(
                zip(self._core_pct_labels, self._core_freq_labels, per_core, per_core_freq)
            ):
                pct_label.setText(f"{pct:.0f}%")
                pct_label.setStyleSheet(f"color: {usage_color(pct)};")
                freq_val = f"{freq:.1f}" if freq else "--"
                freq_label.setText(f"{freq_val}G")
                freq_label.setStyleSheet(f"color: {freq_color(freq if freq else 0)};")