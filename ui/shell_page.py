"""
Main workspace shell — navigation, header, and views.
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
from config import APP_TAGLINE, AUTHOR_CREDIT
from database import Database
from ui.widgets import NavButton, MetricPill, AuthorFooter
from ui.views.analysis_view import AnalysisView
from ui.views.science_view import ScienceView
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView


class ShellPage(QWidget):
    logout_requested = pyqtSignal()

    NAV_ANALYSIS = 0
    NAV_SCIENCE = 1
    NAV_HISTORY = 2
    NAV_SETTINGS = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._nav_buttons: list[NavButton] = []
        self._db = Database()
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

        right = QVBoxLayout()
        right.setSpacing(0)

        content_wrap = QWidget()
        content_layout = QVBoxLayout(content_wrap)
        content_layout.setContentsMargins(32, 28, 32, 20)

        self._stack = QStackedWidget()
        self._analysis = AnalysisView()
        self._science = ScienceView()
        self._history = HistoryView()
        self._settings = SettingsView()
        self._stack.addWidget(self._analysis)
        self._stack.addWidget(self._science)
        self._stack.addWidget(self._history)
        self._stack.addWidget(self._settings)
        content_layout.addWidget(self._stack)
        right.addWidget(content_wrap, stretch=1)

        footer_bar = QFrame()
        footer_bar.setFixedHeight(28)
        footer_bar.setStyleSheet(
            f"background:{theme.BG_SECONDARY}; border-top:1px solid {theme.BORDER};"
        )
        fl = QHBoxLayout(footer_bar)
        fl.setContentsMargins(28, 0, 28, 0)
        fl.addWidget(AuthorFooter())
        fl.addStretch()
        model_lbl = QLabel(AUTHOR_CREDIT)
        model_lbl.setStyleSheet(theme.muted_style() + "font-size:10px;")
        fl.addWidget(model_lbl)
        right.addWidget(footer_bar)

        body.addLayout(right, stretch=1)
        root.addLayout(body)

        self._analysis.analysis_completed.connect(self._on_analysis_done)
        self._settings.history_cleared.connect(self._history.refresh)
        self._settings.preferences_changed.connect(self._analysis.apply_preferences)
        self._select_nav(self.NAV_ANALYSIS)

    def _build_header(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(72)
        bar.setStyleSheet(
            f"background:{theme.BG_SECONDARY}; border-bottom:1px solid {theme.BORDER};"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(28, 0, 28, 0)

        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        brand = QLabel("GEOSHIELD")
        brand.setStyleSheet(theme.accent_label_style())
        brand_col.addWidget(brand)
        sub = QLabel(APP_TAGLINE)
        sub.setStyleSheet(theme.muted_style())
        brand_col.addWidget(sub)
        lay.addLayout(brand_col)
        lay.addSpacing(20)

        self._plan = MetricPill("PRO PLAN ACTIVE", theme.GOLD)
        lay.addWidget(self._plan)
        lay.addStretch()

        self._status = QLabel("Systems operational")
        self._status.setStyleSheet(theme.status_chip_style(theme.SUCCESS))
        lay.addWidget(self._status)
        lay.addSpacing(16)

        self._stats_lbl = QLabel("")
        self._stats_lbl.setStyleSheet(theme.muted_style())
        lay.addWidget(self._stats_lbl)

        self._avatar = QLabel("?")
        self._avatar.setFixedSize(42, 42)
        self._avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._avatar.setStyleSheet(
            f"background:{theme.ACCENT_SOFT}; color:{theme.ACCENT};"
            f"border-radius:21px; font-weight:800; font-size:15px;"
        )
        lay.addWidget(self._avatar)

        user_col = QVBoxLayout()
        user_col.setSpacing(0)
        self._user_label = QLabel("")
        self._user_label.setStyleSheet("font-weight:700; font-size:13px;")
        user_col.addWidget(self._user_label)
        self._role_lbl = QLabel("Risk Scientist")
        self._role_lbl.setStyleSheet(theme.muted_style())
        user_col.addWidget(self._role_lbl)
        lay.addLayout(user_col)

        out = QPushButton("Sign out")
        out.setProperty("class", "secondary")
        out.setCursor(Qt.CursorShape.PointingHandCursor)
        out.clicked.connect(self.logout_requested.emit)
        lay.addWidget(out)
        return bar

    def _build_sidebar(self) -> QFrame:
        side = QFrame()
        side.setFixedWidth(252)
        side.setStyleSheet(
            f"background:{theme.BG_SECONDARY}; border-right:1px solid {theme.BORDER};"
        )
        lay = QVBoxLayout(side)
        lay.setContentsMargins(18, 28, 18, 28)
        lay.setSpacing(6)

        menu_lbl = QLabel("WORKSPACE")
        menu_lbl.setStyleSheet(
            theme.muted_style() + "font-weight:800; letter-spacing:1.2px; font-size:10px;"
        )
        lay.addWidget(menu_lbl)
        lay.addSpacing(10)

        items = [
            (self.NAV_ANALYSIS, "Risk Analysis", "◎"),
            (self.NAV_SCIENCE, "Science Lab", "🔬"),
            (self.NAV_HISTORY, "History & Archives", "◷"),
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
        tl.setContentsMargins(16, 16, 16, 16)
        t = QLabel("Scientific workflow")
        t.setStyleSheet(f"color:{theme.ACCENT}; font-weight:700; font-size:12px;")
        tl.addWidget(t)
        tip_txt = QLabel(
            "Run analysis, then open Science Lab for full instrument data, "
            "model decomposition, 24h–7d projections, and CSV/JSON exports."
        )
        tip_txt.setStyleSheet(theme.muted_style())
        tip_txt.setWordWrap(True)
        tl.addWidget(tip_txt)
        lay.addWidget(tip)

        credit = QLabel(AUTHOR_CREDIT)
        credit.setStyleSheet(theme.muted_style() + "font-size:10px;")
        credit.setWordWrap(True)
        lay.addWidget(credit)
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
        stats = self._db.get_user_stats(user["id"])
        self._stats_lbl.setText(
            f"{stats['total_analyses']} analyses · avg Ψ {stats['avg_risk_score']}"
        )
        self._analysis.set_user(user)
        self._history.set_user(user)
        self._settings.set_user(user)

    def _on_analysis_done(self, result: dict):
        self._status.setText("Analysis complete")
        self._status.setStyleSheet(theme.status_chip_style(theme.SUCCESS))
        self._science.load_result(result)
        if self._user:
            stats = self._db.get_user_stats(self._user["id"])
            self._stats_lbl.setText(
                f"{stats['total_analyses']} analyses · avg Ψ {stats['avg_risk_score']}"
            )
        self._history.refresh(disasters=result.get("historical", []))
