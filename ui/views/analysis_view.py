"""
Risk analysis workspace — premium layout with interactive map.
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
from preferences import load_preferences, format_temperature
from report_export import export_html_report
from ui.widgets import RiskCard, StatTile, SectionTitle, MetricPill
from ui.map_widget import InteractiveMapWidget
from workers import AnalysisWorker


class AnalysisView(QWidget):
    analysis_completed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._worker = None
        self._last_result = None
        self._setup_ui()
        self.apply_preferences()

    def set_user(self, user: dict):
        self._user = user
        prefs = load_preferences()
        if prefs.get("default_location") and not self._search.text():
            self._search.setText(prefs["default_location"])

    def apply_preferences(self):
        prefs = load_preferences()
        self._map.set_map_style(prefs.get("map_style", "dark"))

    def _setup_ui(self):
        stack = QStackedLayout(self)
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(22)

        head = QHBoxLayout()
        head.addWidget(
            SectionTitle(
                "Risk Analysis",
                "Fuse live meteorology with historical disaster intelligence for any region.",
            ),
            stretch=1,
        )
        self._live_chip = MetricPill("LIVE DATA", theme.SUCCESS)
        head.addWidget(self._live_chip, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(head)

        search_card = QFrame()
        search_card.setStyleSheet(theme.card_style(elevated=True))
        sc = QVBoxLayout(search_card)
        sc.setContentsMargins(20, 18, 20, 18)
        sc.setSpacing(12)

        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("City, region, or coordinates…")
        self._search.setMinimumHeight(42)
        self._search.returnPressed.connect(self._start_analysis)
        search_row.addWidget(self._search, stretch=1)

        self._analyze_btn = QPushButton("Run analysis")
        self._analyze_btn.setFixedWidth(150)
        self._analyze_btn.setMinimumHeight(42)
        self._analyze_btn.clicked.connect(self._start_analysis)
        search_row.addWidget(self._analyze_btn)

        self._export_btn = QPushButton("Export report")
        self._export_btn.setProperty("class", "secondary")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._export_report)
        search_row.addWidget(self._export_btn)
        sc.addLayout(search_row)

        chips = QHBoxLayout()
        chips.setSpacing(8)
        for loc in QUICK_LOCATIONS:
            btn = QPushButton(loc)
            btn.setProperty("class", "chip")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, c=loc: self._search.setText(c))
            chips.addWidget(btn)
        chips.addStretch()
        sc.addLayout(chips)
        layout.addWidget(search_card)

        stats = QGridLayout()
        stats.setSpacing(12)
        self._loc_tile = StatTile("Location")
        self._temp_tile = StatTile("Temperature")
        self._hum_tile = StatTile("Humidity")
        self._wind_tile = StatTile("Wind")
        self._precip_tile = StatTile("Precipitation")
        self._hist_tile = StatTile("Archive events")
        tiles = [
            self._loc_tile,
            self._temp_tile,
            self._hum_tile,
            self._wind_tile,
            self._precip_tile,
            self._hist_tile,
        ]
        for i, t in enumerate(tiles):
            stats.addWidget(t, i // 3, i % 3)
        layout.addLayout(stats)

        cards = QHBoxLayout()
        cards.setSpacing(14)
        self._flood = RiskCard("Flood", "Precipitation & soil saturation", "💧")
        self._fire = RiskCard("Wildfire", "Heat, dryness & wind spread", "🔥")
        self._slide = RiskCard("Landslide", "Slope stress & rainfall load", "⛰")
        for c in (self._flood, self._fire, self._slide):
            cards.addWidget(c)
        layout.addLayout(cards)

        pred_card = QFrame()
        pred_card.setStyleSheet(theme.card_style())
        pcl = QVBoxLayout(pred_card)
        pcl.setContentsMargins(20, 16, 20, 16)
        pt = QLabel("Multi-horizon projections (Science Lab)")
        pt.setStyleSheet("font-weight:700;")
        pcl.addWidget(pt)
        self._pred_row = QHBoxLayout()
        self._pred_24 = StatTile("24h Ψ")
        self._pred_72 = StatTile("72h Ψ")
        self._pred_7d = StatTile("7-day Ψ")
        self._fwi_tile = StatTile("FWI proxy")
        for t in (self._pred_24, self._pred_72, self._pred_7d, self._fwi_tile):
            self._pred_row.addWidget(t)
        pcl.addLayout(self._pred_row)
        self._pred_hint = QLabel("Run analysis to generate forecast-linked hazard projections.")
        self._pred_hint.setStyleSheet(theme.muted_style())
        pcl.addWidget(self._pred_hint)
        layout.addWidget(pred_card)

        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        overall_frame = QFrame()
        overall_frame.setStyleSheet(theme.card_style(elevated=True))
        ol = QVBoxLayout(overall_frame)
        ol.setContentsMargins(24, 22, 24, 22)
        ol.addWidget(QLabel("Composite Risk Index"))
        row = QHBoxLayout()
        self._overall_score = QLabel("—")
        self._overall_score.setStyleSheet(theme.title_style(40))
        row.addWidget(self._overall_score)
        row.addStretch()
        self._overall_badge = QLabel("PENDING")
        self._overall_badge.setStyleSheet(theme.muted_style() + "font-weight:800;")
        row.addWidget(self._overall_badge)
        ol.addLayout(row)
        self._overall_bar = QProgressBar()
        self._overall_bar.setRange(0, 100)
        self._overall_bar.setFixedHeight(12)
        self._overall_bar.setTextVisible(False)
        ol.addWidget(self._overall_bar)
        self._condition_lbl = QLabel("")
        self._condition_lbl.setStyleSheet(theme.muted_style())
        ol.addWidget(self._condition_lbl)
        bottom.addWidget(overall_frame, stretch=1)

        rec_frame = QFrame()
        rec_frame.setStyleSheet(theme.card_style())
        rl = QVBoxLayout(rec_frame)
        rl.setContentsMargins(24, 22, 24, 22)
        rl.addWidget(QLabel("Operational guidance"))
        self._rec_text = QLabel("Run an analysis to receive tailored multi-hazard recommendations.")
        self._rec_text.setStyleSheet(theme.subtitle_style())
        self._rec_text.setWordWrap(True)
        rl.addWidget(self._rec_text)
        bottom.addWidget(rec_frame, stretch=2)
        layout.addLayout(bottom)

        self._map = InteractiveMapWidget()
        layout.addWidget(self._map)

        scroll.setWidget(inner)
        content = QWidget()
        root = QVBoxLayout(content)
        root.addWidget(scroll)
        stack.addWidget(content)

        self._overlay = self._build_overlay()
        stack.addWidget(self._overlay)
        self._overlay.hide()

    def _build_overlay(self) -> QFrame:
        o = QFrame()
        o.setStyleSheet("background-color: rgba(6, 10, 16, 0.92);")
        lay = QVBoxLayout(o)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t = QLabel("Analyzing region")
        t.setStyleSheet(theme.title_style(24))
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)
        s = QLabel(
            "Geocoding · 48h instruments · Tri-hazard model · Projections · Science export"
        )
        s.setStyleSheet(theme.subtitle_style())
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(s)
        bar = QProgressBar()
        bar.setRange(0, 0)
        bar.setFixedWidth(340)
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
        self._live_chip.setText("FETCHING…")
        self._live_chip.setStyleSheet(theme.status_chip_style(theme.WARNING))

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
        prefs = load_preferences()

        self._loc_tile.set_value(weather.get("display_name", result["city"]))
        self._temp_tile.set_value(format_temperature(weather["temperature"]))
        self._hum_tile.set_value(f"{weather['humidity']:.0f}%")
        self._wind_tile.set_value(f"{weather['wind_speed']:.1f} km/h")
        self._precip_tile.set_value(f"{weather.get('precipitation', 0):.1f} mm")
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
            f"color:{color}; font-weight:800; font-size:14px;"
        )
        self._overall_bar.setValue(int(overall))
        self._overall_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background:{color}; border-radius:6px; }}"
        )
        self._condition_lbl.setText(
            f"Conditions: {weather.get('condition', '—')} · {weather.get('timezone', '')}"
        )

        recs = result.get("recommendations", {})
        lines = [f"▸ {text}" for text in recs.values()]
        self._rec_text.setText("\n\n".join(lines))

        science = result.get("science", {})
        preds = science.get("predictions", [])
        pred_map = {
            "24-hour outlook": self._pred_24,
            "72-hour outlook": self._pred_72,
            "7-day outlook": self._pred_7d,
        }
        for p in preds:
            tile = pred_map.get(p["horizon"])
            if tile:
                delta = p.get("delta_from_current", 0)
                tile.set_value(
                    f"{p['projected_overall']:.0f} ({p['projected_level'][:3].upper()}) "
                    f"{delta:+.0f}"
                )
        self._fwi_tile.set_value(f"{weather.get('fire_weather_index_proxy', 0):.0f}")
        if preds:
            self._pred_hint.setText(
                "Open Science Lab for factor decomposition, charts, CSV/JSON exports."
            )

        if weather.get("lat") is not None:
            disasters = result.get("historical", []) if prefs.get(
                "show_disaster_markers", True
            ) else []
            self._map.load_analysis(
                weather["lat"],
                weather["lon"],
                weather.get("display_name", result["city"]),
                disasters=disasters,
                overall_level=level,
            )

        self._live_chip.setText("LIVE DATA")
        self._live_chip.setStyleSheet(theme.status_chip_style(theme.SUCCESS))
        self._export_btn.setEnabled(True)
        self.analysis_completed.emit(result)

    def _on_failed(self, message: str):
        self._live_chip.setText("OFFLINE")
        self._live_chip.setStyleSheet(theme.status_chip_style(theme.DANGER))
        QMessageBox.critical(self, "Analysis failed", message)

    def _export_report(self):
        if not self._last_result or not self._user:
            return
        prefs = load_preferences()
        path = export_html_report(
            self._last_result,
            self._user.get("full_name", "Analyst"),
        )
        QMessageBox.information(
            self,
            "Report exported",
            f"Professional HTML report saved to:\n{path}",
        )
        if prefs.get("auto_open_reports", True):
            folder = os.path.dirname(path)
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", folder], check=False)
            else:
                subprocess.run(["xdg-open", folder], check=False)
