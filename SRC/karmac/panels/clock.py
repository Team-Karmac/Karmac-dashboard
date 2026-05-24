"""
Karmac Dashboard — Clock & Date Panel
Displays the current time and date with configurable format and timezone.
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QDateTime, QTimer, QTimeZone
from PySide6.QtGui import QFont
from karmac.panels.base import BasePanel
from karmac.settings import Settings


class ClockPanel(BasePanel):
    """Displays the current time and date."""

    REFRESH_INTERVAL = 1000
    ACCENT_COLOR = "#4361ee"

    def __init__(self, settings: Settings, parent=None):
        self._time_label = None
        self._date_label = None
        super().__init__(settings, title="Clock", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        self._time_label = QLabel()
        self._time_label.setObjectName("panel-value")
        self._time_label.setAlignment(Qt.AlignLeft)

        font = self._time_label.font()
        font.setPointSize(36)
        font.setWeight(QFont.Weight.Light)
        self._time_label.setFont(font)

        self._date_label = self.make_subtitle_label()

        layout.addWidget(self._time_label)
        layout.addWidget(self._date_label)

    def refresh(self):
        if self._time_label is None:
            return

        clock_settings = self.settings.clock

        # Handle timezone
        tz = clock_settings.get("timezone", "local")
        if tz == "local" or not tz:
            now = QDateTime.currentDateTime()
        else:
            try:
                qt_tz = QTimeZone(tz.encode())
                now = QDateTime.currentDateTime().toTimeZone(qt_tz)
            except Exception:
                now = QDateTime.currentDateTime()

        # Time format
        if clock_settings.get("format_24h", False):
            time_fmt = "HH:mm:ss" if clock_settings.get("show_seconds", True) else "HH:mm"
        else:
            time_fmt = "h:mm:ss AP" if clock_settings.get("show_seconds", True) else "h:mm AP"

        # Date format
        date_fmt_key = clock_settings.get("date_format", "long")
        if date_fmt_key == "short":
            date_fmt = "MM/dd/yyyy"
        elif date_fmt_key == "iso":
            date_fmt = "yyyy-MM-dd"
        else:
            date_fmt = "dddd, MMMM d, yyyy"

        self._time_label.setText(now.toString(time_fmt))
        self._date_label.setText(now.toString(date_fmt))