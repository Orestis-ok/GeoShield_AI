"""
Settings — profile, preferences, subscription, and data controls.
"""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QScrollArea,
)

import theme
from config import (
    APP_NAME,
    APP_VERSION,
    APP_BUILD,
    APP_TAGLINE,
    ORG_NAME,
    REPORTS_DIR,
    AUTHOR_CREDIT,
    AUTHOR_NAME,
    MODEL_VERSION,
    SCIENCE_EXPORT_DIR,
)
from database import Database
from preferences import load_preferences, save_preferences
from ui.widgets import SectionTitle, FeatureRow


class SettingsView(QWidget):
    history_cleared = pyqtSignal()
    preferences_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._db = Database()
        self._prefs = load_preferences()
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(22)

        layout.addWidget(
            SectionTitle(
                "Settings",
                "Configure your workspace, data preferences, and subscription details.",
            )
        )

        # Subscription card
        sub_card = QFrame()
        sub_card.setStyleSheet(theme.card_style(elevated=True))
        sl = QVBoxLayout(sub_card)
        sl.setContentsMargins(28, 24, 28, 24)
        sl.setSpacing(12)
        row = QHBoxLayout()
        plan = QLabel("GeoShield Professional")
        plan.setStyleSheet(theme.title_style(22))
        row.addWidget(plan)
        row.addStretch()
        badge = QLabel("$20 / MONTH")
        badge.setStyleSheet(theme.pro_badge_style())
        row.addWidget(badge)
        sl.addLayout(row)
        sl.addWidget(
            QLabel(
                "Your license includes unlimited regional analyses, interactive maps, "
                "HTML intelligence exports, historical archives, and priority model updates."
            )
        )
        for icon, t, d in [
            ("✓", "Unlimited analyses", "No per-query limits on professional workspaces."),
            ("✓", "Interactive maps", "Leaflet-powered pan/zoom with hazard context."),
            ("✓", "Science Lab", "Full instrument panel, projections, CSV/JSON research exports."),
            ("✓", "Export & compliance", "Branded reports for stakeholders and regulators."),
        ]:
            sl.addWidget(FeatureRow(icon, t, d))
        creator = QLabel(f"{AUTHOR_CREDIT} · Research & product design")
        creator.setStyleSheet(theme.accent_label_style())
        sl.addWidget(creator)
        layout.addWidget(sub_card)

        # Profile
        profile = self._card("Account")
        pl = profile.layout()
        self._profile_name = QLabel("—")
        self._profile_name.setStyleSheet(theme.title_style(18))
        pl.addWidget(self._profile_name)
        self._profile_email = QLabel("—")
        self._profile_email.setStyleSheet(theme.subtitle_style())
        pl.addWidget(self._profile_email)
        layout.addWidget(profile)

        # Preferences
        prefs_card = self._card("Workspace preferences")
        pl = prefs_card.layout()

        pl.addWidget(self._label("Default search location"))
        self._default_loc = QLineEdit()
        self._default_loc.setPlaceholderText("e.g. Athens")
        self._default_loc.setText(self._prefs.get("default_location", ""))
        pl.addWidget(self._default_loc)

        pl.addWidget(self._label("Temperature unit"))
        self._temp_unit = QComboBox()
        self._temp_unit.addItems(["Celsius (°C)", "Fahrenheit (°F)"])
        self._temp_unit.setCurrentIndex(
            1 if self._prefs.get("temperature_unit") == "fahrenheit" else 0
        )
        pl.addWidget(self._temp_unit)

        pl.addWidget(self._label("Map basemap style"))
        self._map_style = QComboBox()
        self._map_style.addItems(["Dark (Carto)", "Streets (OSM)", "Satellite"])
        styles = ["dark", "streets", "satellite"]
        idx = styles.index(self._prefs.get("map_style", "dark"))
        self._map_style.setCurrentIndex(idx)
        pl.addWidget(self._map_style)

        self._remember = QCheckBox("Keep me signed in by default")
        self._remember.setChecked(self._prefs.get("remember_me", True))
        pl.addWidget(self._remember)

        self._markers = QCheckBox("Show disaster markers on interactive map")
        self._markers.setChecked(self._prefs.get("show_disaster_markers", True))
        pl.addWidget(self._markers)

        self._auto_reports = QCheckBox("Open reports folder after export")
        self._auto_reports.setChecked(self._prefs.get("auto_open_reports", True))
        pl.addWidget(self._auto_reports)

        save_btn = QPushButton("Save preferences")
        save_btn.clicked.connect(self._save_prefs)
        pl.addWidget(save_btn)
        layout.addWidget(prefs_card)

        # Data & privacy
        data_card = self._card("Data & privacy")
        dl = data_card.layout()
        dl.addWidget(
            QLabel(
                "Accounts, analyses, and preferences are stored locally on this device. "
                "Weather intelligence is retrieved from Open-Meteo. No cloud sync is enabled."
            )
        )
        path_lbl = QLabel(f"Reports: {REPORTS_DIR}")
        path_lbl.setStyleSheet(theme.muted_style())
        path_lbl.setWordWrap(True)
        dl.addWidget(path_lbl)
        layout.addWidget(data_card)

        # About
        about = self._card("About")
        al = about.layout()
        al.addWidget(QLabel(f"{APP_NAME} · {APP_TAGLINE}"))
        al.addWidget(QLabel(f"Version {APP_VERSION} · Build {APP_BUILD}"))
        al.addWidget(QLabel(f"© {ORG_NAME}"))
        al.addWidget(QLabel(f"Risk model: {MODEL_VERSION}"))
        al.addWidget(QLabel(f"Created {AUTHOR_CREDIT}"))
        al.addWidget(QLabel(f"Science exports: {SCIENCE_EXPORT_DIR}"))
        layout.addWidget(about)

        actions = QHBoxLayout()
        clear_btn = QPushButton("Clear analysis history")
        clear_btn.setProperty("class", "danger")
        clear_btn.clicked.connect(self._clear_history)
        actions.addWidget(clear_btn)
        actions.addStretch()
        layout.addLayout(actions)
        layout.addStretch()

        scroll.setWidget(inner)
        root = QVBoxLayout(self)
        root.addWidget(scroll)

    def _card(self, title: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(theme.card_style())
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 22, 24, 22)
        lay.setSpacing(10)
        t = QLabel(title)
        t.setStyleSheet("font-weight:700; font-size:14px;")
        lay.addWidget(t)
        return card

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(theme.auth_input_label_style())
        return lbl

    def set_user(self, user: dict | None):
        self._user = user
        if user:
            self._profile_name.setText(user.get("full_name", "User"))
            self._profile_email.setText(user.get("email", ""))
        else:
            self._profile_name.setText("Not signed in")
            self._profile_email.setText("")

    def _save_prefs(self):
        styles = ["dark", "streets", "satellite"]
        self._prefs = {
            "default_location": self._default_loc.text().strip(),
            "temperature_unit": (
                "fahrenheit" if self._temp_unit.currentIndex() == 1 else "celsius"
            ),
            "map_style": styles[self._map_style.currentIndex()],
            "remember_me": self._remember.isChecked(),
            "show_disaster_markers": self._markers.isChecked(),
            "auto_open_reports": self._auto_reports.isChecked(),
            "notifications_enabled": self._prefs.get("notifications_enabled", True),
        }
        save_preferences(self._prefs)
        self.preferences_changed.emit()
        QMessageBox.information(self, "GeoShield", "Preferences saved successfully.")

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
