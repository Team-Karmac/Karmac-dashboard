# Karmac Dashboard

> **Everything you need. Nothing you don't.**

Karmac is a free and open source desktop dashboard for Linux. It gives everyday users a beautiful, organized view of their system and personal information — without requiring any technical knowledge to set up or use.

![Karmac Dashboard](Assets/Karmac_Logo.svg)

![Karmac Dashboard Screenshot](Assets/Screenshot.png)

---

## Features

**Row 1 — Personal**
- 🕐 **Clock & Date** — Configurable time format, date format, and timezone
- 🌤 **Weather** — Current conditions + 3-day forecast powered by Open-Meteo (no API key required)
- ⏱ **System Uptime** — Time since last boot

**Row 2 — Connectivity & Memory**
- 🌐 **Network** — Live upload/download speeds, ping/latency, and internet speed test
- 💾 **RAM Usage** — Used/available memory in real time
- 💿 **Hard Drives** — Space used/free for all detected drives

**Row 3 — Thermal & Processing**
- 🌡 **Temperature** — CPU and GPU temperatures in Celsius and Fahrenheit
- 💨 **Fan Speeds** — RPM readings grouped by hardware chip with Zero RPM detection
- ⚡ **CPU Cores** — Overall usage, per-core activity, and per-core frequency

**Row 4 — Power & Graphics**
- 🎮 **GPU Usage** — AMD GPU load percentage, VRAM usage, and power draw
- ⚡ **Power Usage** — CPU package and GPU power consumption in watts

**Sidebar**
- Full hardware information including CPU, GPU, RAM, storage, OS, kernel, desktop environment, and display details

**Full Settings System**
- Dark/light theme, font size, panel enable/disable, timezone, custom fan labels, RPM thresholds, temperature thresholds, drive visibility, ping host, and more

---

## Requirements

- Linux (any modern distribution)
- Python 3.10 or higher
- AMD or Intel CPU (for power/temperature monitoring)

---

## Installation

### Step 1 — Install system dependencies

```
sudo apt install libxcb-cursor0 lm-sensors nvme-cli librsvg2-bin mangohud
```

### Step 2 — Clone the repository

```
git clone https://gitlab.com/team.karmac1/Karmac-dashboard.git
cd Karmac-dashboard
```

### Step 3 — Create a virtual environment

```
python3 -m venv ~/karmac-env
source ~/karmac-env/bin/activate
```

### Step 4 — Install Python dependencies

```
pip install PySide6 requests psutil speedtest-cli
```

### Step 5 — Run Karmac

```
cd src
python3 main.py
```

---

## Optional Configuration

### RAM Details (manufacturer, speed, type)

Karmac reads RAM details using `dmidecode`. To allow this without a password prompt:

```
sudo visudo
```

Add this line at the bottom:

```
YOUR_USERNAME ALL=(ALL) NOPASSWD: /usr/sbin/dmidecode
```

### CPU Power Monitoring (RAPL)

To enable CPU power readings without root access, create a udev rule:

```
sudo nano /etc/udev/rules.d/99-rapl.rules
```

Add these lines:

```
SUBSYSTEM=="powercap", KERNEL=="intel-rapl:0", ACTION=="add", RUN+="/bin/chmod a+r /sys/class/powercap/intel-rapl:0/energy_uj"
SUBSYSTEM=="powercap", KERNEL=="intel-rapl:0:0", ACTION=="add", RUN+="/bin/chmod a+r /sys/class/powercap/intel-rapl:0:0/energy_uj"
```

Then apply immediately:

```
sudo chmod a+r /sys/class/powercap/intel-rapl:0/energy_uj
sudo chmod a+r /sys/class/powercap/intel-rapl:0:0/energy_uj
```

---

## Desktop Launcher

### Create the app icon

```
rsvg-convert -w 128 -h 128 ~/Karmac-dashboard/Assets/Karmac_Logo.svg -o ~/.local/share/icons/Karmac_Logo.png
```

### Create the launcher

```
nano ~/.local/share/applications/karmac.desktop
```

Paste the following, replacing `YOUR_USERNAME` with your username:

```
[Desktop Entry]
Type=Application
Name=Karmac Dashboard
Comment=Everything you need. Nothing you don't.
Exec=bash -c 'source /home/YOUR_USERNAME/karmac-env/bin/activate && python3 /home/YOUR_USERNAME/Karmac-dashboard/src/main.py'
Icon=/home/YOUR_USERNAME/.local/share/icons/Karmac_Logo.png
Categories=Utility;System;
Terminal=false
StartupNotify=true
```

### Create a desktop shortcut

```
cp ~/.local/share/applications/karmac.desktop ~/Desktop/
chmod +x ~/Desktop/karmac.desktop
gio set ~/Desktop/karmac.desktop metadata::trusted true
```

---

## Contributing

Karmac is built in the open and contributions are very welcome! Whether you're a developer, designer, translator, or tester — there's a place for you.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get involved.

---

## License

Karmac is licensed under the [GNU General Public License v3.0](LICENSE).

---

## Made by Team Karmac