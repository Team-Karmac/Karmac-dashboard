# Karmac Dashboard

> **Everything you need. Nothing you don't.**

Karmac is a free and open source desktop dashboard for Linux. It gives everyday users a beautiful, organized view of their system and personal information — without requiring any technical knowledge to set up or use.

![Karmac Dashboard](Assets/Karmac_Logo.svg)

![Karmac Dashboard Screenshot](Assets/Screenshot.png)

---

## Features

- 🕐 **Clock & Date** — Configurable time format, date format, and timezone
- 🌤 **Weather** — Current conditions powered by Open-Meteo (no API key required)
- 💨 **Fan Speeds** — Real-time RPM readings grouped by hardware chip, with custom labels and warning thresholds
- 🌐 **Network Status** — Live upload/download speeds and connection info
- ⏱ **System Uptime** — Time since last boot

**Plus a full settings system** including dark/light theme, font size, panel enable/disable, timezone selection, custom fan labels, and RPM warning thresholds.

---

## Requirements

- Linux (any modern distribution)
- Python 3.10 or higher
- PySide6, requests, psutil

---

## Installation

**1. Clone the repository:**
```
git clone https://gitlab.com/team.karmac1/Karmac-dashboard.git
cd Karmac-dashboard
```

**2. Create a virtual environment:**
```
python3 -m venv ~/karmac-env
source ~/karmac-env/bin/activate
```

**3. Install dependencies:**
```
pip install PySide6 requests psutil
```

**4. Install the required system library:**
```
sudo apt install libxcb-cursor0
```

**5. Run Karmac:**
```
cd src
python3 main.py
```

---

## Desktop Launcher

To add Karmac to your application menu, create a launcher file:

```
nano ~/.local/share/applications/karmac.desktop
```

Paste the following, replacing `/home/YOUR_USERNAME` with your actual home directory:

```
[Desktop Entry]
Type=Application
Name=Karmac Dashboard
Comment=Everything you need. Nothing you don't.
Exec=bash -c 'source /home/YOUR_USERNAME/karmac-env/bin/activate && python3 /home/YOUR_USERNAME/Karmac-dashboard/src/main.py'
Icon=/home/YOUR_USERNAME/Karmac-dashboard/assets/Karmac_Logo.svg
Categories=Utility;System;
Terminal=false
StartupNotify=true
```

Save with **Ctrl+X**, then **Y**, then **Enter**. Karmac will now appear in your application menu.

---

## Contributing

Karmac is built in the open and contributions are very welcome! Whether you're a developer, designer, translator, or tester — there's a place for you.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get involved.

---

## License

Karmac is licensed under the [GNU General Public License v3.0](LICENSE).

---

## Made by Team Karmac