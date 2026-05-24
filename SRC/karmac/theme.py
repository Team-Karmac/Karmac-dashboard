"""
Karmac Dashboard — Theme System
Defines dark and light themes and applies them to the application.
"""

COLORS = {
    "dark": {
        "bg_primary":       "#0a0a18",
        "bg_secondary":     "#0f0f22",
        "bg_panel":         "#13132a",
        "bg_panel_hover":   "#1a1a35",
        "border":           "rgba(255, 255, 255, 0.07)",
        "border_accent":    "rgba(255, 255, 255, 0.14)",
        "text_primary":     "#f0f0ff",
        "text_secondary":   "rgba(240, 240, 255, 0.55)",
        "text_muted":       "rgba(240, 240, 255, 0.28)",
        "accent_blue":      "#4361ee",
        "accent_green":     "#06d6a0",
        "accent_amber":     "#ffbe0b",
        "accent_red":       "#ff4d6d",
        "scrollbar":        "rgba(255, 255, 255, 0.08)",
        "scrollbar_hover":  "rgba(255, 255, 255, 0.16)",
    },
    "light": {
        "bg_primary":       "#eeeef8",
        "bg_secondary":     "#e4e4f0",
        "bg_panel":         "#ffffff",
        "bg_panel_hover":   "#f5f5ff",
        "border":           "rgba(0, 0, 0, 0.07)",
        "border_accent":    "rgba(0, 0, 0, 0.13)",
        "text_primary":     "#0d0d1f",
        "text_secondary":   "rgba(13, 13, 31, 0.55)",
        "text_muted":       "rgba(13, 13, 31, 0.32)",
        "accent_blue":      "#4361ee",
        "accent_green":     "#06b887",
        "accent_amber":     "#d4a000",
        "accent_red":       "#e8003d",
        "scrollbar":        "rgba(0, 0, 0, 0.08)",
        "scrollbar_hover":  "rgba(0, 0, 0, 0.16)",
    }
}



FONT_SIZES = {
    "small": {
        "panel_title":    9,
        "panel_value":   28,
        "panel_subtitle":11,
        "panel_unit":    10,
        "sidebar_title": 16,
        "nav_button":    12,
    },
    "medium": {
        "panel_title":   10,
        "panel_value":   34,
        "panel_subtitle":13,
        "panel_unit":    12,
        "sidebar_title": 19,
        "nav_button":    13,
    },
    "large": {
        "panel_title":   12,
        "panel_value":   40,
        "panel_subtitle":15,
        "panel_unit":    13,
        "sidebar_title": 22,
        "nav_button":    15,
    },
}

def get_stylesheet(theme: str, font_size: str = 'medium') -> str:
    c = COLORS.get(theme, COLORS["dark"])
    f = FONT_SIZES.get(font_size, FONT_SIZES["medium"])
    return f"""
    QWidget {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
        font-family: 'Ubuntu', 'Segoe UI', 'Helvetica Neue', sans-serif;
        font-size: 14px;
        border: none;
        outline: none;
    }}

    QMainWindow {{
        background-color: {c['bg_primary']};
    }}

    /* ── Panel cards ── */
    #panel {{
        background-color: {c['bg_panel']};
        border: 1px solid {c['border_accent']};
        border-radius: 14px;
        padding: 0px;
    }}

    /* ── Panel inner content ── */
    #panel-inner {{
        background-color: transparent;
        padding: 20px 22px 20px 22px;
    }}

    #panel-title {{
        color: {c['text_muted']};
        font-size: {f['panel_title']}px;
        font-weight: 700;
        letter-spacing: 0.14em;
    }}

    #section-title {{
        color: {c['text_muted']};
        font-size: {f['panel_title']}px;
        font-weight: 700;
        letter-spacing: 0.14em;
    }}

    #panel-value {{
        color: {c['text_primary']};
        font-size: {f['panel_value']}px;
        font-weight: 300;
        letter-spacing: -0.02em;
    }}

    #panel-subtitle {{
        color: {c['text_secondary']};
        font-size: {f['panel_subtitle']}px;
        font-weight: 400;
    }}

    #panel-unit {{
        color: {c['text_muted']};
        font-size: {f['panel_unit']}px;
    }}

    #panel-accent-bar {{
        background-color: {c['accent_blue']};
        border-top-left-radius: 14px;
        border-top-right-radius: 14px;
        min-height: 3px;
        max-height: 3px;
    }}

    /* ── Sidebar ── */
    #sidebar {{
        background-color: {c['bg_secondary']};
        border-right: 1px solid {c['border_accent']};
    }}

    #sidebar-title {{
        color: {c['text_primary']};
        font-size: {f['sidebar_title']}px;
        font-weight: 700;
        letter-spacing: 0.02em;
    }}

    #sidebar-tagline {{
        color: {c['text_muted']};
        font-size: 10px;
        font-style: italic;
        letter-spacing: 0.04em;
    }}

    #nav-button {{
        background-color: transparent;
        color: {c['text_secondary']};
        border: none;
        border-radius: 9px;
        padding: 9px 14px;
        text-align: left;
        font-size: {f['nav_button']}px;
        font-weight: 500;
        letter-spacing: 0.01em;
    }}

    #nav-button:hover {{
        background-color: {c['bg_panel']};
        color: {c['text_primary']};
    }}

    #nav-button:checked {{
        background-color: {c['bg_panel']};
        color: {c['accent_blue']};
    }}

    #version-label {{
        color: {c['text_muted']};
        font-size: 10px;
        letter-spacing: 0.08em;
    }}

    /* ── Settings ── */
    #settings-label {{
        color: {c['text_secondary']};
        font-size: 13px;
    }}

    QCheckBox {{
        color: {c['text_secondary']};
        font-size: 13px;
        spacing: 10px;
    }}

    QCheckBox::indicator {{
        width: 17px;
        height: 17px;
        border-radius: 5px;
        border: 1px solid {c['border_accent']};
        background-color: {c['bg_panel']};
    }}

    QCheckBox::indicator:checked {{
        background-color: {c['accent_blue']};
        border-color: {c['accent_blue']};
    }}

    QComboBox {{
        background-color: {c['bg_panel']};
        color: {c['text_primary']};
        border: 1px solid {c['border_accent']};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        min-width: 150px;
    }}

    QComboBox::drop-down {{ border: none; width: 24px; }}

    QComboBox QAbstractItemView {{
        background-color: {c['bg_panel']};
        color: {c['text_primary']};
        border: 1px solid {c['border_accent']};
        border-radius: 8px;
        selection-background-color: {c['accent_blue']};
    }}

    QLineEdit {{
        background-color: {c['bg_panel']};
        color: {c['text_primary']};
        border: 1px solid {c['border_accent']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }}

    QLineEdit:focus {{ border-color: {c['accent_blue']}; }}

    QPushButton {{
        background-color: {c['accent_blue']};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 13px;
        font-weight: 600;
    }}

    QPushButton:hover {{ background-color: #5472f0; }}
    QPushButton:pressed {{ background-color: #3251dc; }}

    QPushButton#secondary {{
        background-color: {c['bg_panel']};
        color: {c['text_secondary']};
        border: 1px solid {c['border_accent']};
    }}

    QPushButton#secondary:hover {{
        background-color: {c['bg_panel_hover']};
        color: {c['text_primary']};
    }}

    /* ── Scrollbar ── */
    QScrollBar:vertical {{
        background: transparent;
        width: 5px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {c['scrollbar']};
        border-radius: 3px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{ background: {c['scrollbar_hover']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

    QFrame[frameShape="4"] {{ color: {c['border']}; }}
    """


def apply_theme(app, theme: str, font_size: str = "medium"):
    app.setStyleSheet(get_stylesheet(theme, font_size))


def get_color(theme: str, key: str) -> str:
    return COLORS.get(theme, COLORS["dark"]).get(key, "#ffffff")