"""
GeoShield — global theme and stylesheet helpers.
"""

# Palette
BG_PRIMARY = "#0f1419"
BG_SECONDARY = "#1a2332"
BG_CARD = "#1e2a3a"
BG_INPUT = "#152030"
BG_HOVER = "#243447"

ACCENT = "#0ea5e9"
ACCENT_HOVER = "#0284c7"
ACCENT_MUTED = "#0c4a6e"

TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED = "#64748b"

BORDER = "#2d3f54"
BORDER_FOCUS = "#0ea5e9"

SUCCESS = "#10b981"
WARNING = "#f59e0b"
DANGER = "#ef4444"
CRITICAL = "#dc2626"

RISK_LOW = "#22c55e"
RISK_MODERATE = "#eab308"
RISK_HIGH = "#f97316"
RISK_CRITICAL = "#ef4444"

FONT_FAMILY = "Segoe UI, Inter, Arial, sans-serif"


def risk_color(level: str) -> str:
    return {
        "low": RISK_LOW,
        "moderate": RISK_MODERATE,
        "high": RISK_HIGH,
        "critical": RISK_CRITICAL,
    }.get(level, TEXT_MUTED)


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

QLineEdit, QTextEdit {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    selection-background-color: {ACCENT_MUTED};
}}

QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {BORDER_FOCUS};
}}

QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}

QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 11px 20px;
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
    border-color: {TEXT_MUTED};
}}

QPushButton[class="ghost"] {{
    background-color: transparent;
    color: {ACCENT};
    padding: 6px 12px;
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
    background-color: #2a1515;
    border-color: {DANGER};
}}

QProgressBar {{
    background-color: {BG_INPUT};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    border-radius: 4px;
    background-color: {ACCENT};
}}

QScrollBar:vertical {{
    background: {BG_SECONDARY};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}
"""


def card_style() -> str:
    return f"""
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
    """


def title_style(size: int = 28) -> str:
    return f"""
        font-size: {size}px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        letter-spacing: -0.5px;
    """


def subtitle_style() -> str:
    return f"font-size: 14px; color: {TEXT_SECONDARY};"


def muted_style() -> str:
    return f"font-size: 12px; color: {TEXT_MUTED};"


def accent_label_style() -> str:
    return f"font-size: 11px; font-weight: 600; color: {ACCENT}; letter-spacing: 1px;"
