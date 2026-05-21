"""
Reusable UI components.
"""
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
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


class RiskCard(QFrame):
    def __init__(self, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(theme.card_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel(title)
        t.setStyleSheet("font-weight: 700; font-size: 15px;")
        header.addWidget(t)
        header.addStretch()
        self._badge = QLabel("—")
        self._badge.setStyleSheet(
            f"background:{theme.BG_INPUT}; color:{theme.TEXT_MUTED};"
            f"padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700;"
        )
        header.addWidget(self._badge)
        layout.addLayout(header)

        sub = QLabel(subtitle)
        sub.setStyleSheet(theme.muted_style())
        layout.addWidget(sub)

        self._score = QLabel("—")
        self._score.setStyleSheet(theme.title_style(26))
        layout.addWidget(self._score)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(10)
        layout.addWidget(self._bar)

    def set_risk(self, score: float, level: str):
        color = theme.risk_color(level)
        self._score.setText(f"{score:.0f}")
        self._badge.setText(level.upper())
        self._badge.setStyleSheet(
            f"background:{theme.BG_INPUT}; color:{color};"
            f"padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700;"
        )
        self._bar.setValue(int(score))
        self._bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}"
        )


class StatTile(QFrame):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            theme.card_style()
            + "padding: 4px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        lbl = QLabel(label)
        lbl.setStyleSheet(theme.muted_style() + "font-weight: 600;")
        layout.addWidget(lbl)
        self._value = QLabel("—")
        self._value.setStyleSheet("font-weight: 700; font-size: 15px;")
        layout.addWidget(self._value)

    def set_value(self, text: str):
        self._value.setText(text)


class NavButton(QPushButton):
    def __init__(self, text: str, icon: str = "", parent=None):
        label = f"  {icon}  {text}" if icon else text
        super().__init__(label, parent)
        self.setProperty("class", "nav")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._active = False

    def set_active(self, active: bool):
        self._active = active
        self.setProperty("class", "nav-active" if active else "nav")
        self.style().unpolish(self)
        self.style().polish(self)


class MapWidget(QLabel):
    """Loads a static OpenStreetMap preview for coordinates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(240)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            theme.card_style()
            + f"background-color: {theme.BG_INPUT}; color: {theme.TEXT_MUTED};"
        )
        self.setText("Map preview will appear after analysis")
        self._nam = QNetworkAccessManager(self)
        self._nam.finished.connect(self._on_loaded)
        self._reply = None

    def load_coordinates(self, lat: float, lon: float):
        self.setText("Loading map…")
        zoom = 9
        url = (
            "https://staticmap.openstreetmap.de/staticmap.php"
            f"?center={lat},{lon}&zoom={zoom}&size=640x360"
            f"&markers={lat},{lon},lightblue1"
        )
        if self._reply:
            self._reply.abort()
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"User-Agent", b"GeoShield/1.0")
        self._reply = self._nam.get(request)

    def _on_loaded(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            pix = QPixmap()
            if pix.loadFromData(data):
                scaled = pix.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.setPixmap(scaled)
                self.setText("")
            else:
                self._show_fallback(reply)
        else:
            self._show_fallback(reply)
        reply.deleteLater()

    def _show_fallback(self, reply):
        self.setPixmap(QPixmap())
        self.setText("Map unavailable — coordinates saved for this region")

    def clear_map(self):
        self.setPixmap(QPixmap())
        self.setText("Run an analysis to view the region map")


class SectionTitle(QWidget):
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet(theme.title_style(20))
        layout.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet(theme.subtitle_style())
            layout.addWidget(s)
