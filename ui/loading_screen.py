"""
Application loading / splash screen.
"""
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar,
)

import theme


class LoadingScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(24)

        brand = QLabel("GEOSHIELD")
        brand.setStyleSheet(
            theme.accent_label_style()
            + "font-size: 13px; letter-spacing: 6px;"
        )
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(brand)

        title = QLabel("Disaster Risk Intelligence")
        title.setStyleSheet(theme.title_style(32))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Initializing systems...")
        subtitle.setStyleSheet(theme.subtitle_style())
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status = subtitle
        layout.addWidget(subtitle)

        layout.addSpacing(32)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedWidth(320)
        self._bar.setTextVisible(False)
        layout.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)

        self._hint = QLabel("Loading database and risk engine")
        self._hint.setStyleSheet(theme.muted_style())
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._hint)

    def start(self):
        self._progress = 0
        self._bar.setValue(0)
        self._timer.start(35)

    def _tick(self):
        self._progress += 2
        self._bar.setValue(self._progress)

        if self._progress == 30:
            self._status.setText("Connecting to weather services...")
        elif self._progress == 60:
            self._status.setText("Preparing risk models...")
        elif self._progress == 85:
            self._status.setText("Almost ready...")

        if self._progress >= 100:
            self._timer.stop()
            QTimer.singleShot(200, self.finished.emit)
