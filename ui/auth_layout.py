"""
Shared split-layout frame for login and signup pages.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame

import theme
from config import APP_NAME, APP_TAGLINE, APP_VERSION


def build_auth_page(form_widget: QWidget) -> QWidget:
    """Wrap a form widget in a branded two-column auth layout."""
    page = QWidget()
    layout = QHBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    hero = QFrame()
    hero.setStyleSheet(theme.hero_panel_style())
    hero.setMinimumWidth(420)
    hl = QVBoxLayout(hero)
    hl.setContentsMargins(48, 48, 48, 48)
    hl.setSpacing(16)

    hl.addStretch()
    brand = QLabel("GEOSHIELD")
    brand.setStyleSheet(theme.accent_label_style() + "letter-spacing:5px; font-size:12px;")
    hl.addWidget(brand)

    title = QLabel("Protect what matters.\nKnow the risk before it strikes.")
    title.setStyleSheet(theme.title_style(30))
    title.setWordWrap(True)
    hl.addWidget(title)

    desc = QLabel(
        f"{APP_TAGLINE}. Enterprise-grade flood, wildfire, and landslide "
        "intelligence powered by live weather and historical disaster archives."
    )
    desc.setStyleSheet(theme.subtitle_style())
    desc.setWordWrap(True)
    hl.addWidget(desc)

    hl.addSpacing(24)
    feats = [
        "Live Open-Meteo weather integration",
        "Multi-factor composite risk scoring",
        "Historical disaster database",
        "Exportable HTML intelligence reports",
    ]
    for f in feats:
        row = QLabel(f"✓  {f}")
        row.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:13px;")
        hl.addWidget(row)

    hl.addStretch()
    ver = QLabel(f"v{APP_VERSION}")
    ver.setStyleSheet(theme.muted_style())
    hl.addWidget(ver)

    layout.addWidget(hero, stretch=5)

    form_col = QFrame()
    form_col.setStyleSheet(f"background:{theme.BG_PRIMARY};")
    fl = QVBoxLayout(form_col)
    fl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    fl.addWidget(form_widget)
    layout.addWidget(form_col, stretch=4)

    return page
