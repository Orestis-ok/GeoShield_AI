"""
Reusable premium UI components.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QWidget,
)

import theme
from config import AUTHOR_CREDIT


class RiskCard(QFrame):
    def __init__(self, title: str, subtitle: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet(theme.card_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)

        header = QHBoxLayout()
        if icon:
            ic = QLabel(icon)
            ic.setStyleSheet(f"font-size:18px; color:{theme.ACCENT};")
            header.addWidget(ic)
        t = QLabel(title)
        t.setStyleSheet("font-weight: 700; font-size: 15px;")
        header.addWidget(t)
        header.addStretch()
        self._badge = QLabel("—")
        self._badge.setStyleSheet(
            f"background:{theme.BG_INPUT}; color:{theme.TEXT_MUTED};"
            f"padding:5px 11px; border-radius:14px; font-size:10px; font-weight:800;"
        )
        header.addWidget(self._badge)
        layout.addLayout(header)

        sub = QLabel(subtitle)
        sub.setStyleSheet(theme.muted_style())
        layout.addWidget(sub)

        self._score = QLabel("—")
        self._score.setStyleSheet(theme.title_style(28))
        layout.addWidget(self._score)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(8)
        layout.addWidget(self._bar)

    def set_risk(self, score: float, level: str):
        color = theme.risk_color(level)
        self._score.setText(f"{score:.0f}")
        self._badge.setText(level.upper())
        self._badge.setStyleSheet(
            f"background:{color}22; color:{color};"
            f"padding:5px 11px; border-radius:14px; font-size:10px; font-weight:800;"
        )
        self._bar.setValue(int(score))
        self._bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}"
        )


class StatTile(QFrame):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(theme.card_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(
            theme.muted_style() + "font-weight:700; letter-spacing:0.5px; font-size:10px;"
        )
        layout.addWidget(lbl)
        self._value = QLabel("—")
        self._value.setStyleSheet("font-weight: 700; font-size: 16px;")
        layout.addWidget(self._value)

    def set_value(self, text: str):
        self._value.setText(text)


class NavButton(QPushButton):
    def __init__(self, text: str, icon: str = "", parent=None):
        label = f"  {icon}  {text}" if icon else text
        super().__init__(label, parent)
        self.setProperty("class", "nav")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_active(self, active: bool):
        self.setProperty("class", "nav-active" if active else "nav")
        self.style().unpolish(self)
        self.style().polish(self)


class SectionTitle(QWidget):
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet(theme.title_style(22))
        layout.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet(theme.subtitle_style())
            s.setWordWrap(True)
            layout.addWidget(s)


class MetricPill(QLabel):
    def __init__(self, text: str, color: str = None, parent=None):
        super().__init__(text, parent)
        c = color or theme.ACCENT
        self.setStyleSheet(theme.status_chip_style(c))


class FeatureRow(QWidget):
    def __init__(self, icon: str, title: str, detail: str, parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 6, 0, 6)
        ic = QLabel(icon)
        ic.setFixedWidth(28)
        ic.setStyleSheet(f"color:{theme.ACCENT}; font-size:16px;")
        row.addWidget(ic)
        col = QVBoxLayout()
        col.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet("font-weight:600; font-size:13px;")
        col.addWidget(t)
        d = QLabel(detail)
        d.setStyleSheet(theme.muted_style())
        d.setWordWrap(True)
        col.addWidget(d)
        row.addLayout(col, stretch=1)


class AuthorFooter(QLabel):
    """Persistent creator attribution."""

    def __init__(self, parent=None):
        super().__init__(AUTHOR_CREDIT, parent)
        self.setStyleSheet(
            theme.muted_style() + f" color: {theme.TEXT_MUTED}; font-size: 11px;"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
