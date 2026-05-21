"""
Application settings and about.
"""
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
)

import theme
from config import APP_NAME, APP_VERSION, APP_BUILD, APP_TAGLINE, ORG_NAME
from database import Database
from ui.widgets import SectionTitle
from PyQt6.QtCore import pyqtSignal


class SettingsView(QWidget):
    history_cleared = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._db = Database()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(20)

        layout.addWidget(
            SectionTitle("Settings", "Application preferences and product information.")
        )

        about = QFrame()
        about.setStyleSheet(theme.card_style(elevated=True))
        al = QVBoxLayout(about)
        al.setContentsMargins(28, 24, 28, 24)
        al.setSpacing(10)

        name = QLabel(APP_NAME)
        name.setStyleSheet(theme.title_style(26))
        al.addWidget(name)

        tag = QLabel(APP_TAGLINE)
        tag.setStyleSheet(theme.subtitle_style())
        al.addWidget(tag)

        ver = QLabel(f"Version {APP_VERSION} · Build {APP_BUILD}")
        ver.setStyleSheet(theme.muted_style())
        al.addWidget(ver)

        al.addWidget(QLabel(f"© {ORG_NAME}"))

        desc = QLabel(
            "GeoShield delivers geographic risk intelligence by combining live "
            "meteorological data with curated historical disaster records — built "
            "for analysts, emergency planners, and operations teams."
        )
        desc.setStyleSheet(theme.subtitle_style())
        desc.setWordWrap(True)
        al.addWidget(desc)
        layout.addWidget(about)

        data_card = QFrame()
        data_card.setStyleSheet(theme.card_style())
        dl = QVBoxLayout(data_card)
        dl.setContentsMargins(24, 22, 24, 22)
        dl.setSpacing(8)
        dl.addWidget(QLabel("Data & privacy"))
        privacy = QLabel(
            "Accounts and analysis history are stored locally on this device. "
            "Weather data is retrieved from Open-Meteo. No cloud sync is enabled."
        )
        privacy.setStyleSheet(theme.subtitle_style())
        privacy.setWordWrap(True)
        dl.addWidget(privacy)
        layout.addWidget(data_card)

        actions = QHBoxLayout()
        clear_btn = QPushButton("Clear analysis history")
        clear_btn.setProperty("class", "secondary")
        clear_btn.clicked.connect(self._clear_history)
        actions.addWidget(clear_btn)
        actions.addStretch()
        layout.addLayout(actions)
        layout.addStretch()

    def set_user(self, user: dict | None):
        self._user = user

    def _clear_history(self):
        if not self._user:
            return
        reply = QMessageBox.question(
            self,
            "Clear history",
            "Delete all saved analyses for your account? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._db.clear_user_history(self._user["id"])
            self.history_cleared.emit()
            QMessageBox.information(self, "GeoShield", "Analysis history cleared.")
