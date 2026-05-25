"""
Karmac Dashboard — Hardware Brand & Specs Panel
Displays system hardware information including CPU, GPU, RAM, and storage.
"""

import subprocess
import psutil
import os
import re
import platform
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication
from karmac.panels.base import BasePanel
from karmac.settings import Settings


def get_cpu_name() -> str:
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    return line.split(":")[1].strip()
    except Exception:
        pass
    return "Unknown CPU"


def get_gpu_name() -> str:
    try:
        result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)
        for line in result.stdout.splitlines():
            if any(gpu in line.upper() for gpu in ("VGA", "3D", "DISPLAY")):
                # Find all bracketed sections
                brackets = re.findall(r"\[([^\[\]]+)\]", line)
                is_amd = "amd" in line.lower() or "ati" in line.lower() or "radeon" in line.lower()
                is_nvidia = "nvidia" in line.lower() or "geforce" in line.lower()

                if brackets:
                    # Last bracket usually has the most specific model name
                    # Pick the one that looks most like a GPU model
                    model = None
                    for b in reversed(brackets):
                        if any(k in b.upper() for k in ("RADEON", "GEFORCE", "RTX", "GTX", "RX", "VEGA", "NAVI", "ARC")):
                            model = b
                            break
                    if not model:
                        model = brackets[-1]

                    if is_amd and not model.upper().startswith("AMD"):
                        return f"AMD {model}"
                    elif is_nvidia and not model.upper().startswith("NVIDIA"):
                        return f"NVIDIA {model}"
                    # Clean up OEM/multiple model listings
                    # Take everything before first "/" or "OEM"
                    model = re.split(r"\s+OEM|\s*/", model)[0].strip()
                    return model

                # No brackets — clean up the raw string
                parts = line.split(":")
                if len(parts) >= 3:
                    name = ":".join(parts[2:]).strip()
                    name = re.sub(r"Advanced Micro Devices, Inc\.?", "AMD", name)
                    name = re.sub(r"\s+", " ", name).strip()
                    return name
    except Exception:
        pass
    return "Unknown GPU"


def get_ram_total() -> str:
    try:
        mem = psutil.virtual_memory()
        gb = mem.total / (1024 ** 3)
        for size in [2, 4, 8, 16, 32, 64, 128]:
            if abs(gb - size) < 1:
                return f"{size} GB"
        return f"{gb:.1f} GB"
    except Exception:
        return "Unknown"


def get_ram_speed() -> str:
    try:
        result = subprocess.run(
            ["sudo", "dmidecode", "-t", "memory"],
            capture_output=True, text=True, timeout=5
        )
        speeds = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("Speed:") and "MT/s" in line:
                speed = line.split(":")[1].strip()
                if speed not in ("Unknown", ""):
                    speeds.append(speed)
        if speeds:
            return max(set(speeds), key=speeds.count)
    except Exception:
        pass
    return "Unknown"


def get_storage_total() -> str:
    try:
        total = 0
        seen = set()
        for p in psutil.disk_partitions():
            if any(skip in p.fstype for skip in ('squash', 'tmpfs', 'devtmpfs')):
                continue
            if p.mountpoint in seen:
                continue
            try:
                usage = psutil.disk_usage(p.mountpoint)
                total += usage.total
                seen.add(p.mountpoint)
            except Exception:
                continue
        if total == 0:
            return "Unknown"
        tb = total / (1024 ** 4)
        if tb >= 1:
            return f"{tb:.1f} TB"
        gb = total / (1024 ** 3)
        return f"{gb:.0f} GB"
    except Exception:
        return "Unknown"


def get_motherboard() -> str:
    try:
        for path in ["/sys/class/dmi/id/board_name", "/sys/class/dmi/id/product_name"]:
            if os.path.exists(path):
                with open(path) as f:
                    name = f.read().strip()
                    if name and name not in ("None", "To be filled by O.E.M."):
                        return name
    except Exception:
        pass
    return "Unknown"


def get_os_info() -> str:
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=")[1].strip().strip('"')
    except Exception:
        pass
    return "Linux"


def get_kernel_version() -> str:
    try:
        return platform.release()
    except Exception:
        return "Unknown"


def get_desktop_environment() -> str:
    """Get the current desktop environment."""
    de = os.environ.get("XDG_CURRENT_DESKTOP", "")
    if de:
        return de
    de = os.environ.get("DESKTOP_SESSION", "")
    if de:
        return de.capitalize()
    return "Unknown"




# EDID manufacturer ID to brand name lookup
EDID_MANUFACTURERS = {
    "AAC": "AcerView", "ACR": "Acer", "AOC": "AOC", "AIC": "AG Neovo",
    "APP": "Apple", "AST": "AST Research", "AUO": "AU Optronics",
    "BNQ": "BenQ", "BOE": "BOE", "CMI": "InnoLux", "CMN": "Innolux",
    "CPL": "Compal", "CPQ": "Compaq", "CTX": "CTX", "DEL": "Dell",
    "DPC": "Delta", "DWE": "Daewoo", "ECS": "ELITEGROUP", "EIZ": "EIZO",
    "ENC": "Eizo Nanao", "EPH": "Epiphany", "EXN": "Exlim", "FUS": "Fujitsu Siemens",
    "GGL": "Google", "GSM": "LG", "GWY": "Gateway", "HEI": "Hyundai",
    "HIT": "Hitachi", "HPN": "HP", "HPQ": "HP", "HSD": "HannStar",
    "HTC": "Hitachi", "HWP": "HP", "IBM": "IBM", "ICL": "Fujitsu ICL",
    "IFS": "InFocus", "IQT": "Hyundai", "IVM": "Iiyama", "KDS": "Korea Data Systems",
    "KFC": "KFC Computek", "LEN": "Lenovo", "LGD": "LG", "LGP": "LG Philips",
    "LNK": "LINK Technologies", "LPL": "LG Philips", "MAX": "Maxdata",
    "MEI": "Panasonic", "MEL": "Mitsubishi", "MSI": "MSI", "MST": "MS Telematica",
    "MTC": "Mitac", "NAN": "Nanao", "NEC": "NEC", "NVD": "Nvidia",
    "OQI": "OPTIQUEST", "PHL": "Philips", "PIO": "Pioneer", "PLN": "Planar",
    "PNR": "Planar", "PTS": "ProView", "QDS": "Quanta Display",
    "REL": "Relisys", "SAM": "Samsung", "SAN": "Samsung", "SBI": "Smartboard",
    "SEC": "Samsung", "SGI": "SGI", "SHP": "Sharp", "SNY": "Sony",
    "SRC": "Shamrock", "STP": "Sceptre", "SYN": "Synaptics", "TAT": "Tatung",
    "TOS": "Toshiba", "TSB": "Toshiba", "UNM": "Unisys", "VES": "Vestel",
    "VIT": "Visitec", "VIZ": "VIZIO", "VSC": "ViewSonic", "WTC": "Wen Technology",
    "ZCM": "Zenith", "AOO": "AOC", "AUS": "ASUS", "ASU": "ASUS", "BTC": "Behaviour Tech", "MSI": "MSI", "GBT": "Gigabyte", "RTK": "Realtek", "HKC": "HKC", "INN": "Innovision", "PKB": "Packard Bell",
}


def decode_edid_manufacturer(edid: bytes) -> str:
    """Decode the 3-letter manufacturer code from EDID bytes 8-9."""
    try:
        if len(edid) < 10:
            return ""
        # Bytes 8-9 contain packed 5-bit characters
        b1, b2 = edid[8], edid[9]
        c1 = chr(((b1 >> 2) & 0x1F) + 64)
        c2 = chr((((b1 & 0x03) << 3) | ((b2 >> 5) & 0x07)) + 64)
        c3 = chr((b2 & 0x1F) + 64)
        code = c1 + c2 + c3
        return EDID_MANUFACTURERS.get(code, code)
    except Exception:
        return ""


def get_ram_details() -> list:
    """Get RAM stick details including make, model, type and speed."""
    sticks = []
    try:
        result = subprocess.run(
            ["sudo", "dmidecode", "-t", "memory"],
            capture_output=True, text=True, timeout=5
        )
        current = {}
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("Memory Device"):
                if current.get("size") and current["size"] != "No Module Installed":
                    sticks.append(current)
                current = {}
            elif ":" in line:
                key, _, val = line.partition(":")
                current[key.strip().lower().replace(" ", "_")] = val.strip()
        if current.get("size") and current["size"] != "No Module Installed":
            sticks.append(current)
    except Exception:
        pass
    return sticks



# Drive model prefix to manufacturer lookup
DRIVE_MANUFACTURERS = {
    "Force": "Corsair", "MP": "Corsair", "Corsair": "Corsair",
    "Samsung": "Samsung", "870": "Samsung", "980": "Samsung", "990": "Samsung",
    "970": "Samsung", "860": "Samsung", "850": "Samsung",
    "WD": "Western Digital", "Western": "Western Digital",
    "Seagate": "Seagate", "Barracuda": "Seagate", "FireCuda": "Seagate",
    "Toshiba": "Toshiba", "TOSHIBA": "Toshiba",
    "Crucial": "Crucial", "MX": "Crucial", "BX": "Crucial", "P": "Crucial",
    "Kingston": "Kingston", "SV300": "Kingston", "SA400": "Kingston",
    "SanDisk": "SanDisk", "Ultra": "SanDisk",
    "Intel": "Intel", "SSDPE": "Intel", "SSDSC": "Intel",
    "Hitachi": "Hitachi", "HTS": "Hitachi", "HDS": "Hitachi",
    "HGST": "HGST", "HUH": "HGST",
    "SK": "SK Hynix", "Hynix": "SK Hynix",
    "Micron": "Micron", "MTFD": "Micron",
    "ADATA": "ADATA", "XPG": "ADATA",
    "PNY": "PNY", "CS": "PNY",
    "Patriot": "Patriot", "Burst": "Patriot",
    "Team": "TeamGroup", "TM8": "TeamGroup",
    "Lexar": "Lexar", "LNM": "Lexar",
    "Sabrent": "Sabrent", "Rocket": "Sabrent",
    "MSI": "MSI", "SPATIUM": "MSI",
    "Gigabyte": "Gigabyte", "GP-GSM": "Gigabyte",
    "GOODRAM": "GOODRAM", "SSDPR": "GOODRAM",
    "Transcend": "Transcend", "TS": "Transcend",
}


def get_drive_manufacturer(model: str) -> str:
    """Try to identify the drive manufacturer from the model name."""
    for prefix, brand in DRIVE_MANUFACTURERS.items():
        if model.startswith(prefix) or prefix in model:
            return brand
    return ""

def get_drive_details() -> list:
    """Get hard drive make, model and interface."""
    drives = []
    try:
        import json
        result = subprocess.run(
            ["lsblk", "-d", "-o", "NAME,MODEL,TRAN,SIZE,ROTA", "--json"],
            capture_output=True, text=True, timeout=5
        )
        data = json.loads(result.stdout)
        for device in data.get("blockdevices", []):
            name  = device.get("name", "")
            model = (device.get("model") or "").strip()
            tran  = (device.get("tran") or "").strip()
            size  = (device.get("size") or "").strip()
            rota  = str(device.get("rota", "1")).strip()
            if True:

                # Skip loop devices and small boot devices
                if name.startswith("loop") or name.startswith("sr"):
                    continue

                # Determine drive type
                if tran == "nvme" or "nvme" in name.lower():
                    drive_type = "NVMe SSD"
                elif tran == "sata":
                    drive_type = "SATA SSD" if rota == "0" else "SATA HDD"
                elif tran == "usb":
                    drive_type = "USB"
                elif rota == "0":
                    drive_type = "SSD"
                else:
                    drive_type = "HDD"

                clean_model = model.replace("_", " ").strip()
                manufacturer = get_drive_manufacturer(clean_model)
                drives.append({
                    "name":         name,
                    "model":        clean_model,
                    "manufacturer": manufacturer,
                    "type":         drive_type,
                    "size":         size,
                })
    except Exception:
        pass
    return drives

def get_monitor_names() -> list:
    """Get monitor make and model from EDID data."""
    monitors = []
    try:
        import glob
        # Find all connected displays via drm
        for card in sorted(glob.glob("/sys/class/drm/card*-*")):
            status_file = os.path.join(card, "status")
            edid_file   = os.path.join(card, "edid")
            if not os.path.exists(status_file) or not os.path.exists(edid_file):
                continue
            try:
                with open(status_file) as f:
                    if f.read().strip() != "connected":
                        continue
                with open(edid_file, "rb") as f:
                    edid = f.read()
                if len(edid) < 128:
                    continue
                # Parse monitor name from EDID descriptor blocks
                name = None
                for i in range(4):
                    offset = 54 + i * 18
                    if edid[offset:offset+3] == b'\x00\x00\x00':
                        descriptor_type = edid[offset+3]
                        if descriptor_type == 0xFC:  # Monitor name
                            raw = edid[offset+5:offset+18]
                            name = raw.decode("ascii", errors="ignore").strip().rstrip("\n")
                            break
                if name:
                    manufacturer = decode_edid_manufacturer(edid)
                    if manufacturer and manufacturer.upper() not in name.upper():
                        monitors.append(f"{manufacturer} {name}")
                    else:
                        monitors.append(name)
            except Exception:
                continue
    except Exception:
        pass

    # Fallback: use xrandr to get monitor names
    if not monitors:
        try:
            result = subprocess.run(
                ["xrandr", "--verbose"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if "Monitor name:" in line:
                    name = line.split("Monitor name:")[1].strip()
                    if name:
                        monitors.append(name)
        except Exception:
            pass

    return monitors if monitors else []

def get_display_info() -> list:
    """Get monitor name, resolution and refresh rate for all screens."""
    displays = []
    try:
        monitor_names = get_monitor_names()
        app = QApplication.instance()
        if app:
            screens = app.screens()
            for i, screen in enumerate(screens):
                geo  = screen.geometry()
                res  = f"{geo.width()}x{geo.height()}"
                rate = f"{screen.refreshRate():.0f} Hz"
                if i < len(monitor_names):
                    name = monitor_names[i]
                else:
                    name = screen.name() or f"Display {i+1}"
                displays.append(f"{name}  {res} @ {rate}")
    except Exception:
        pass

    # Fallback using xrandr
    if not displays:
        try:
            result = subprocess.run(
                ["xrandr", "--current"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if " connected" in line:
                    # Get resolution and refresh rate
                    match = re.search(r'(\d+x\d+)\+\d+\+\d+', line)
                    name_match = re.match(r'^(\S+)', line)
                    name = name_match.group(1) if name_match else "Display"
                    res = match.group(1) if match else "Unknown"
                    displays.append(f"{name}  {res}")
        except Exception:
            pass

    return displays if displays else ["Unknown"]


class HardwarePanel(BasePanel):
    """Displays system hardware brand and specifications."""

    REFRESH_INTERVAL = 0
    ACCENT_COLOR = "#c17c3a"

    def __init__(self, settings: Settings, parent=None):
        super().__init__(settings, title="Hardware", parent=parent)

    def build_content(self, layout: QVBoxLayout):
        ram_total = get_ram_total()
        ram_speed = get_ram_speed()
        ram_str   = f"{ram_total} — {ram_speed}" if ram_speed != "Unknown" else ram_total

        specs = [
            ("CPU",     get_cpu_name()),
            ("GPU",     get_gpu_name()),
            ("Board",   get_motherboard()),
            ("OS",      get_os_info()),
            ("Kernel",  get_kernel_version()),
            ("Desktop", get_desktop_environment()),
        ]

        for label, value in specs:
            layout.addWidget(self._make_spec_row(label, value))

        # RAM sticks - combine into summary
        ram_sticks = get_ram_details()
        if ram_sticks:
            stick    = ram_sticks[0]
            total    = get_ram_total()
            ram_type = stick.get("type", "").strip()
            speed    = stick.get("configured_memory_speed") or stick.get("speed", "")
            speed    = speed.strip() if speed else ""
            mfr      = stick.get("manufacturer", "").strip()
            mfr_map  = {
                "G-Skill": "G.Skill", "Kingston": "Kingston", "Corsair": "Corsair",
                "Crucial": "Crucial", "Samsung": "Samsung", "Hynix": "SK Hynix",
                "SK Hynix": "SK Hynix", "Micron": "Micron", "ADATA": "ADATA",
                "Patriot": "Patriot", "TeamGroup": "TeamGroup",
            }
            mfr = mfr_map.get(mfr, mfr)
            parts = []
            if mfr and mfr not in ("Unknown", "Not Specified", ""):
                parts.append(mfr)
            parts.append(total)
            if ram_type and ram_type not in ("Unknown", ""):
                parts.append(ram_type)
            if speed and speed not in ("Unknown", ""):
                parts.append(speed)
            layout.addWidget(self._make_spec_row("RAM", "  ".join(parts)))
        else:
            ram_str = get_ram_total()
            layout.addWidget(self._make_spec_row("RAM", ram_str))

        # Drives
        drive_details = get_drive_details()
        if drive_details:
            for i, drive in enumerate(drive_details):
                label = f"Hard Drive {i+1}" if len(drive_details) > 1 else "Hard Drive"
                mfr   = drive.get("manufacturer", "")
                # Clean up drive name — remove redundant type info already in type field
                model = drive["model"]
                for strip in ("nvme", "NVMe", "NVME", "ssd", "SSD", "hdd", "HDD"):
                    model = re.sub(rf"\b{strip}\b", "", model, flags=re.IGNORECASE).strip()
                model = re.sub(r"\s+", " ", model).strip()
                if mfr and mfr.upper() not in model.upper():
                    value = f"{mfr} {model}  ({drive['type']}  {drive['size']})"
                else:
                    value = f"{model}  ({drive['type']}  {drive['size']})"
                layout.addWidget(self._make_spec_row(label, value))
        else:
            layout.addWidget(self._make_spec_row("Storage", get_storage_total()))

        # Displays
        displays = get_display_info()
        for i, display in enumerate(displays):
            label = "Display" if len(displays) == 1 else f"Display {i+1}"
            layout.addWidget(self._make_spec_row(label, display))

    def _make_spec_row(self, label: str, value: str) -> QWidget:
        row = QWidget()
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(1)

        label_widget = QLabel(label.upper())
        label_widget.setStyleSheet(
            "color: rgba(240,240,255,0.35);"
            "font-size: 9px;"
            "font-weight: 700;"
            "letter-spacing: 0.12em;"
        )

        value_widget = QLabel(value)
        value_widget.setObjectName("panel-subtitle")
        value_widget.setWordWrap(True)
        value_widget.setStyleSheet("color: #f0f0ff;")

        layout.addWidget(label_widget)
        layout.addWidget(value_widget)

        return row

    def refresh(self):
        pass