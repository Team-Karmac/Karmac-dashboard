# Karmac Dashboard
### Project Specification v0.1

![Karmac Logo](Karmac_Logo.svg)

---

## What is Karmac?

Karmac is a free and open source desktop dashboard application for Linux. It gives everyday users a single, beautiful, organized view of their system's health and key personal information — without requiring technical knowledge to set up or use.

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
- Designed to look great out of the box with sensible defaults
- No configuration files required; everything is managed through the app's settings interface

---

## Dashboard Panels (v1.0)

The following five panels are included in the first release. All panels can be toggled and repositioned by the user.

### Clock & Date
Displays the current time and date. Supports 12-hour and 24-hour formats.

### Weather
Displays current local weather conditions including temperature, conditions, and forecast. Location set by the user in settings.

### Fan Speeds
Displays active fan speeds in RPM for all detected system fans, labeled by their hardware identifier.

### Network Status
Displays current upload and download speeds, connection type, and network name.

### System Uptime
Displays how long the system has been running since last boot.

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

## Technical Notes (for developers)

- Standalone desktop application targeting Linux
- Written in Python
- UI built with PySide6 (Qt framework)
- No external server or hosting dependency
- All data is read locally from the system
- Weather data sourced from Open-Meteo (free, open source, no API key required)
- Fully open source; primary repository hosted on GitLab *(to be set up)*, mirrored to GitHub for visibility
- Licensed under GNU General Public License v3 (GPL v3)

---

## Future Considerations

### Planned for v2.0
The following panels were scoped out of v1.0 to keep the first release achievable, and are the priority for the next release:

- CPU & GPU Temperature monitoring
- RAM Usage display
- Hard Drive Space monitoring
- CPU Core Activity display
- Hardware Brand & Specs Display

### Longer Term
Additional features that may be considered based on community feedback:

- Currently playing music display
- Calendar integration
- System notifications center
- Quick app launcher
- Battery status (for laptop users)
- Additional language packs
- Community-contributed themes

---

## Project Identity

**Name:** Karmac Dashboard  
**Tagline:** Everything you need. Nothing you don't.  
**Made by:** Team Karmac  
**License:** GNU General Public License v3 (GPL v3)  
**Primary Repository:** GitLab *(to be set up)*  
**Mirror:** GitHub *(to be set up)*  
**Community:** GitLab Issues & Discussions *(primary)*, Matrix *(real-time chat, to be added when community grows)*  

---

*This document is a living specification. It will be updated as the project evolves.*  
*Version 0.1 — May 2026*