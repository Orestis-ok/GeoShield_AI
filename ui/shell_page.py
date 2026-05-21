"""
Main application shell — navigation, header, and views.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
)

import theme
from config import APP_TAGLINE
from ui.widgets import NavButton
from ui.views.analysis_view import AnalysisView
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView


class ShellPage(QWidget):
    logout_requested = pyqtSignal()

    NAV_ANALYSIS = 0
    NAV_HISTORY = 1
    NAV_SETTINGS = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._nav_buttons: list[NavButton] = []
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        body.addWidget(self._build_sidebar())

        content_wrap = QWidget()
        content_layout = QVBoxLayout(content_wrap)
        content_layout.setContentsMargins(28, 24, 28, 24)

        self._stack = QStackedWidget()
        self._analysis = AnalysisView()
        self._history = HistoryView()
        self._settings = SettingsView()
        self._stack.addWidget(self._analysis)
        self._stack.addWidget(self._history)
        self._stack.addWidget(self._settings)
        content_layout.addWidget(self._stack)

        body.addWidget(content_wrap, stretch=1)
        root.addLayout(body)

        self._analysis.analysis_completed.connect(self._on_analysis_done)
        self._settings.history_cleared.connect(self._history.refresh)

        self._select_nav(self.NAV_ANALYSIS)

    def _build_header(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(68)
        bar.setStyleSheet(
            f"background:{theme.BG_SECONDARY}; border-bottom:1px solid {theme.BORDER};"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(24, 0, 24, 0)

        brand = QLabel("GEOSHIELD")
        brand.setStyleSheet(theme.accent_label_style())
        lay.addWidget(brand)

        sub = QLabel(APP_TAGLINE)
        sub.setStyleSheet(theme.muted_style())
        lay.addWidget(sub)
        lay.addStretch()

        self._status = QLabel("Operational")
        self._status.setStyleSheet(theme.status_chip_style(theme.SUCCESS))
        lay.addWidget(self._status)

        lay.addSpacing(16)

        self._avatar = QLabel("?")
        self._avatar.setFixedSize(40, 40)
        self._avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._avatar.setStyleSheet(
            f"background:{theme.ACCENT_SOFT}; color:{theme.ACCENT};"
            f"border-radius:20px; font-weight:700;"
        )
        lay.addWidget(self._avatar)

        self._user_label = QLabel("")
        self._user_label.setStyleSheet("font-weight:600;")
        lay.addWidget(self._user_label)

        out = QPushButton("Sign out")
        out.setProperty("class", "secondary")
        out.setCursor(Qt.CursorShape.PointingHandCursor)
        out.clicked.connect(self.logout_requested.emit)
        lay.addWidget(out)

        return bar

    def _build_sidebar(self) -> QFrame:
        side = QFrame()
        side.setFixedWidth(240)
        side.setStyleSheet(
            f"background:{theme.BG_SECONDARY}; border-right:1px solid {theme.BORDER};"
        )
        lay = QVBoxLayout(side)
        lay.setContentsMargins(16, 24, 16, 24)
        lay.setSpacing(6)

        menu_lbl = QLabel("WORKSPACE")
        menu_lbl.setStyleSheet(theme.muted_style() + "font-weight:700; letter-spacing:1px;")
        lay.addWidget(menu_lbl)
        lay.addSpacing(8)

        items = [
            (self.NAV_ANALYSIS, "Analysis", "◎"),
            (self.NAV_HISTORY, "History", "◷"),
            (self.NAV_SETTINGS, "Settings", "⚙"),
        ]
        for idx, text, icon in items:
            btn = NavButton(text, icon)
            btn.clicked.connect(lambda _, i=idx: self._select_nav(i))
            self._nav_buttons.append(btn)
            lay.addWidget(btn)

        lay.addStretch()

        tip = QFrame()
        tip.setStyleSheet(theme.card_style())
        tl = QVBoxLayout(tip)
        tl.setContentsMargins(14, 14, 14, 14)
        t = QLabel("Pro tip")
        t.setStyleSheet("font-weight:700; font-size:12px;")
        tl.addWidget(t)
        tip_txt = QLabel("Use quick-location chips for faster regional scans.")
        tip_txt.setStyleSheet(theme.muted_style())
        tip_txt.setWordWrap(True)
        tl.addWidget(tip_txt)
        lay.addWidget(tip)

        return side

    def _select_nav(self, index: int):
        for i, btn in enumerate(self._nav_buttons):
            btn.set_active(i == index)
        self._stack.setCurrentIndex(index)
        if index == self.NAV_HISTORY:
            self._history.refresh()

    def set_user(self, user: dict):
        self._user = user
        name = user.get("full_name", "User")
        self._user_label.setText(name)
        self._avatar.setText(name[0].upper() if name else "?")
        self._analysis.set_user(user)
        self._history.set_user(user)
        self._settings.set_user(user)

    def _on_analysis_done(self, result: dict):
        self._status.setText("Analysis complete")
        self._status.setStyleSheet(theme.status_chip_style(theme.SUCCESS))
        self._history.refresh(disasters=result.get("historical", []))

    def set_status(self, text: str, color: str):
        self._status.setText(text)
        self._status.setStyleSheet(theme.status_chip_style(color))
