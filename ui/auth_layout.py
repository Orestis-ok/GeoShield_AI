"""
Branded split-layout for authentication screens.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame

import theme
from config import APP_NAME, APP_TAGLINE, APP_VERSION, AUTHOR_CREDIT, AUTHOR_NAME
from ui.widgets import FeatureRow


def build_auth_page(form_widget: QWidget) -> QWidget:
    page = QWidget()
    layout = QHBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    hero = QFrame()
    hero.setStyleSheet(theme.hero_panel_style())
    hero.setMinimumWidth(460)
    hl = QVBoxLayout(hero)
    hl.setContentsMargins(52, 48, 52, 48)
    hl.setSpacing(12)

    hl.addStretch()
    brand = QLabel("GEOSHIELD")
    brand.setStyleSheet(theme.accent_label_style() + "font-size:12px; letter-spacing:6px;")
    hl.addWidget(brand)

    pro = QLabel("PROFESSIONAL · $20/mo")
    pro.setStyleSheet(theme.pro_badge_style())
    pro.setFixedWidth(160)
    hl.addWidget(pro)

    title = QLabel("Enterprise disaster\nrisk intelligence")
    title.setStyleSheet(theme.title_style(34))
    title.setWordWrap(True)
    hl.addWidget(title)

    desc = QLabel(APP_TAGLINE)
    desc.setStyleSheet(theme.subtitle_style())
    desc.setWordWrap(True)
    hl.addWidget(desc)

    hl.addSpacing(20)
    for icon, t, d in [
        ("◆", "Live meteorological fusion", "Open-Meteo geocoding with humidity, wind, and precipitation models."),
        ("◆", "Multi-hazard scoring", "Flood, wildfire, and landslide indices with composite operational index."),
        ("◆", "Interactive coverage maps", "Pan, zoom, and contextual markers tied to each analysis."),
        ("◆", "Science Lab", "48h instruments, model decomposition, 24h–7d projections, research exports."),
        ("◆", "Stakeholder-ready exports", "Branded HTML intelligence reports for briefings and compliance."),
    ]:
        hl.addWidget(FeatureRow(icon, t, d))

    hl.addStretch()
    author = QLabel(AUTHOR_CREDIT)
    author.setStyleSheet(theme.accent_label_style())
    hl.addWidget(author)
    foot = QLabel(f"{APP_NAME} v{APP_VERSION} · {AUTHOR_NAME}")
    foot.setStyleSheet(theme.muted_style())
    hl.addWidget(foot)

    layout.addWidget(hero, stretch=5)

    form_col = QFrame()
    form_col.setStyleSheet(f"background:{theme.BG_PRIMARY};")
    fl = QVBoxLayout(form_col)
    fl.setContentsMargins(56, 48, 56, 48)
    fl.setAlignment(Qt.AlignmentFlag.AlignCenter)

    card = QFrame()
    card.setMaximumWidth(440)
    card.setStyleSheet(theme.card_style(elevated=True))
    cl = QVBoxLayout(card)
    cl.setContentsMargins(32, 32, 32, 32)
    cl.addWidget(form_widget)
    fl.addWidget(card)
    layout.addWidget(form_col, stretch=4)

    return page
