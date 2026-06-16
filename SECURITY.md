# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 3.x     | ✅ Active support |
| 2.x     | ❌ No longer supported |
| 1.x     | ❌ No longer supported |

## Reporting a Vulnerability

Team Karmac takes security seriously. If you discover a security vulnerability in Karmac Dashboard, please report it responsibly.

**Do NOT open a public GitLab issue for security vulnerabilities.**

Instead, please report vulnerabilities privately via email:

📧 **Team.Karmac@proton.me**

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

We will acknowledge your report within **48 hours** and aim to provide a fix within **14 days** for critical issues.

## Security Design Principles

Karmac Dashboard is designed with privacy and security as core values:

### Network Connections
Karmac makes the following outbound connections:
| Destination | Purpose | When | User Control |
|-------------|---------|------|--------------|
| api.open-meteo.com | Weather data | Every refresh | Configurable |
| 9.9.9.9 (Quad9) | Latency check | Every 5 seconds | Configurable host |
| Ookla speedtest servers | Speed test | Manual only | User initiated |

No other outbound connections are made. No telemetry, no analytics, no data collection.

### System Access
Karmac reads the following system resources:
- `/proc/cpuinfo`, `/proc/meminfo` — CPU and RAM info (read-only)
- `/sys/class/hwmon/` — Temperature and fan sensors (read-only)
- `/sys/class/drm/` — GPU information (read-only)
- `/sys/class/powercap/` — Power consumption (read-only)
- `~/.local/share/MangoHud/` — FPS data (read-only)

### Elevated Privileges
Two system tools require sudo access:
- `dmidecode` — reads hardware BIOS information
- `nethogs` — monitors per-process network traffic

These are configured via `/etc/sudoers.d/` with `NOPASSWD` and limited to the specific commands only.

### Input Validation
- Ping host: validated against safe hostname/IP regex before use
- Network interface: validated against safe interface name pattern before passing to nethogs
- All user-configurable values are validated before use

### Dependencies
| Package | Version | Notes |
|---------|---------|-------|
| PySide6 | 6.7.0 | Qt Python bindings — actively maintained |
| requests | 2.34.2 | HTTP library — actively maintained |
| psutil | 7.2.2 | System monitoring — actively maintained |
| speedtest-cli | 2.1.3 | Speed test — limited maintenance activity |
| certifi | 2026.5.20 | CA certificates — actively maintained |
| urllib3 | 2.7.0 | HTTP client — actively maintained |
| idna | 3.17 | Internationalized domain names |
| charset-normalizer | 3.4.7 | Character encoding |

**Note on speedtest-cli:** This package has limited maintenance activity. It is only used when the user explicitly clicks "Run Test" and makes no automatic connections. We are evaluating alternatives for a future release.

## Threat Model

### Assets
- User's system information (displayed locally, never transmitted)
- User's network activity (monitored locally via nethogs)
- User's settings (stored in `~/.config/karmac/settings.json`)

### Threat Actors
- **Remote attacker** — limited attack surface; Karmac opens no network ports and accepts no incoming connections
- **Malicious dependency** — mitigated by pinned versions and SHA256 checksums in Flatpak manifest
- **Malicious media metadata** — not applicable; Karmac does not parse media files

### Out of Scope
- Physical access attacks
- OS-level privilege escalation (Karmac runs as the user, not root)
- Attacks requiring social engineering of the user

## Security Changelog

| Version | Security Changes |
|---------|-----------------|
| 3.0.1 | Fixed socket leak in ping function; added host validation; fixed thread safety in ping updates; added interface name validation for nethogs |
| 3.0.0 | Changed default ping host from Google (8.8.8.8) to Quad9 (9.9.9.9); documented all outbound connections |