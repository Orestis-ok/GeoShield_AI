"""
Premium application splash / loading screen.
"""
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame

import theme
from config import APP_TAGLINE, AUTHOR_CREDIT


class LoadingScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def _setup_ui(self):
        self.setStyleSheet(f"background:{theme.BG_PRIMARY};")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        ring = QFrame()
        ring.setFixedSize(88, 88)
        ring.setStyleSheet(
            f"border: 3px solid {theme.BORDER};"
            f"border-top: 3px solid {theme.ACCENT};"
            f"border-radius: 44px;"
            f"background: transparent;"
        )
        layout.addWidget(ring, alignment=Qt.AlignmentFlag.AlignCenter)

        brand = QLabel("GEOSHIELD")
        brand.setStyleSheet(theme.accent_label_style() + "font-size:14px; letter-spacing:8px;")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(brand)

        title = QLabel("Professional Risk Intelligence")
        title.setStyleSheet(theme.title_style(26))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(APP_TAGLINE)
        subtitle.setStyleSheet(theme.subtitle_style())
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status = subtitle
        layout.addWidget(subtitle)

        layout.addSpacing(28)
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setFixedWidth(360)
        self._bar.setTextVisible(False)
        layout.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)

        self._hint = QLabel("Initializing secure workspace")
        self._hint.setStyleSheet(theme.muted_style())
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._hint)

        credit = QLabel(AUTHOR_CREDIT)
        credit.setStyleSheet(theme.accent_label_style())
        credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credit)

    def start(self):
        self._progress = 0
        self._bar.setValue(0)
        self._timer.start(32)

    def _tick(self):
        self._progress += 2
        self._bar.setValue(self._progress)
        if self._progress == 28:
            self._status.setText("Loading risk models & disaster archives…")
        elif self._progress == 55:
            self._status.setText("Connecting to Open-Meteo services…")
        elif self._progress == 82:
            self._status.setText("Preparing interactive map engine…")
        if self._progress >= 100:
            self._timer.stop()
            QTimer.singleShot(180, self.finished.emit)
