"""
Karmac Dashboard — Settings View
The settings screen for configuring Karmac preferences.
"""

import zoneinfo
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QComboBox, QLineEdit,
    QScrollArea, QFrame, QSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from karmac.settings import Settings
import requests


class LocationSearchThread(QThread):
    result = Signal(list)
    error  = Signal(str)

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run(self):
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={self.query}&count=5&language=en&format=json"
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            self.result.emit(response.json().get("results", []))
        except Exception as e:
            self.error.emit(str(e))


class SettingSection(QWidget):
    def __init__(self, title: str, color: str = None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title_label = QLabel(title.upper())
        title_label.setObjectName("section-title")
        if color:
            title_label.setStyleSheet(
                f"color: {color}; font-size: 11px; font-weight: 700; letter-spacing: 0.14em;"
            )
        layout.addWidget(title_label)

        self._content = QVBoxLayout()
        self._content.setContentsMargins(0, 4, 0, 0)
        self._content.setSpacing(10)
        layout.addLayout(self._content)

    def add_widget(self, widget):
        self._content.addWidget(widget)

    def add_layout(self, layout):
        self._content.addLayout(layout)


def make_row(label_text: str, widget: QWidget) -> QWidget:
    """Helper to create a label + widget row."""
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    label = QLabel(label_text)
    label.setObjectName("settings-label")
    layout.addWidget(label)
    layout.addStretch()
    layout.addWidget(widget)
    return row


class SettingsView(QWidget):

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self._search_thread = None
        self._search_results_data = []
        self._fan_label_inputs = {}
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(28, 28, 36, 28)
        layout.setSpacing(32)
        layout.setAlignment(Qt.AlignTop)

        # Page title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: 300;")
        layout.addWidget(title)

        layout.addWidget(self._build_appearance())
        layout.addWidget(self._build_panels_section())
        layout.addWidget(self._build_clock_section())
        layout.addWidget(self._build_weather_section())
        layout.addWidget(self._build_fans_section())
        layout.addWidget(self._build_startup_section())
        layout.addStretch()

        scroll.setWidget(inner)
        outer.addWidget(scroll)

    # ── Section builders ───────────────────────────────────

    def _build_appearance(self) -> QWidget:
        section = SettingSection("Appearance", "#4361ee")

        # Theme
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Dark", "Light"])
        self._theme_combo.setCurrentText(self.settings.theme.capitalize())
        self._theme_combo.currentTextChanged.connect(self._on_theme_changed)
        section.add_widget(make_row("Theme", self._theme_combo))

        # Font size
        self._font_combo = QComboBox()
        self._font_combo.addItems(["Small", "Medium", "Large"])
        self._font_combo.setCurrentText(self.settings.font_size.capitalize())
        self._font_combo.currentTextChanged.connect(self._on_font_size_changed)
        section.add_widget(make_row("Font Size", self._font_combo))

        return section

    def _build_panels_section(self) -> QWidget:
        section = SettingSection("Panels", "#9b5de5")

        panel_labels = {
            "clock":      "Clock and Date",
            "weather":    "Weather",
            "fan_speeds": "Fan Speeds",
            "network":    "Network Status",
            "uptime":     "System Uptime",
        }

        self._panel_checks = {}
        for name, label in panel_labels.items():
            cb = QCheckBox(label)
            cb.setChecked(self.settings.panels.get(name, {}).get("enabled", True))
            cb.toggled.connect(lambda checked, n=name: self._on_panel_toggled(n, checked))
            self._panel_checks[name] = cb
            section.add_widget(cb)

        note = QLabel("Changes take effect after restarting Karmac.")
        note.setObjectName("panel-unit")
        note.setStyleSheet("color: rgba(240,240,255,0.3); font-style: italic;")
        section.add_widget(note)

        return section

    def _build_clock_section(self) -> QWidget:
        section = SettingSection("Clock", "#4361ee")

        self._24h_check = QCheckBox("Use 24-hour format")
        self._24h_check.setChecked(self.settings.clock.get("format_24h", False))
        self._24h_check.toggled.connect(self._on_clock_changed)
        section.add_widget(self._24h_check)

        self._seconds_check = QCheckBox("Show seconds")
        self._seconds_check.setChecked(self.settings.clock.get("show_seconds", True))
        self._seconds_check.toggled.connect(self._on_clock_changed)
        section.add_widget(self._seconds_check)

        # Date format
        self._date_format_combo = QComboBox()
        self._date_format_combo.addItems(["Long (Sunday, May 24, 2026)", "Short (05/24/2026)", "ISO (2026-05-24)"])
        fmt = self.settings.clock.get("date_format", "long")
        self._date_format_combo.setCurrentIndex({"long": 0, "short": 1, "iso": 2}.get(fmt, 0))
        self._date_format_combo.currentIndexChanged.connect(self._on_date_format_changed)
        section.add_widget(make_row("Date Format", self._date_format_combo))

        # Timezone
        self._tz_combo = QComboBox()
        self._tz_combo.setMinimumWidth(220)
        self._populate_timezones()
        self._tz_combo.currentTextChanged.connect(self._on_timezone_changed)
        section.add_widget(make_row("Timezone", self._tz_combo))

        return section

    def _build_weather_section(self) -> QWidget:
        section = SettingSection("Weather", "#06d6a0")

        # Location search
        loc_row = QWidget()
        loc_layout = QHBoxLayout(loc_row)
        loc_layout.setContentsMargins(0, 0, 0, 0)
        loc_layout.setSpacing(8)

        self._location_input = QLineEdit()
        self._location_input.setPlaceholderText("Search for a city...")
        if self.settings.weather.get("location_name"):
            self._location_input.setText(self.settings.weather["location_name"])

        self._location_search_btn = QPushButton("Search")
        self._location_search_btn.clicked.connect(self._search_location)
        loc_layout.addWidget(self._location_input)
        loc_layout.addWidget(self._location_search_btn)

        self._location_results = QComboBox()
        self._location_results.addItem("— Search results —")
        self._location_results.currentIndexChanged.connect(self._on_location_selected)

        self._location_status = QLabel("")
        self._location_status.setObjectName("panel-subtitle")

        # Units
        self._units_combo = QComboBox()
        self._units_combo.addItems(["Celsius", "Fahrenheit"])
        self._units_combo.setCurrentText(self.settings.weather.get("units", "celsius").capitalize())
        self._units_combo.currentTextChanged.connect(self._on_units_changed)

        section.add_widget(loc_row)
        section.add_widget(self._location_results)
        section.add_widget(self._location_status)
        section.add_widget(make_row("Temperature Units", self._units_combo))

        return section

    def _build_fans_section(self) -> QWidget:
        section = SettingSection("Fan Speeds", "#ffbe0b")

        # RPM warning threshold
        self._rpm_warning_spin = QSpinBox()
        self._rpm_warning_spin.setRange(500, 5000)
        self._rpm_warning_spin.setSingleStep(100)
        self._rpm_warning_spin.setValue(self.settings.fans.get("rpm_warning", 2000))
        self._rpm_warning_spin.setSuffix(" RPM")
        self._rpm_warning_spin.setMinimumWidth(120)
        self._rpm_warning_spin.valueChanged.connect(self._on_rpm_warning_changed)
        section.add_widget(make_row("Warning Threshold", self._rpm_warning_spin))

        # RPM critical threshold
        self._rpm_critical_spin = QSpinBox()
        self._rpm_critical_spin.setRange(500, 6000)
        self._rpm_critical_spin.setSingleStep(100)
        self._rpm_critical_spin.setValue(self.settings.fans.get("rpm_critical", 3000))
        self._rpm_critical_spin.setSuffix(" RPM")
        self._rpm_critical_spin.setMinimumWidth(120)
        self._rpm_critical_spin.valueChanged.connect(self._on_rpm_critical_changed)
        section.add_widget(make_row("Critical Threshold", self._rpm_critical_spin))

        # Custom fan labels
        label_header = QLabel("Custom Fan Labels")
        label_header.setObjectName("settings-label")
        section.add_widget(label_header)

        hint = QLabel("Rename fans to something more descriptive (e.g. 'CPU Fan', 'Top Case')")
        hint.setObjectName("panel-unit")
        hint.setStyleSheet("color: rgba(240,240,255,0.3); font-style: italic;")
        hint.setWordWrap(True)
        section.add_widget(hint)

        # Fan label inputs — populated dynamically from detected fans
        self._fan_labels_container = QVBoxLayout()
        self._fan_labels_container.setSpacing(8)
        fan_labels_widget = QWidget()
        fan_labels_widget.setLayout(self._fan_labels_container)
        section.add_widget(fan_labels_widget)
        self._populate_fan_labels()

        return section

    def _build_startup_section(self) -> QWidget:
        section = SettingSection("Startup", "#ff4d6d")

        self._startup_check = QCheckBox("Launch Karmac automatically on login")
        self._startup_check.setChecked(self.settings.launch_on_startup)
        self._startup_check.toggled.connect(self._on_startup_changed)
        section.add_widget(self._startup_check)

        return section

    # ── Helpers ────────────────────────────────────────────

    def _populate_timezones(self):
        """Populate timezone dropdown with available timezones."""
        self._tz_combo.addItem("Local (system default)")
        try:
            zones = sorted(zoneinfo.available_timezones())
            for tz in zones:
                self._tz_combo.addItem(tz)
        except Exception:
            # Fallback list of common timezones
            common = [
                "America/New_York", "America/Chicago", "America/Denver",
                "America/Los_Angeles", "America/Anchorage", "Pacific/Honolulu",
                "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow",
                "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Asia/Dubai",
                "Australia/Sydney", "Pacific/Auckland",
            ]
            for tz in common:
                self._tz_combo.addItem(tz)

        current = self.settings.clock.get("timezone", "local")
        if current == "local":
            self._tz_combo.setCurrentIndex(0)
        else:
            idx = self._tz_combo.findText(current)
            if idx >= 0:
                self._tz_combo.setCurrentIndex(idx)

    def _populate_fan_labels(self):
        """Populate fan label inputs based on currently detected fans."""
        try:
            import psutil
            sensors = psutil.sensors_fans()
            if not sensors:
                return

            existing_labels = self.settings.fans.get("labels", {})

            for chip_name, entries in sensors.items():
                for entry in entries:
                    raw = entry.label or "Fan"
                    row = QWidget()
                    layout = QHBoxLayout(row)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(8)

                    raw_label = QLabel(f"{raw}:")
                    raw_label.setObjectName("settings-label")
                    raw_label.setMinimumWidth(80)

                    input_field = QLineEdit()
                    input_field.setPlaceholderText(raw)
                    input_field.setText(existing_labels.get(raw, ""))

                    save_btn = QPushButton("Save")
                    save_btn.setFixedWidth(80)
                    save_btn.clicked.connect(
                        lambda _, r=raw, field=input_field: self._save_fan_label(r, field.text())
                    )

                    layout.addWidget(raw_label)
                    layout.addWidget(input_field)
                    layout.addWidget(save_btn)

                    self._fan_labels_container.addWidget(row)
                    self._fan_label_inputs[raw] = input_field

        except Exception:
            no_fans = QLabel("No fans detected")
            no_fans.setObjectName("panel-unit")
            self._fan_labels_container.addWidget(no_fans)

    def _refresh_weather_panel(self):
        main_window = self.parent()
        if main_window and hasattr(main_window, '_panels'):
            panel = main_window._panels.get('weather')
            if panel:
                panel.refresh()

    def _rebuild_dashboard(self):
        """Trigger a dashboard rebuild after panel visibility changes."""
        main_window = self.parent()
        if main_window and hasattr(main_window, '_rebuild_panels'):
            main_window._rebuild_panels()

    # ── Event handlers ─────────────────────────────────────

    def _on_theme_changed(self, value: str):
        self.settings.theme = value.lower()
        if self.parent():
            self.parent().apply_theme(value.lower())

    def _on_font_size_changed(self, value: str):
        self.settings.font_size = value.lower()
        if self.parent():
            self.parent().apply_theme(self.settings.theme)

    def _on_panel_toggled(self, panel_name: str, enabled: bool):
        self.settings.set_panel_enabled(panel_name, enabled)

    def _on_clock_changed(self):
        self.settings._data["clock"]["format_24h"]   = self._24h_check.isChecked()
        self.settings._data["clock"]["show_seconds"]  = self._seconds_check.isChecked()
        self.settings.save()

    def _on_date_format_changed(self, index: int):
        fmt = ["long", "short", "iso"][index]
        self.settings._data["clock"]["date_format"] = fmt
        self.settings.save()

    def _on_timezone_changed(self, value: str):
        tz = "local" if value.startswith("Local") else value
        self.settings._data["clock"]["timezone"] = tz
        self.settings.save()

    def _on_units_changed(self, value: str):
        weather = dict(self.settings.weather)
        weather["units"] = value.lower()
        self.settings.weather = weather
        self._refresh_weather_panel()

    def _on_rpm_warning_changed(self, value: int):
        fans = dict(self.settings.fans)
        fans["rpm_warning"] = value
        self.settings.fans = fans

    def _on_rpm_critical_changed(self, value: int):
        fans = dict(self.settings.fans)
        fans["rpm_critical"] = value
        self.settings.fans = fans

    def _save_fan_label(self, raw: str, custom: str):
        self.settings.set_fan_label(raw, custom.strip())

    def _on_startup_changed(self, checked: bool):
        self.settings.launch_on_startup = checked
        self._setup_autostart(checked)

    def _search_location(self):
        query = self._location_input.text().strip()
        if not query:
            return
        self._location_status.setText("Searching...")
        self._location_results.clear()
        self._location_results.addItem("— Searching... —")
        self._location_results.setEnabled(False)
        self._search_thread = LocationSearchThread(query)
        self._search_thread.result.connect(self._on_search_results)
        self._search_thread.error.connect(self._on_search_error)
        self._search_thread.start()

    def _on_search_results(self, results: list):
        self._location_results.clear()
        self._search_results_data = results
        if not results:
            self._location_results.addItem("No results found")
            self._location_status.setText("Try a different search term")
            self._location_results.setEnabled(False)
            return
        self._location_results.addItem("— Select a location —")
        for r in results:
            label = f"{r['name']}, {r.get('admin1','')}, {r.get('country','')}".strip(", ")
            self._location_results.addItem(label)
        self._location_results.setEnabled(True)
        self._location_status.setText(f"{len(results)} result(s) found")

    def _on_search_error(self, error: str):
        self._location_results.clear()
        self._location_results.addItem("— Search failed —")
        self._location_status.setText(f"Error: {error}")
        self._location_results.setEnabled(False)

    def _on_location_selected(self, index: int):
        if index <= 0 or not self._search_results_data:
            return
        result = self._search_results_data[index - 1]
        weather = dict(self.settings.weather)
        weather["latitude"]      = result.get("latitude")
        weather["longitude"]     = result.get("longitude")
        weather["location_name"] = result.get("name", "")
        self.settings.weather = weather
        self._location_status.setText(f"✓ Location set to {result.get('name', '')}")
        self._refresh_weather_panel()

    def _setup_autostart(self, enabled: bool):
        from pathlib import Path
        autostart_dir  = Path.home() / ".config" / "autostart"
        autostart_file = autostart_dir / "karmac.desktop"
        if enabled:
            autostart_dir.mkdir(parents=True, exist_ok=True)
            autostart_file.write_text(
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Karmac Dashboard\n"
                "Comment=Everything you need. Nothing you don't.\n"
                "Exec=karmac\n"
                "Hidden=false\n"
                "NoDisplay=false\n"
                "X-GNOME-Autostart-enabled=true\n"
            )
        else:
            if autostart_file.exists():
                autostart_file.unlink()