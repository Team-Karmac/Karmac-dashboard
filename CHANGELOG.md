# Karmac Dashboard — Changelog

---

## v2.0.0 — May 2026

### New Panels
- **Temperature** — CPU and GPU temperature monitoring with configurable display (Celsius, Fahrenheit, or both) and color-coded warning/critical thresholds
- **RAM Usage** — Real-time memory usage with used/available/total display
- **Hard Drives** — Disk space monitoring for all detected drives with individual drive visibility toggles
- **CPU Cores** — Per-core usage percentages and real-time frequencies in GHz alongside overall usage
- **GPU Usage** — AMD GPU load percentage, VRAM usage, and power draw (reads directly from sysfs)
- **Power Usage** — CPU package and GPU power consumption in watts via RAPL interface
- **FPS** — Live frames per second, frametime, and gaming stats via MangoHud integration

### Panel Improvements
- **Clock** — Added mini calendar with today's date highlighted in blue
- **Weather** — Added 3-day forecast with high/low temperatures and precipitation probability. Added today's high/low to current conditions
- **Network** — Added ping/latency with quality rating (Excellent/Good/Fair/Poor) and internet speed test via speedtest-cli. Configurable ping host
- **Fan Speeds** — Fans now grouped by hardware chip (e.g. NZXT Smart Device, AMD GPU). Zero RPM detection for GPU fans. Custom fan labels in settings
- **CPU Cores** — Added per-core frequency display alongside usage percentages

### Layout
- Expanded from 2 columns to 3 columns
- Expanded from 2 rows to 4 rows
- Panels reorganized by category for better visual flow

### Sidebar
- Hardware information moved from dashboard panel to navigation sidebar
- Sidebar now shows: CPU, GPU, motherboard, OS, kernel, desktop environment, RAM (with manufacturer and speed), storage, and display (with resolution and refresh rate)
- Monitor make and model detected via EDID data
- ASUS, Corsair, and other manufacturers identified via lookup tables

### Settings
- Added panel enable/disable toggles
- Added font size selection (Small/Medium/Large)
- Added timezone selection with full timezone database
- Added date format options (Long/Short/ISO)
- Added temperature display format (Celsius only/Fahrenheit only/Both)
- Added temperature warning and critical thresholds
- Added fan RPM warning and critical thresholds
- Added custom fan labels
- Added drive visibility toggles
- Added ping host configuration
- Added network section for ping configuration
- Blue borders on all input fields to indicate editability

### Stability
- Global exception handler added — crashes now logged to ~/.config/karmac/karmac.log
- All panel refresh methods wrapped in try/except to prevent one panel crash from killing the app
- Network panel ping delayed 3 seconds on launch to allow network readiness
- speedtest-cli import wrapped safely with graceful fallback

### Technical
- Version bumped to 2.0.0
- Added support for MangoHud FPS logging
- Added RAPL power monitoring support
- Added dmidecode integration for RAM details
- Added EDID parsing for monitor identification
- Added lsblk JSON output for reliable drive detection
- Weather API updated to fetch 4-day forecast data

---

## v1.0.0 — May 2026

### Initial Release
- Five core panels: Clock and Date, Weather, Fan Speeds, Network Status, System Uptime
- Dark and light theme support
- Fully customizable panel layout
- Open-Meteo weather integration (no API key required)
- Fan speeds grouped by hardware chip with Zero RPM detection
- Settings system with persistent storage
- Desktop launcher support
- GPL v3 licensed
- GitLab primary repository with GitHub mirror

---

## v3.0.0 — May 2026

### New Panels
- **Network Traffic** — Per-process bandwidth monitoring via nethogs (requires sudo)
- **Process Monitor** — Top processes by CPU or RAM with toggleable sort, friendly process names, and color-coded thresholds
- **Disk I/O** — Real-time NVMe/SSD read/write speeds via psutil

### Color System Overhaul
- All panels now use universal green/yellow/red traffic light system for data values
- Panel accent colors reserved for title bars only
- Green = normal, Yellow = warning, Red = critical

### Configurable Thresholds
- CPU usage warning/critical thresholds
- RAM usage warning/critical thresholds
- GPU usage warning/critical thresholds
- Power usage warning/critical thresholds (watts)
- FPS warning/critical thresholds (inverted — lower is worse)
- All configurable in Settings

### Privacy
- Default ping host changed from Google (8.8.8.8) to Quad9 (9.9.9.9) — non-profit, privacy-focused
- Privacy notes added to Settings for speed test (Ookla) and ping host
- Full privacy documentation added to README
- Complete audit of all outbound connections documented

### General
- Taskbar icon now shows Karmac logo instead of generic gear
- Version bumped to 3.0.0
- nethogs added to system dependencies for network traffic monitoring