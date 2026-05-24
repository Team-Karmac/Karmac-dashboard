"""
Karmac Dashboard — Settings Manager
Handles loading, saving, and accessing user preferences.
"""

import json
from pathlib import Path


DEFAULT_SETTINGS = {
    "theme": "dark",
    "font_size": "medium",
    "launch_on_startup": False,
    "panels": {
        "clock":      {"enabled": True,  "position": 0},
        "weather":    {"enabled": True,  "position": 1},
        "fan_speeds": {"enabled": True,  "position": 2},
        "network":    {"enabled": True,  "position": 3},
        "uptime":     {"enabled": True,  "position": 4},
    },
    "weather": {
        "latitude":      None,
        "longitude":     None,
        "location_name": "",
        "units":         "celsius",
        "refresh_interval": 10,
    },
    "clock": {
        "format_24h":   False,
        "show_seconds": True,
        "timezone":     "local",
        "date_format":  "long",
    },
    "fans": {
        "labels":            {},
        "rpm_warning":       2000,
        "rpm_critical":      3000,
    },
    "network": {
        "interface": "auto",
        "speed_unit": "auto",
    },
    "window": {
        "width":  1100,
        "height": 700,
        "x":      None,
        "y":      None,
    }
}


class Settings:
    """Manages Karmac user settings with persistent storage."""

    def __init__(self):
        self._config_dir  = Path.home() / ".config" / "karmac"
        self._config_file = self._config_dir / "settings.json"
        self._data = json.loads(json.dumps(DEFAULT_SETTINGS))  # deep copy
        self._load()

    def _load(self):
        try:
            if self._config_file.exists():
                with open(self._config_file, "r") as f:
                    saved = json.load(f)
                    self._deep_merge(self._data, saved)
        except (json.JSONDecodeError, IOError):
            pass

    def _deep_merge(self, base, override):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def save(self):
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w") as f:
                json.dump(self._data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save settings: {e}")

    # ── Properties ────────────────────────────────────────

    @property
    def theme(self):
        return self._data.get("theme", "dark")

    @theme.setter
    def theme(self, value):
        if value in ("dark", "light"):
            self._data["theme"] = value
            self.save()

    @property
    def font_size(self):
        return self._data.get("font_size", "medium")

    @font_size.setter
    def font_size(self, value):
        if value in ("small", "medium", "large"):
            self._data["font_size"] = value
            self.save()

    @property
    def launch_on_startup(self):
        return self._data.get("launch_on_startup", False)

    @launch_on_startup.setter
    def launch_on_startup(self, value):
        self._data["launch_on_startup"] = bool(value)
        self.save()

    @property
    def panels(self):
        return self._data.get("panels", DEFAULT_SETTINGS["panels"])

    @property
    def weather(self):
        return self._data.get("weather", DEFAULT_SETTINGS["weather"])

    @weather.setter
    def weather(self, value):
        self._data["weather"] = value
        self.save()

    @property
    def clock(self):
        return self._data.get("clock", DEFAULT_SETTINGS["clock"])

    @property
    def fans(self):
        return self._data.get("fans", DEFAULT_SETTINGS["fans"])

    @fans.setter
    def fans(self, value):
        self._data["fans"] = value
        self.save()

    @property
    def network(self):
        return self._data.get("network", DEFAULT_SETTINGS["network"])

    @property
    def window(self):
        return self._data.get("window", DEFAULT_SETTINGS["window"])

    def update_window_geometry(self, x, y, width, height):
        self._data["window"] = {"x": x, "y": y, "width": width, "height": height}
        self.save()

    def set_panel_enabled(self, panel_name, enabled):
        if panel_name in self._data["panels"]:
            self._data["panels"][panel_name]["enabled"] = enabled
            self.save()

    def set_panel_position(self, panel_name, position):
        if panel_name in self._data["panels"]:
            self._data["panels"][panel_name]["position"] = position
            self.save()

    def get_fan_label(self, raw_label: str) -> str:
        """Get custom label for a fan, falling back to raw label."""
        return self._data["fans"]["labels"].get(raw_label, raw_label)

    def set_fan_label(self, raw_label: str, custom_label: str):
        """Set a custom label for a fan."""
        self._data["fans"]["labels"][raw_label] = custom_label
        self.save()