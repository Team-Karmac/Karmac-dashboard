"""
Karmac Dashboard — Clock, Date & Calendar Panel
Displays current time, date, and a mini calendar with today highlighted.
"""

import calendar
from datetime import datetime
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout
from PySide6.QtCore import Qt, QDateTime, QTimer, QTimeZone
from PySide6.QtGui import QFont
from karmac.panels.base import BasePanel
from karmac.settings import Settings


class ClockPanel(BasePanel):
    """Displays current time, date and a mini calendar."""

    REFRESH_INTERVAL = 1000
    ACCENT_COLOR = "#4361ee"

    def __init__(self, settings: Settings, parent=None):
        self._time_label   = None
        self._date_label   = None
        self._cal_title    = None
        self._cal_grid     = None
        self._last_month   = None
        self._last_year    = None
        self._day_labels   = {}
        super().__init__(settings, title="Clock", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        # Time display
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
        layout.addSpacing(10)

        # Calendar section
        cal_header = QLabel("CALENDAR")
        cal_header.setStyleSheet(
            "color: rgba(240,240,255,0.35);"
            "font-size: 10px;"
            "font-weight: 700;"
            "letter-spacing: 0.1em;"
        )
        layout.addWidget(cal_header)
        layout.addSpacing(4)

        # Month/year title
        self._cal_title = QLabel()
        self._cal_title.setStyleSheet(
            "color: rgba(240,240,255,0.7);"
            "font-size: 11px;"
            "font-weight: 600;"
            "letter-spacing: 0.05em;"
        )
        layout.addWidget(self._cal_title)
        layout.addSpacing(4)

        # Calendar grid
        self._cal_widget = QWidget()
        self._cal_grid   = QGridLayout(self._cal_widget)
        self._cal_grid.setContentsMargins(0, 0, 0, 0)
        self._cal_grid.setSpacing(2)
        self._cal_grid.setHorizontalSpacing(4)

        # Day headers
        day_headers = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for col, day in enumerate(day_headers):
            lbl = QLabel(day)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedWidth(26)
            if day in ("Sa", "Su"):
                lbl.setStyleSheet("color: rgba(240,240,255,0.3); font-size: 10px; font-weight: 600;")
            else:
                lbl.setStyleSheet("color: rgba(240,240,255,0.35); font-size: 10px; font-weight: 600;")
            self._cal_grid.addWidget(lbl, 0, col)

        layout.addWidget(self._cal_widget)

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

        # Update calendar
        today = datetime.now()
        if today.month != self._last_month or today.year != self._last_year:
            self._build_calendar(today)
            self._last_month = today.month
            self._last_year  = today.year
        else:
            # Just update today's highlight
            self._highlight_today(today.day)

    def _build_calendar(self, today: datetime):
        """Build the calendar grid for the current month."""
        # Clear existing day cells (keep header row)
        for key, lbl in self._day_labels.items():
            lbl.setParent(None)
        self._day_labels.clear()

        # Month title
        self._cal_title.setText(today.strftime("%B %Y"))

        # Get calendar data
        cal = calendar.monthcalendar(today.year, today.month)

        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    lbl = QLabel("")
                else:
                    lbl = QLabel(str(day))

                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFixedWidth(26)
                lbl.setFixedHeight(20)

                if day == today.day:
                    # Today — highlighted
                    lbl.setStyleSheet("""
                        background-color: #4361ee;
                        color: #ffffff;
                        border-radius: 4px;
                        font-size: 10px;
                        font-weight: 700;
                    """)
                elif col_idx >= 5:
                    # Weekend
                    lbl.setStyleSheet("color: rgba(240,240,255,0.4); font-size: 10px;")
                else:
                    lbl.setStyleSheet("color: rgba(240,240,255,0.65); font-size: 10px;")

                self._cal_grid.addWidget(lbl, row_idx + 1, col_idx)
                if day != 0:
                    self._day_labels[day] = lbl

    def _highlight_today(self, today_day: int):
        """Update only the today highlight without rebuilding the whole calendar."""
        for day, lbl in self._day_labels.items():
            if day == today_day:
                lbl.setStyleSheet("""
                    background-color: #4361ee;
                    color: #ffffff;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: 700;
                """)