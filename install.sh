#!/bin/bash
# ============================================================
#  Karmac Dashboard — Installer
#  Everything you need. Nothing you don't.
#  https://gitlab.com/team.karmac1/Karmac-dashboard
# ============================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Banner
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${WHITE}         Karmac Dashboard Installer        ${BLUE}║${NC}"
echo -e "${BLUE}║${CYAN}   Everything you need. Nothing you don't. ${BLUE}║${NC}"
echo -e "${BLUE}║${WHITE}              Version 3.0.0                ${BLUE}║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Variables
INSTALL_DIR="$HOME/Karmac-dashboard"
VENV_DIR="$HOME/karmac-env"
USERNAME=$(whoami)
ICON_DIR="$HOME/.local/share/icons"
APPS_DIR="$HOME/.local/share/applications"
DESKTOP_DIR="$HOME/Desktop"

# ── Helper functions ─────────────────────────────────────────

info()    { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
step()    { echo -e "\n${WHITE}──────────────────────────────────────${NC}"; echo -e "${WHITE}$1${NC}"; echo -e "${WHITE}──────────────────────────────────────${NC}"; }

# ── Check prerequisites ──────────────────────────────────────

step "Checking prerequisites..."

if [[ "$(uname)" != "Linux" ]]; then
    error "Karmac is only supported on Linux."
fi

if ! command -v python3 &>/dev/null; then
    error "Python 3 is not installed. Please install python3 and try again."
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 10 ]]; then
    error "Python 3.10 or higher is required. You have Python $PYTHON_VERSION."
fi
success "Python $PYTHON_VERSION found"

if ! command -v apt &>/dev/null; then
    warning "apt not found. You may need to install system dependencies manually."
    warning "Required: libxcb-cursor0 lm-sensors nvme-cli librsvg2-bin mangohud nethogs"
fi

# ── Install system dependencies ──────────────────────────────

step "Installing system dependencies..."

sudo apt update -qq

PACKAGES=(
    "libxcb-cursor0"      # Required for Qt to launch on X11
    "lm-sensors"          # Fan speed and temperature monitoring
    "nvme-cli"            # NVMe drive information
    "librsvg2-bin"        # SVG to PNG conversion for app icon
    "mangohud"            # FPS monitoring via game overlay
    "nethogs"             # Per-process network traffic monitoring
    "python3-venv"        # Python virtual environment support
    "python3-full"        # Full Python installation
)

for pkg in "${PACKAGES[@]}"; do
    if dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
        success "$pkg already installed"
    else
        info "Installing $pkg..."
        sudo apt install -y "$pkg" 2>/dev/null && success "$pkg installed" || warning "Could not install $pkg — some features may not work"
    fi
done

# ── Set up Python virtual environment ────────────────────────

step "Setting up Python virtual environment..."

if [[ -d "$VENV_DIR" ]]; then
    info "Virtual environment already exists at $VENV_DIR"
else
    python3 -m venv "$VENV_DIR"
    success "Virtual environment created at $VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# ── Install Python dependencies ──────────────────────────────

step "Installing Python dependencies..."

pip install --upgrade pip -q

PYTHON_PACKAGES=(
    "PySide6>=6.5.0"
    "requests>=2.28.0"
    "psutil>=5.9.0"
    "speedtest-cli>=2.1.3"
)

for pkg in "${PYTHON_PACKAGES[@]}"; do
    info "Installing $pkg..."
    pip install "$pkg" -q && success "$pkg installed" || warning "Could not install $pkg"
done

# ── Configure system permissions ─────────────────────────────

step "Configuring system permissions..."

# RAM details via dmidecode
SUDOERS_LINE="$USERNAME ALL=(ALL) NOPASSWD: /usr/sbin/dmidecode"
if sudo grep -q "$USERNAME.*dmidecode" /etc/sudoers 2>/dev/null; then
    success "dmidecode sudoers entry already exists"
else
    info "Adding dmidecode sudoers entry for RAM details..."
    echo "$SUDOERS_LINE" | sudo tee -a /etc/sudoers > /dev/null
    success "dmidecode sudoers entry added"
fi

# Network traffic via nethogs
NETHOGS_LINE="$USERNAME ALL=(ALL) NOPASSWD: /usr/sbin/nethogs"
if sudo grep -q "$USERNAME.*nethogs" /etc/sudoers 2>/dev/null; then
    success "nethogs sudoers entry already exists"
else
    info "Adding nethogs sudoers entry for network traffic monitoring..."
    echo "$NETHOGS_LINE" | sudo tee -a /etc/sudoers > /dev/null
    success "nethogs sudoers entry added"
fi

# CPU power monitoring via RAPL
RAPL_RULES="/etc/udev/rules.d/99-rapl.rules"
if [[ -f "$RAPL_RULES" ]]; then
    success "RAPL udev rules already exist"
else
    info "Creating RAPL udev rules for CPU power monitoring..."
    sudo tee "$RAPL_RULES" > /dev/null << 'RULES'
SUBSYSTEM=="powercap", KERNEL=="intel-rapl:0", ACTION=="add", RUN+="/bin/chmod a+r /sys/class/powercap/intel-rapl:0/energy_uj"
SUBSYSTEM=="powercap", KERNEL=="intel-rapl:0:0", ACTION=="add", RUN+="/bin/chmod a+r /sys/class/powercap/intel-rapl:0:0/energy_uj"
RULES
    sudo chmod a+r /sys/class/powercap/intel-rapl:0/energy_uj 2>/dev/null || true
    sudo chmod a+r /sys/class/powercap/intel-rapl:0:0/energy_uj 2>/dev/null || true
    success "RAPL udev rules created"
fi

# ── Configure MangoHud ────────────────────────────────────────

step "Configuring MangoHud for FPS monitoring..."

MANGOHUD_DIR="$HOME/.config/MangoHud"
MANGOHUD_CONF="$MANGOHUD_DIR/MangoHud.conf"
MANGOHUD_LOG_DIR="$HOME/.local/share/MangoHud"

mkdir -p "$MANGOHUD_DIR" "$MANGOHUD_LOG_DIR"

if [[ -f "$MANGOHUD_CONF" ]]; then
    success "MangoHud config already exists"
else
    cat > "$MANGOHUD_CONF" << MANGOCFG
output_folder=$MANGOHUD_LOG_DIR
log_interval=100
fps
gpu_stats
cpu_stats
ram
autostart_log=1
MANGOCFG
    success "MangoHud config created"
fi

info "To enable FPS monitoring in Steam games, add 'mangohud %command%' to each game's launch options"

# ── Create app icon ───────────────────────────────────────────

step "Creating app icon..."

mkdir -p "$ICON_DIR"
SVG_ICON="$INSTALL_DIR/Assets/Karmac_Logo.svg"
PNG_ICON="$ICON_DIR/Karmac_Logo.png"

if [[ -f "$SVG_ICON" ]]; then
    rsvg-convert -w 128 -h 128 "$SVG_ICON" -o "$PNG_ICON" && success "App icon created" || warning "Could not create icon"
else
    warning "Logo SVG not found — icon not created"
fi

# ── Create desktop launcher ───────────────────────────────────

step "Creating desktop launcher..."

mkdir -p "$APPS_DIR"

DESKTOP_CONTENT="[Desktop Entry]
Type=Application
Name=Karmac Dashboard
Comment=Everything you need. Nothing you don't.
Exec=bash -c 'source $VENV_DIR/bin/activate && python3 $INSTALL_DIR/SRC/main.py'
Icon=$PNG_ICON
Categories=Utility;System;
Terminal=false
StartupNotify=true"

echo "$DESKTOP_CONTENT" > "$APPS_DIR/karmac.desktop"
chmod +x "$APPS_DIR/karmac.desktop"
success "Desktop launcher created"

if [[ -d "$DESKTOP_DIR" ]]; then
    cp "$APPS_DIR/karmac.desktop" "$DESKTOP_DIR/Karmac.desktop"
    chmod +x "$DESKTOP_DIR/Karmac.desktop"
    gio set "$DESKTOP_DIR/Karmac.desktop" metadata::trusted true 2>/dev/null || true
    success "Desktop shortcut created"
fi

# ── Privacy notice ────────────────────────────────────────────

step "Privacy information..."

echo -e "${CYAN}Karmac is designed to be privacy-focused.${NC}"
echo -e "Outbound connections:"
echo -e "  ${GREEN}✓${NC} Weather: Open-Meteo (FOSS, EU-based, no tracking)"
echo -e "  ${GREEN}✓${NC} Ping: Quad9 (9.9.9.9) — non-profit, privacy-focused DNS"
echo -e "  ${YELLOW}!${NC} Speed Test: Ookla (only when you click Run Test)"
echo -e "  ${GREEN}✓${NC} Everything else is 100% local"

# ── Done ─────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${GREEN}     Karmac Dashboard v3.0.0 installed!    ${BLUE}║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${WHITE}Launch Karmac from your application menu or desktop shortcut.${NC}"
echo -e "${WHITE}Or run manually:${NC}"
echo -e "${CYAN}  source $VENV_DIR/bin/activate${NC}"
echo -e "${CYAN}  cd $INSTALL_DIR/SRC && python3 main.py${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} A system restart may be required for all permission changes to take effect."
echo ""