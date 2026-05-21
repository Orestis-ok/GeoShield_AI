"""
Risk analysis workspace.
"""
import os
import subprocess
import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QProgressBar,
    QGridLayout,
    QScrollArea,
    QMessageBox,
    QStackedLayout,
)

import theme
from config import QUICK_LOCATIONS
from report_export import export_html_report
from ui.widgets import RiskCard, StatTile, MapWidget, SectionTitle
from workers import AnalysisWorker


class AnalysisView(QWidget):
    analysis_completed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._worker = None
        self._last_result = None
        self._setup_ui()

    def set_user(self, user: dict):
        self._user = user

    def _setup_ui(self):
        stack = QStackedLayout(self)
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        content = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(20)

        layout.addWidget(
            SectionTitle(
                "Risk Analysis",
                "Real-time weather intelligence combined with historical disaster data.",
            )
        )

        # Search bar
        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search city or region…")
        self._search.returnPressed.connect(self._start_analysis)
        search_row.addWidget(self._search, stretch=1)

        self._analyze_btn = QPushButton("Analyze")
        self._analyze_btn.setFixedWidth(140)
        self._analyze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._analyze_btn.clicked.connect(self._start_analysis)
        search_row.addWidget(self._analyze_btn)

        self._export_btn = QPushButton("Export Report")
        self._export_btn.setProperty("class", "secondary")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._export_report)
        search_row.addWidget(self._export_btn)

        layout.addLayout(search_row)

        chips = QHBoxLayout()
        chips.setSpacing(8)
        for loc in QUICK_LOCATIONS:
            btn = QPushButton(loc)
            btn.setProperty("class", "chip")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, c=loc: self._search.setText(c))
            chips.addWidget(btn)
        chips.addStretch()
        layout.addLayout(chips)

        # Stats row
        stats = QHBoxLayout()
        stats.setSpacing(12)
        self._loc_tile = StatTile("Location")
        self._temp_tile = StatTile("Temperature")
        self._hum_tile = StatTile("Humidity")
        self._wind_tile = StatTile("Wind")
        self._hist_tile = StatTile("Historical events")
        for t in (
            self._loc_tile,
            self._temp_tile,
            self._hum_tile,
            self._wind_tile,
            self._hist_tile,
        ):
            stats.addWidget(t)
        layout.addLayout(stats)

        # Risk cards
        cards = QHBoxLayout()
        cards.setSpacing(14)
        self._flood = RiskCard("Flood", "Precipitation & saturation")
        self._fire = RiskCard("Wildfire", "Heat, dryness & wind")
        self._slide = RiskCard("Landslide", "Slope & rainfall stress")
        cards.addWidget(self._flood)
        cards.addWidget(self._fire)
        cards.addWidget(self._slide)
        layout.addLayout(cards)

        # Overall + recommendations
        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        overall_frame = QFrame()
        overall_frame.setStyleSheet(theme.card_style(elevated=True))
        ol = QVBoxLayout(overall_frame)
        ol.setContentsMargins(24, 22, 24, 22)
        ol.addWidget(QLabel("Composite Risk Index"))
        row = QHBoxLayout()
        self._overall_score = QLabel("—")
        self._overall_score.setStyleSheet(theme.title_style(36))
        row.addWidget(self._overall_score)
        row.addStretch()
        self._overall_badge = QLabel("PENDING")
        self._overall_badge.setStyleSheet(theme.muted_style() + "font-weight:700;")
        row.addWidget(self._overall_badge)
        ol.addLayout(row)
        self._overall_bar = QProgressBar()
        self._overall_bar.setRange(0, 100)
        self._overall_bar.setFixedHeight(14)
        self._overall_bar.setTextVisible(False)
        ol.addWidget(self._overall_bar)
        bottom.addWidget(overall_frame, stretch=1)

        rec_frame = QFrame()
        rec_frame.setStyleSheet(theme.card_style())
        rl = QVBoxLayout(rec_frame)
        rl.setContentsMargins(24, 22, 24, 22)
        rl.addWidget(QLabel("Operational Guidance"))
        self._rec_text = QLabel("Run an analysis to receive tailored recommendations.")
        self._rec_text.setStyleSheet(theme.subtitle_style())
        self._rec_text.setWordWrap(True)
        rl.addWidget(self._rec_text)
        bottom.addWidget(rec_frame, stretch=2)

        layout.addLayout(bottom)

        self._map = MapWidget()
        layout.addWidget(self._map)

        scroll.setWidget(inner)
        root = QVBoxLayout(content)
        root.addWidget(scroll)
        stack.addWidget(content)

        self._overlay = self._build_overlay()
        stack.addWidget(self._overlay)
        self._overlay.hide()

    def _build_overlay(self) -> QFrame:
        o = QFrame()
        o.setStyleSheet(f"background-color: rgba(8, 12, 16, 0.88);")
        lay = QVBoxLayout(o)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t = QLabel("Analyzing region")
        t.setStyleSheet(theme.title_style(22))
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)
        s = QLabel("Fetching live weather · Computing risk models · Querying archives")
        s.setStyleSheet(theme.subtitle_style())
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(s)
        bar = QProgressBar()
        bar.setRange(0, 0)
        bar.setFixedWidth(300)
        lay.addWidget(bar, alignment=Qt.AlignmentFlag.AlignCenter)
        return o

    def _start_analysis(self):
        if self._worker and self._worker.isRunning():
            return
        city = self._search.text().strip()
        if not city:
            QMessageBox.warning(self, "GeoShield", "Enter a city or region to analyze.")
            return

        self._overlay.show()
        self._overlay.raise_()
        self._analyze_btn.setEnabled(False)
        self._export_btn.setEnabled(False)

        uid = self._user["id"] if self._user else None
        self._worker = AnalysisWorker(city, uid)
        self._worker.finished.connect(self._on_success)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._cleanup_worker)
        self._worker.failed.connect(self._cleanup_worker)
        self._worker.start()

    def _cleanup_worker(self):
        self._overlay.hide()
        self._analyze_btn.setEnabled(True)

    def _on_success(self, result: dict):
        self._last_result = result
        weather = result["weather"]
        risks = result["risks"]
        city = result["city"]

        self._loc_tile.set_value(weather.get("display_name", city))
        self._temp_tile.set_value(f"{weather['temperature']:.1f} °C")
        self._hum_tile.set_value(f"{weather['humidity']:.0f}%")
        self._wind_tile.set_value(f"{weather['wind_speed']:.1f} km/h")
        self._hist_tile.set_value(str(result["historical_count"]))

        self._flood.set_risk(risks["flood"]["score"], risks["flood"]["level"])
        self._fire.set_risk(risks["fire"]["score"], risks["fire"]["level"])
        self._slide.set_risk(risks["landslide"]["score"], risks["landslide"]["level"])

        overall = risks["overall"]
        level = risks.get("overall_level", "low")
        color = theme.risk_color(level)
        self._overall_score.setText(f"{overall:.0f}")
        self._overall_badge.setText(level.upper())
        self._overall_badge.setStyleSheet(
            f"color:{color}; font-weight:700; font-size:13px;"
        )
        self._overall_bar.setValue(int(overall))
        self._overall_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background:{color}; border-radius:6px; }}"
        )

        recs = result.get("recommendations", {})
        lines = [f"• {text}" for text in recs.values()]
        self._rec_text.setText("\n".join(lines))

        if weather.get("lat") is not None and weather.get("lon") is not None:
            self._map.load_coordinates(weather["lat"], weather["lon"])

        self._export_btn.setEnabled(True)
        self.analysis_completed.emit(result)

    def _on_failed(self, message: str):
        QMessageBox.critical(self, "Analysis failed", message)

    def _export_report(self):
        if not self._last_result or not self._user:
            return
        path = export_html_report(
            self._last_result,
            self._user.get("full_name", "Analyst"),
        )
        QMessageBox.information(
            self,
            "Report exported",
            f"HTML report saved to:\n{path}",
        )
        if sys.platform == "win32":
            os.startfile(os.path.dirname(path))
        elif sys.platform == "darwin":
            subprocess.run(["open", os.path.dirname(path)], check=False)
        else:
            subprocess.run(["xdg-open", os.path.dirname(path)], check=False)
