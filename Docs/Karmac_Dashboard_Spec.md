# Karmac Dashboard
### Project Specification v0.3

---

## What is Karmac?

Karmac is a free and open source desktop dashboard application for Linux. It gives everyday users a single, beautiful, organized view of their system's health and key personal information — without requiring any technical knowledge to set up or use.

Karmac is built on a simple belief: Linux desktop users deserve a polished, privacy-respecting dashboard that works for everyone, not just developers and power users.

---

## The Problem Karmac Solves

Linux has long had tools for monitoring system performance and displaying personal information, but they share common shortcomings:

- They are built for technical users and assume comfort with configuration files and command-line tools
- They are either too minimal or too complex, with little middle ground
- They lack visual polish and feel out of place on a modern desktop
- They rarely combine system monitoring and personal information in one cohesive experience
- Server and homelab dashboards exist in abundance, but nothing comparable exists for the everyday Linux desktop user

Karmac fills this gap.

---

## Who is Karmac For?

Karmac is designed for all Linux desktop users, including:

- Everyday users who are new to Linux and want something that just works
- Privacy-conscious users switching away from proprietary operating systems like Windows and macOS
- Experienced Linux users who want a cleaner, more unified dashboard experience
- Gamers and enthusiasts who want real-time hardware monitoring in a friendly interface

---

## Core Philosophy

- **Privacy first** — Karmac collects no user data, sends nothing to external servers, and never will
- **Free and open source** — licensed under an open source license, free forever with no premium tier
- **Approachable** — designed for humans, not just power users
- **Honest** — what you see is what you get; no hidden features, no upsells, no ads
- **Community driven** — built in the open, with contributions welcomed from anyone

---

## Features

### Launch Behavior
Karmac can be configured to:
- Launch automatically at system startup, acting as a home screen
- Launch manually like any other application
- The user chooses their preferred behavior in settings

### Themes
- Full dark mode support
- Full light mode support
- Theme selection available in settings

### Layout
- Fully customizable — users can rearrange, resize, show, or hide any panel
- Three column grid layout across four rows
- Designed to look great out of the box with sensible defaults
- No configuration files required; everything is managed through the app's settings interface

### Sidebar
- Displays full hardware information alongside navigation
- Hardware section includes: CPU, GPU, motherboard, OS, kernel, desktop environment, RAM, storage, and display details

---

## Dashboard Panels (v2.0)

All panels can be toggled and repositioned by the user. Each panel has a unique accent color for instant visual identification.

### Row 1 — Personal & Connectivity
| Panel | Color | Description |
|-------|-------|-------------|
| Clock & Calendar | Blue | Time, date, and mini calendar with today highlighted |
| Weather | Green | Current conditions, high/low, humidity, wind, and 3-day forecast |
| Network | Purple | Live upload/download speeds, ping/latency, and internet speed test |

### Row 2 — Thermal & Processing
| Panel | Color | Description |
|-------|-------|-------------|
| Temperature | Orange | CPU and GPU temperatures — Celsius, Fahrenheit, or both |
| Fan Speeds | Yellow | RPM readings grouped by hardware chip with Zero RPM detection |
| CPU Cores | Pink | Overall usage, per-core activity, and per-core frequency |

### Row 3 — Memory & Storage
| Panel | Color | Description |
|-------|-------|-------------|
| System Uptime | Red | Time since last boot |
| RAM Usage | Aquamarine | Used/available memory with percentage |
| Hard Drives | Lime | Space used/free for all detected drives |

### Row 4 — Power & Graphics
| Panel | Color | Description |
|-------|-------|-------------|
| GPU Usage | Light Violet | AMD GPU load %, VRAM usage, and power draw |
| Power Usage | Cyan | CPU package and GPU power consumption in watts |
| FPS | Coral | Live FPS, frametime, CPU/GPU load via MangoHud integration |

---

## Color Palette

| Panel | Color | Hex |
|-------|-------|-----|
| Clock | Blue | #4361ee |
| Weather | Green | #06d6a0 |
| Fan Speeds | Yellow | #ffd000 |
| Network | Purple | #9b5de5 |
| System Uptime | Red | #ff4d6d |
| CPU/GPU Temperature | Orange | #ff6d00 |
| RAM Usage | Aquamarine | #00f5d4 |
| Hard Drive Space | Lime | #b5e800 |
| CPU Core Activity | Pink | #ff006e |
| Hardware Brand & Specs | Brown | #c17c3a |
| GPU Usage | Light Violet | #c77dff |
| Power Usage | Cyan | #00b4d8 |
| FPS | Coral | #ff6b6b |

---

## Settings

### Appearance
- Theme (Dark / Light)
- Font Size (Small / Medium / Large)

### Panels
- Enable/disable individual panels
- Changes take effect after restarting Karmac

### Clock
- 12/24-hour format
- Show/hide seconds
- Date format (Long / Short / ISO)
- Timezone selection

### Weather
- Location search
- Temperature units (Celsius / Fahrenheit)

### Network
- Ping host configuration

### Fan Speeds
- Warning RPM threshold
- Critical RPM threshold
- Custom fan labels

### Temperature
- Display format (Celsius only / Fahrenheit only / Both)
- Warning threshold (°C)
- Critical threshold (°C)

### Hard Drives
- Show/hide individual drives

### Startup
- Launch Karmac automatically on login

---

## What Karmac Is Not

- Not a server or homelab dashboard
- Not a widget system requiring manual assembly
- Not a web application or browser-based tool
- Not a data collection platform
- Not a subscription service

---

## Language Support

Karmac launches in English. Additional language translations are welcomed and encouraged from community contributors. All translations are credited within the application.

---

## Technical Notes

- Standalone desktop application targeting Linux
- Written in Python
- UI built with PySide6 (Qt framework)
- No external server or hosting dependency
- All data is read locally from the system
- Weather data sourced from Open-Meteo (free, open source, no API key required)
- FPS data sourced from MangoHud log files
- Power monitoring via RAPL interface
- Fully open source; primary repository hosted on GitLab, mirrored to GitHub for visibility
- Licensed under GNU General Public License v3 (GPL v3)
- Crash logging to ~/.config/karmac/karmac.log

---

## Future Considerations

### v4 Architecture
- **Shared metrics service** — centralized data collection with a shared cache that panels subscribe to, rather than each panel polling independently. Important for scalability and efficiency on lower-powered hardware

### Community-Driven Features
The following may be considered based on community feedback:
- Plugin/widget framework for community-created panels
- Theme marketplace
- Currently playing music display
- Calendar integration
- System notifications center
- Quick app launcher
- Battery status for laptop users
- Additional language packs
- NVIDIA GPU support improvements
- AppImage packaging
- AUR package for Arch/Manjaro users
- Multi-monitor support

---

## Project Identity

**Name:** Karmac Dashboard
**Tagline:** Everything you need. Nothing you don't.
**Made by:** Team Karmac
**License:** GNU General Public License v3 (GPL v3)
**Primary Repository:** GitLab — gitlab.com/team.karmac1/Karmac-dashboard
**Mirror:** GitHub — github.com/Team-Karmac/Karmac-dashboard
**Community:** GitLab Issues & Discussions *(primary)*, Matrix *(real-time chat, to be added when community grows)*

---

*This document is a living specification. It will be updated as the project evolves.*
*Version 0.3 — May 2026*