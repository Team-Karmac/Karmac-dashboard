# Karmac Dashboard — Changelog

---

## v3.0.2 — June 2026

### Security
- Fixed a socket leak in the network ping check — sockets are now closed in a `finally` block even if the connection attempt fails
- Added input validation for the ping host and network interface settings, so a malformed or malicious value in settings.json can't be used for injection
- Fixed a thread-safety issue where ping results were updating the UI directly from a background thread; now goes through a proper Qt signal/slot
- Added a documented, narrowly-scoped bandit suppression for a false-positive temp-directory finding in the drives panel (the flagged string is a mount-path comparison, not a directory write)
- Added SECURITY.md and THREAT_MODEL.md, documenting every outbound connection, every elevated-privilege command, and the actual threats considered during development
- Added a CI pipeline running dependency auditing, secret scanning, static security analysis, and SBOM generation on every commit — none of this existed before this release

### Bug Fixes
- Fixed the Temperature panel's display format setting (Celsius only / Fahrenheit only / Both) — the panel was silently reading the wrong settings key and always rendering both units regardless of what was selected in Settings
- Fixed the hardware sidebar's BIOS field — added BIOS vendor, version, and release date, and fixed the actual code path that builds the sidebar (a separate, duplicated spec list inside window.py, not the HardwarePanel class most of the codebase assumes is in use)
- Fixed a hardcoded color in the sidebar's spec row labels that made them unreadable in light theme
- Removed two redundant local `import re` statements and an unnecessary `global` declaration in the network traffic panel — no behavior change, cleanup only
- Fixed the Flatpak manifest's runtime version, which had quietly gone end-of-life; updated to a currently supported KDE runtime
- Replaced a shell-script-generation pattern in the Flatpak manifest with Flatpak's proper `type: script` source, per upstream reviewer feedback
- Fixed Python 3.12 compatibility in the Flatpak build (charset-normalizer wheel selection, build-isolation handling)
- Fixed the SBOM generation step to record actually-installed package versions instead of the version floors from requirements.txt

### Documentation & Project Integrity
- Removed two orphaned, stale duplicate copies of requirements.txt (root and SRC/karmac/) that had drifted out of sync with the one actually in use; updated setup.py to match the real, current dependency versions
- Added an AI-disclosure section to README.md and merged AI-disclosure language into the existing CONTRIBUTING.md, rather than overwriting either with a partial draft
- Established a verification practice going forward: before editing any existing document, pull and diff against its actual current content rather than rewriting from memory

This release was prompted by community review feedback on the Flathub submission. Beyond the specific issues raised, the review process surfaced a real, previously undiscovered settings bug (Temperature display format) and a real architectural gap (duplicated sidebar logic) — both fixed here. The CI pipeline added in this release had never successfully completed a single run prior to this fix; every commit before this one was silently failing pipeline validation due to a YAML syntax error in the original configuration.

---

## v3.0.1 — June 2026

### Light Theme Fixes
- Calendar day numbers and headers now visible in light theme
- Sidebar hardware labels readable in both dark and light themes
- CPU core labels visible in light theme
- Power Usage CPU/GPU values visible in light theme
- FPS idle text visible in light theme
- Process monitor RAM button visible in light theme

### Flatpak Compatibility
- Replaced ping command with TCP socket latency check — works inside Flatpak sandbox
- Fixed OS detection to show host OS (e.g. Linux Mint) instead of KDE Flatpak runtime
- Fixed hard drives panel to deduplicate by physical device — prevents dozens of duplicate entries in Flatpak
- Flatpak manifest created and tested

### Documentation
- Added "Why Karmac?" comparison table to README
- Added Roadmap section to README
- Added v4 architecture considerations to spec
- Privacy section improved

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
- **Fan Speeds** — Fans now grouped by hardware chip. Zero RPM detection for GPU fans. Custom fan labels in settings
- **CPU Cores** — Added per-core frequency display alongside usage percentages

### Layout
- Expanded from 2 columns to 3 columns
- Expanded from 2 rows to 4 rows
- Panels reorganized by category for better visual flow

### Sidebar
- Hardware information moved from dashboard panel to navigation sidebar
- Sidebar now shows: CPU, GPU, motherboard, OS, kernel, desktop environment, RAM, storage, and display details
- Monitor make and model detected via EDID data

### Settings
- Added panel enable/disable toggles
- Added font size, timezone, date format options
- Added temperature display format (Celsius/Fahrenheit/Both)
- Added temperature, fan RPM warning and critical thresholds
- Added custom fan labels, drive visibility toggles, ping host configuration
- Blue borders on all input fields to indicate editability

### Stability
- Global exception handler — crashes logged to ~/.config/karmac/karmac.log
- All panel refresh methods wrapped in try/except
- Network panel ping delayed on launch for network readiness

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