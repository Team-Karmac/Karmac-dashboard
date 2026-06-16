# Karmac Dashboard — Threat Model

## Overview

This document describes the security threat model for Karmac Dashboard. It identifies
assets, threats, and mitigations considered during design and development.

## Application Profile

- **Type:** Native Linux desktop application
- **Runtime:** Python 3.10+, PySide6 (Qt)
- **Privilege level:** Runs as normal user (no root required)
- **Network:** Outbound only — no listening ports, no incoming connections
- **Data storage:** Local only — `~/.config/karmac/settings.json`

---

## Assets

| Asset | Sensitivity | Notes |
|-------|-------------|-------|
| System hardware info | Low | Already public via /proc, /sys |
| Network activity | Medium | Per-process traffic via nethogs |
| User settings | Low | Theme, preferences — no credentials |
| User's privacy | High | Which apps are running, network usage |

---

## Attack Surface

| Entry Point | Description | Risk |
|-------------|-------------|------|
| Weather API response | JSON from Open-Meteo | Low — parsed with requests, no eval |
| Ping host setting | User-configurable hostname/IP | Low — validated before use |
| Network interface setting | User-configurable interface name | Low — validated before passing to nethogs |
| MangoHud log files | Read from ~/.local/share/MangoHud/ | Low — read-only file parsing |
| /sys and /proc | Kernel interfaces | Low — read-only |
| speedtest-cli | External test servers | Medium — only on user request |

---

## Threats and Mitigations

### T1 — Command Injection via Ping Host
**Threat:** Attacker modifies settings.json to inject shell commands via ping_host field.
**Likelihood:** Low — requires local access to settings file
**Impact:** Medium — could execute arbitrary commands
**Mitigation:** `_validate_host()` validates ping host against safe regex before use. Only valid IPv4 or hostname patterns accepted.

### T2 — Command Injection via Network Interface
**Threat:** Malicious interface name passed to nethogs subprocess.
**Likelihood:** Low — requires local access or compromised settings
**Impact:** Medium — nethogs runs with sudo
**Mitigation:** `_is_valid_interface()` validates interface name against `^[a-zA-Z0-9][a-zA-Z0-9@:._-]{0,15}$` before use.

### T3 — Malicious Weather API Response
**Threat:** Open-Meteo returns malicious data designed to cause crashes or code execution.
**Likelihood:** Very Low — Open-Meteo is a reputable FOSS service
**Impact:** Low — response is parsed as JSON with requests, no eval or exec
**Mitigation:** All API responses wrapped in try/except. No dynamic code execution from API data.

### T4 — Dependency Compromise (Supply Chain)
**Threat:** A dependency is compromised and ships malicious code.
**Likelihood:** Low — all dependencies are well-maintained except speedtest-cli
**Impact:** High — would execute in user context
**Mitigation:** Flatpak manifest pins all dependencies with SHA256 checksums. speedtest-cli risk documented and under review.

### T5 — Socket Resource Exhaustion
**Threat:** Ping function creates sockets faster than they can be closed.
**Likelihood:** Low — ping runs every 5 seconds with timeout
**Impact:** Low — would cause ping to fail, not affect other functionality
**Mitigation:** `try/finally` block ensures sockets always closed. 3-second timeout prevents hanging.

### T6 — Thread Safety (UI Updates from Background Threads)
**Threat:** Background threads update Qt UI directly causing crashes or data corruption.
**Likelihood:** Medium — common Qt mistake
**Impact:** Medium — application crash
**Mitigation:** All background threads communicate via Qt signals/slots. UI only updated in main thread.

### T7 — Privilege Escalation via dmidecode/nethogs
**Threat:** Attacker exploits sudoers configuration to gain elevated privileges.
**Likelihood:** Low — limited to specific commands only
**Impact:** High — if exploited, attacker gains root
**Mitigation:** sudoers entries use `NOPASSWD` limited to exact command paths only. No wildcard arguments permitted.

### T8 — Log File Injection
**Threat:** Malicious MangoHud log file causes unexpected behavior when parsed.
**Likelihood:** Very Low — requires compromise of MangoHud or log directory
**Impact:** Low — FPS panel would show incorrect data
**Mitigation:** Log parsing wrapped in try/except. Values cast to float with error handling.

---

## Security Decisions

| Decision | Rationale |
|----------|-----------|
| No root execution | Karmac runs entirely as user. Only dmidecode and nethogs use sudo via sudoers |
| Quad9 as default ping host | Privacy-focused, non-profit DNS provider. No Google or Cloudflare by default |
| Open-Meteo for weather | FOSS, EU-based, no API key, no tracking |
| Manual-only speed test | Ookla speed test never runs automatically. User must click Run Test |
| Local-only storage | Settings stored in ~/.config/karmac/ — never uploaded anywhere |
| No telemetry | Zero analytics, crash reporting, or usage tracking of any kind |
| Flatpak sandboxing | Flatpak version runs in restricted sandbox with explicit filesystem permissions |

---

## Out of Scope

The following are explicitly out of scope for this threat model:

- Physical access to the machine
- OS-level vulnerabilities
- Attacks requiring the user to run Karmac as root (not supported)
- Attacks against other applications on the system

---

## Review History

| Date | Version | Changes |
|------|---------|---------|
| June 2026 | 3.0.1 | Initial threat model created |