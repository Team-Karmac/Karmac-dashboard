"""
Karmac Dashboard — Weather Panel
Displays current weather using the Open-Meteo API (no API key required).
"""

import requests
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from karmac.panels.base import BasePanel
from karmac.settings import Settings


# Text-based weather icons (avoids emoji rendering issues on Linux)
WEATHER_CODES = {
    0:  ("Clear Sky",          "SUN"),
    1:  ("Mainly Clear",       "SUN"),
    2:  ("Partly Cloudy",      "CLOUD"),
    3:  ("Overcast",           "CLOUD"),
    45: ("Foggy",              "FOG"),
    48: ("Icy Fog",            "FOG"),
    51: ("Light Drizzle",      "RAIN"),
    53: ("Drizzle",            "RAIN"),
    55: ("Heavy Drizzle",      "RAIN"),
    61: ("Light Rain",         "RAIN"),
    63: ("Rain",               "RAIN"),
    65: ("Heavy Rain",         "RAIN"),
    71: ("Light Snow",         "SNOW"),
    73: ("Snow",               "SNOW"),
    75: ("Heavy Snow",         "SNOW"),
    77: ("Snow Grains",        "SNOW"),
    80: ("Light Showers",      "RAIN"),
    81: ("Showers",            "RAIN"),
    82: ("Heavy Showers",      "RAIN"),
    85: ("Snow Showers",       "SNOW"),
    86: ("Heavy Snow Showers", "SNOW"),
    95: ("Thunderstorm",       "STORM"),
    96: ("Thunderstorm",       "STORM"),
    99: ("Thunderstorm",       "STORM"),
}

# Color per weather type
ICON_COLORS = {
    "SUN":   "#ffbe0b",
    "CLOUD": "rgba(240,240,255,0.5)",
    "FOG":   "rgba(240,240,255,0.4)",
    "RAIN":  "#4361ee",
    "SNOW":  "#a0c4ff",
    "STORM": "#ff4d6d",
}


class WeatherFetcher(QThread):
    """Background thread for fetching weather data."""
    data_ready = Signal(dict)
    error = Signal(str)

    def __init__(self, latitude: float, longitude: float, units: str = "celsius"):
        super().__init__()
        self.latitude = latitude
        self.longitude = longitude
        self.units = units

    def run(self):
        try:
            temp_unit = "celsius" if self.units == "celsius" else "fahrenheit"
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={self.latitude}"
                f"&longitude={self.longitude}"
                f"&current=temperature_2m,weathercode,windspeed_10m,relativehumidity_2m"
                f"&temperature_unit={temp_unit}"
                f"&timezone=auto"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.data_ready.emit(response.json())
        except requests.exceptions.ConnectionError:
            self.error.emit("No internet connection")
        except requests.exceptions.Timeout:
            self.error.emit("Request timed out")
        except Exception as e:
            self.error.emit(str(e))


class WeatherPanel(BasePanel):
    """Displays current weather conditions using Open-Meteo."""

    REFRESH_INTERVAL = 600000
    ACCENT_COLOR = "#06d6a0"

    def __init__(self, settings: Settings, parent=None):
        self._icon_label = None
        self._temp_label = None
        self._condition_label = None
        self._detail_label = None
        self._location_label = None
        self._fetcher = None
        super().__init__(settings, title="Weather", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        # Top row: icon badge + temperature
        top_row = QWidget()
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(14)
        top_layout.setAlignment(Qt.AlignLeft)

        # Icon badge
        self._icon_label = QLabel("—")
        self._icon_label.setFixedSize(48, 48)
        self._icon_label.setAlignment(Qt.AlignCenter)
        self._icon_label.setStyleSheet("""
            background-color: rgba(6, 214, 160, 0.12);
            border-radius: 12px;
            color: #06d6a0;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.05em;
        """)

        # Temp + condition
        right_block = QWidget()
        right_layout = QVBoxLayout(right_block)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(2)

        self._temp_label = self.make_value_label("--°")
        self._condition_label = self.make_subtitle_label("Loading...")

        right_layout.addWidget(self._temp_label)
        right_layout.addWidget(self._condition_label)

        top_layout.addWidget(self._icon_label)
        top_layout.addWidget(right_block)
        top_layout.addStretch()

        self._detail_label = self.make_unit_label("")
        self._location_label = self.make_unit_label("")

        layout.addWidget(top_row)
        layout.addWidget(self._detail_label)
        layout.addWidget(self._location_label)

    def refresh(self):
        if self._temp_label is None:
            return

        weather_cfg = self.settings.weather
        lat = weather_cfg.get("latitude")
        lon = weather_cfg.get("longitude")

        if lat is None or lon is None:
            self._condition_label.setText("Set location in Settings")
            return

        if self._fetcher and self._fetcher.isRunning():
            return

        self._fetcher = WeatherFetcher(lat, lon, weather_cfg.get("units", "celsius"))
        self._fetcher.data_ready.connect(self._update_display)
        self._fetcher.error.connect(self._show_error)
        self._fetcher.start()

    def _update_display(self, data: dict):
        try:
            current = data.get("current", {})
            temp = current.get("temperature_2m", "--")
            code = current.get("weathercode", 0)
            humidity = current.get("relativehumidity_2m", "--")
            wind = current.get("windspeed_10m", "--")

            units = self.settings.weather.get("units", "celsius")
            unit_symbol = "°C" if units == "celsius" else "°F"

            description, icon_type = WEATHER_CODES.get(code, ("Unknown", "SUN"))
            icon_color = ICON_COLORS.get(icon_type, "#06d6a0")

            self._icon_label.setText(icon_type)
            self._icon_label.setStyleSheet(f"""
                background-color: rgba(255,255,255,0.06);
                border-radius: 12px;
                color: {icon_color};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.04em;
            """)

            self._temp_label.setText(f"{temp}{unit_symbol}")
            self._condition_label.setText(description)
            self._detail_label.setText(f"Humidity {humidity}%   Wind {wind} km/h")

            location = self.settings.weather.get("location_name", "")
            self._location_label.setText(location)

        except (KeyError, TypeError) as e:
            self._show_error(f"Data error: {e}")

    def _show_error(self, message: str):
        if self._condition_label:
            self._condition_label.setText(f"Error: {message}")