"""
GeoShield Pro — design system and global styles.
"""

# Core palette — deep navy enterprise
BG_PRIMARY = "#060a10"
BG_SECONDARY = "#0b1220"
BG_TERTIARY = "#101a2b"
BG_CARD = "#131f33"
BG_CARD_ELEVATED = "#182640"
BG_INPUT = "#0d1626"
BG_HOVER = "#1e2f4a"
BG_GLASS = "rgba(19, 31, 51, 0.72)"

ACCENT = "#3b9eff"
ACCENT_HOVER = "#60b4ff"
ACCENT_SOFT = "#1a3a5c"
ACCENT_MUTED = "#0f2844"
ACCENT_GLOW = "rgba(59, 158, 255, 0.35)"

GOLD = "#d4a853"
GOLD_SOFT = "#2a2418"
PRO_BADGE = "#c9a227"

TEXT_PRIMARY = "#f4f7fb"
TEXT_SECONDARY = "#9eb0c8"
TEXT_MUTED = "#5c6f88"

BORDER = "#243550"
BORDER_LIGHT = "#2f4568"
BORDER_FOCUS = "#3b9eff"

SUCCESS = "#22c58b"
WARNING = "#f5b942"
DANGER = "#f05252"
CRITICAL = "#e11d48"

RISK_LOW = "#34d399"
RISK_MODERATE = "#fbbf24"
RISK_HIGH = "#fb923c"
RISK_CRITICAL = "#f87171"

FONT_FAMILY = '"Segoe UI", "Inter", system-ui, sans-serif'
FONT_MONO = "Consolas, monospace"

GRADIENT_HERO = (
    "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
    f"stop:0 {BG_SECONDARY}, stop:0.45 #0d1a30, stop:1 #0a1628)"
)


def risk_color(level: str) -> str:
    return {
        "low": RISK_LOW,
        "moderate": RISK_MODERATE,
        "high": RISK_HIGH,
        "critical": RISK_CRITICAL,
    }.get(level.lower(), TEXT_MUTED)


GLOBAL_STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {BG_PRIMARY};
    color: {TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 13px;
}}

QLabel {{
    background: transparent;
    color: {TEXT_PRIMARY};
}}

QLineEdit, QTextEdit, QComboBox {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 11px 14px;
    font-size: 13px;
    selection-background-color: {ACCENT_MUTED};
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 1px solid {BORDER_FOCUS};
}}

QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox QAbstractItemView {{
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT_MUTED};
}}

QCheckBox {{
    color: {TEXT_SECONDARY};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid {BORDER};
    background: {BG_INPUT};
}}

QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

QPushButton {{
    background-color: {ACCENT};
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 22px;
    font-weight: 600;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton:pressed {{
    background-color: {ACCENT_MUTED};
}}

QPushButton:disabled {{
    background-color: {BG_HOVER};
    color: {TEXT_MUTED};
}}

QPushButton[class="secondary"] {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
    border-color: {BORDER_LIGHT};
}}

QPushButton[class="ghost"] {{
    background-color: transparent;
    color: {ACCENT};
    padding: 6px 10px;
    font-weight: 600;
}}

QPushButton[class="ghost"]:hover {{
    background-color: {BG_HOVER};
}}

QPushButton[class="danger"] {{
    background-color: transparent;
    color: {DANGER};
    border: 1px solid {BORDER};
}}

QPushButton[class="danger"]:hover {{
    background-color: #2a1218;
    border-color: {DANGER};
}}

QPushButton[class="chip"] {{
    background-color: {BG_INPUT};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    padding: 7px 14px;
    font-weight: 500;
    font-size: 12px;
}}

QPushButton[class="chip"]:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
    border-color: {ACCENT};
}}

QPushButton[class="nav"] {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    text-align: left;
    padding: 12px 14px;
    border-radius: 10px;
    font-weight: 500;
}}

QPushButton[class="nav"]:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton[class="nav-active"] {{
    background-color: {ACCENT_SOFT};
    color: {ACCENT};
    text-align: left;
    padding: 12px 14px;
    border-radius: 10px;
    font-weight: 700;
    border-left: 3px solid {ACCENT};
}}

QProgressBar {{
    background-color: {BG_INPUT};
    border: none;
    border-radius: 6px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    border-radius: 6px;
    background-color: {ACCENT};
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background: {BG_SECONDARY};
    width: 10px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 28px;
}}

QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}

QTableWidget {{
    background-color: {BG_CARD};
    alternate-background-color: {BG_TERTIARY};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 12px;
    color: {TEXT_PRIMARY};
}}

QTableWidget::item {{
    padding: 8px;
}}

QHeaderView::section {{
    background-color: {BG_SECONDARY};
    color: {TEXT_MUTED};
    padding: 10px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
}}

QFrame[class="glass"] {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}
"""


def card_style(elevated: bool = False) -> str:
    bg = BG_CARD_ELEVATED if elevated else BG_CARD
    return f"""
        background-color: {bg};
        border: 1px solid {BORDER};
        border-radius: 14px;
    """


def hero_panel_style() -> str:
    return f"""
        background: {GRADIENT_HERO};
        border-right: 1px solid {BORDER};
    """


def title_style(size: int = 28) -> str:
    return f"""
        font-size: {size}px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        letter-spacing: -0.6px;
    """


def subtitle_style() -> str:
    return f"font-size: 14px; color: {TEXT_SECONDARY}; line-height: 1.5;"


def muted_style() -> str:
    return f"font-size: 12px; color: {TEXT_MUTED};"


def accent_label_style() -> str:
    return (
        f"font-size: 11px; font-weight: 700; color: {ACCENT}; "
        f"letter-spacing: 2px;"
    )


def pro_badge_style() -> str:
    return f"""
        background-color: {GOLD_SOFT};
        color: {PRO_BADGE};
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1px;
    """


def status_chip_style(color: str) -> str:
    return f"""
        background-color: {color}22;
        color: {color};
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid {color}44;
    """


def auth_input_label_style() -> str:
    return f"font-size: 12px; font-weight: 600; color: {TEXT_SECONDARY};"
