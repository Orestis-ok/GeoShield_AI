"""
Science Lab — comprehensive meteorological data, model decomposition, and projections.
"""
import os
import subprocess
import sys

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
    QTextEdit,
    QMessageBox,
    QGridLayout,
)

import theme
from config import AUTHOR_CREDIT, MODEL_VERSION, SCIENCE_EXPORT_DIR
from data_export import export_science_json, export_hourly_csv, export_daily_csv
from ui.widgets import SectionTitle, MetricPill
from ui.science_charts import hourly_chart_html, forecast_chart_html

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_CHARTS = True
except ImportError:
    HAS_CHARTS = False
    QWebEngineView = None


class ScienceView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._result = None
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        head = QHBoxLayout()
        head.addWidget(
            SectionTitle(
                "Science Lab",
                "Full meteorological instrument panel, model decomposition, multi-horizon "
                "projections, and research-grade exports for scientists and forecasters.",
            ),
            stretch=1,
        )
        self._model_chip = MetricPill(MODEL_VERSION, theme.ACCENT)
        head.addWidget(self._model_chip, alignment=Qt.AlignmentFlag.AlignTop)
        root.addLayout(head)

        self._empty = QFrame()
        self._empty.setStyleSheet(theme.card_style(elevated=True))
        el = QVBoxLayout(self._empty)
        el.setContentsMargins(40, 48, 40, 48)
        msg = QLabel(
            "No analysis loaded.\n\nRun a regional analysis from the Risk Analysis tab. "
            "Comprehensive datasets, projections, and exports will populate here automatically."
        )
        msg.setStyleSheet(theme.subtitle_style())
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        el.addWidget(msg)
        root.addWidget(self._empty)

        self._content = QWidget()
        cl = QVBoxLayout(self._content)
        cl.setSpacing(12)

        export_row = QHBoxLayout()
        for label, slot in [
            ("Export full JSON", self._export_json),
            ("Export hourly CSV", self._export_hourly),
            ("Export 7-day CSV", self._export_daily),
        ]:
            btn = QPushButton(label)
            btn.setProperty("class", "secondary")
            btn.clicked.connect(slot)
            export_row.addWidget(btn)
        export_row.addStretch()
        cl.addLayout(export_row)

        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            f"QTabWidget::pane {{ border: 1px solid {theme.BORDER}; border-radius: 10px; }}"
            f"QTabBar::tab {{ background: {theme.BG_SECONDARY}; color: {theme.TEXT_MUTED}; "
            f"padding: 10px 18px; margin-right: 4px; border-top-left-radius: 8px; "
            f"border-top-right-radius: 8px; }}"
            f"QTabBar::tab:selected {{ background: {theme.BG_CARD}; color: {theme.ACCENT}; font-weight: 700; }}"
        )

        self._tabs.addTab(self._build_instruments_tab(), "Instruments")
        self._tabs.addTab(self._build_model_tab(), "Model")
        self._tabs.addTab(self._build_predictions_tab(), "Predictions")
        self._tabs.addTab(self._build_timeseries_tab(), "Time series")
        self._tabs.addTab(self._build_forecast_tab(), "7-day forecast")
        self._tabs.addTab(self._build_diagnostics_tab(), "Diagnostics")
        self._tabs.addTab(self._build_methodology_tab(), "Methodology")

        cl.addWidget(self._tabs)
        self._content.hide()
        root.addWidget(self._content)

    def _scroll_wrap(self, widget: QWidget) -> QScrollArea:
        s = QScrollArea()
        s.setWidgetResizable(True)
        s.setFrameShape(QFrame.Shape.NoFrame)
        s.setWidget(widget)
        return s

    def _build_instruments_tab(self) -> QWidget:
        w = QWidget()
        self._inst_grid = QGridLayout(w)
        self._inst_grid.setSpacing(10)
        return self._scroll_wrap(w)

    def _build_model_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        self._model_formula = QLabel("")
        self._model_formula.setStyleSheet(
            f"font-family: {theme.FONT_MONO}; color: {theme.ACCENT}; padding: 12px;"
            f"background: {theme.BG_INPUT}; border-radius: 8px;"
        )
        self._model_formula.setWordWrap(True)
        lay.addWidget(self._model_formula)
        self._factor_table = self._table(["Factor", "Value", "Unit", "Contribution"])
        lay.addWidget(self._factor_table)
        self._derived_table = self._table(["Derived index", "Value", "Unit"])
        lay.addWidget(self._derived_table)
        return self._scroll_wrap(w)

    def _build_predictions_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        self._pred_table = self._table([
            "Horizon", "Ψ projected", "Level", "Δ vs now", "Confidence",
            "Flood", "Fire", "Landslide", "Drivers",
        ])
        lay.addWidget(self._pred_table)
        return self._scroll_wrap(w)

    def _build_timeseries_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        if HAS_CHARTS:
            self._hourly_chart = QWebEngineView()
            self._hourly_chart.setMinimumHeight(220)
            lay.addWidget(self._hourly_chart)
        self._hourly_table = self._table([
            "Time", "Temp °C", "RH %", "Precip mm", "Wind", "Gust", "Pressure", "Cloud %",
        ])
        lay.addWidget(self._hourly_table)
        return self._scroll_wrap(w)

    def _build_forecast_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        if HAS_CHARTS:
            self._forecast_chart = QWebEngineView()
            self._forecast_chart.setMinimumHeight(200)
            lay.addWidget(self._forecast_chart)
        self._daily_table = self._table([
            "Date", "T max", "T min", "Precip sum", "Wind max", "RH max", "Condition",
        ])
        lay.addWidget(self._daily_table)
        return self._scroll_wrap(w)

    def _build_diagnostics_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        self._diag_labels: list[QLabel] = []
        card = QFrame()
        card.setStyleSheet(theme.card_style())
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 18, 20, 18)
        self._diag_card_layout = cl
        lay.addWidget(card)
        self._corr_table = self._table(["Variable pair", "Pearson r", "Interpretation"])
        lay.addWidget(self._corr_table)
        return self._scroll_wrap(w)

    def _build_methodology_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        self._method_text = QTextEdit()
        self._method_text.setReadOnly(True)
        self._method_text.setStyleSheet(
            f"background: {theme.BG_INPUT}; color: {theme.TEXT_SECONDARY}; "
            f"font-family: {theme.FONT_MONO}; font-size: 12px; border: 1px solid {theme.BORDER};"
        )
        lay.addWidget(self._method_text)
        credit = QLabel(AUTHOR_CREDIT)
        credit.setStyleSheet(theme.accent_label_style())
        credit.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.addWidget(credit)
        return w

    def _table(self, headers: list[str]) -> QTableWidget:
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t.verticalHeader().setVisible(False)
        t.setAlternatingRowColors(True)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setMinimumHeight(160)
        return t

    def load_result(self, result: dict | None):
        self._result = result
        if not result:
            self._content.hide()
            self._empty.show()
            return
        self._empty.hide()
        self._content.show()
        self._populate(result)

    def _populate(self, result: dict):
        w = result["weather"]
        sci = result.get("science", {})
        risks = result["risks"]

        instruments = [
            ("Location", w.get("display_name", result["city"]), ""),
            ("Coordinates", f"{w.get('lat', 0):.4f}°, {w.get('lon', 0):.4f}°", ""),
            ("Elevation", f"{w.get('elevation_m', 'N/A')}", "m"),
            ("Timezone", w.get("timezone", ""), ""),
            ("Fetched (UTC)", w.get("fetched_at", ""), ""),
            ("Temperature", f"{w['temperature']:.2f}", "°C"),
            ("Dew point", f"{w.get('dewpoint_c', 0):.2f}", "°C"),
            ("Heat index", f"{w.get('heat_index_c', 0):.2f}", "°C"),
            ("Relative humidity", f"{w['humidity']:.1f}", "%"),
            ("Vapor pressure deficit", f"{w.get('vapor_pressure_deficit_kpa', 0):.3f}", "kPa"),
            ("Wind speed", f"{w['wind_speed']:.1f}", "km/h"),
            ("Wind gust", f"{w.get('wind_gust', 0):.1f}", "km/h"),
            ("Precipitation (24h)", f"{w.get('precipitation', 0):.2f}", "mm"),
            ("Mean hourly precip", f"{w.get('precipitation_mean_hourly', 0):.3f}", "mm/h"),
            ("Surface pressure", f"{w.get('surface_pressure_hpa', 0):.1f}", "hPa"),
            ("Cloud cover", f"{w.get('cloud_cover_pct', 0):.1f}", "%"),
            ("WMO weather code", str(w.get("weathercode", "")), ""),
            ("Condition", w.get("condition", ""), ""),
            ("FWI proxy", f"{w.get('fire_weather_index_proxy', 0):.1f}", "index"),
            ("Composite Ψ", f"{risks['overall']:.1f}", f"/100 ({risks.get('overall_level', '')})"),
        ]
        while self._inst_grid.count():
            item = self._inst_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for i, (name, val, unit) in enumerate(instruments):
            tile = QFrame()
            tile.setStyleSheet(theme.card_style())
            tl = QVBoxLayout(tile)
            tl.setContentsMargins(14, 12, 14, 12)
            n = QLabel(name.upper())
            n.setStyleSheet(theme.muted_style() + "font-weight:700;font-size:10px;")
            v = QLabel(f"{val} {unit}".strip())
            v.setStyleSheet("font-weight:700;font-size:14px;")
            tl.addWidget(n)
            tl.addWidget(v)
            self._inst_grid.addWidget(tile, i // 3, i % 3)

        bd = sci.get("breakdown", {})
        comp = bd.get("composite", {})
        self._model_formula.setText(comp.get("formula", ""))

        factors = []
        for hazard in ("flood", "fire", "landslide"):
            block = bd.get(hazard, {})
            for fname, val, unit, contrib in block.get("factors", []):
                factors.append((f"{hazard.title()}: {fname}", f"{val}", unit, f"{contrib:.0f}"))
        self._fill_table(self._factor_table, factors)

        derived = [
            (n, f"{v}" if v is not None else "—", u)
            for n, v, u in bd.get("derived_indices", [])
        ]
        self._fill_table(self._derived_table, derived)

        preds = sci.get("predictions", [])
        pred_rows = []
        for p in preds:
            pred_rows.append((
                p["horizon"],
                f"{p['projected_overall']:.1f}",
                p["projected_level"].upper(),
                f"{p['delta_from_current']:+.1f}",
                f"{p.get('confidence_pct', 0):.0f}%",
                f"{p.get('flood', 0):.0f}",
                f"{p.get('fire', 0):.0f}",
                f"{p.get('landslide', 0):.0f}",
                "; ".join(p.get("drivers", [])),
            ))
        self._fill_table(self._pred_table, pred_rows)

        hourly = w.get("hourly", [])
        if HAS_CHARTS and hourly:
            self._hourly_chart.setHtml(
                hourly_chart_html(hourly), QUrl("https://geoshield.local/chart")
            )
        hrows = [
            (
                h.get("time", "")[-16:],
                f"{h.get('temperature', 0):.1f}" if h.get("temperature") is not None else "—",
                f"{h.get('humidity', 0):.0f}" if h.get("humidity") is not None else "—",
                f"{h.get('precipitation', 0):.2f}",
                f"{h.get('wind', 0):.1f}" if h.get("wind") is not None else "—",
                f"{h.get('wind_gust', 0):.1f}" if h.get("wind_gust") is not None else "—",
                f"{h.get('pressure', 0):.0f}" if h.get("pressure") is not None else "—",
                f"{h.get('cloud', 0):.0f}" if h.get("cloud") is not None else "—",
            )
            for h in hourly[:48]
        ]
        self._fill_table(self._hourly_table, hrows)

        daily = w.get("daily", [])
        if HAS_CHARTS and daily:
            self._forecast_chart.setHtml(
                forecast_chart_html(daily), QUrl("https://geoshield.local/forecast")
            )
        drows = [
            (
                d.get("date", ""),
                f"{d.get('temp_max', 0):.1f}",
                f"{d.get('temp_min', 0):.1f}",
                f"{d.get('precip_sum', 0):.1f}",
                f"{d.get('wind_max', 0):.1f}",
                f"{d.get('humidity_max', 0):.0f}",
                d.get("condition", ""),
            )
            for d in daily
        ]
        self._fill_table(self._daily_table, drows)

        diag = sci.get("diagnostics", {})
        while self._diag_card_layout.count():
            item = self._diag_card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        unc = diag.get("uncertainty_band", {})
        lines = [
            f"Archive events in region: {diag.get('archive_events', 0)}",
            f"Archive baseline Ψ: {diag.get('archive_baseline_score', 0)}",
            f"Composite anomaly: {diag.get('composite_anomaly', 0):+.1f} — {diag.get('anomaly_interpretation', '')}",
            f"Uncertainty band: {unc.get('overall_low', 0):.0f} – {unc.get('overall_high', 0):.0f} ({unc.get('note', '')})",
            f"Temperature σ (24h): {diag.get('volatility', {}).get('temperature_std_c', 0)} °C",
            f"48h precipitation total: {diag.get('volatility', {}).get('precip_48h_mm', 0)} mm",
        ]
        for line in lines:
            lb = QLabel(line)
            lb.setStyleSheet(theme.subtitle_style())
            lb.setWordWrap(True)
            self._diag_card_layout.addWidget(lb)

        corrs = sci.get("correlations", [])
        crows = []
        for c in corrs:
            r = c["r"]
            interp = "Strong" if abs(r) > 0.6 else "Moderate" if abs(r) > 0.35 else "Weak"
            sign = "positive" if r > 0 else "negative"
            crows.append((c["pair"], f"{r:+.3f}", f"{interp} {sign} coupling"))
        self._fill_table(self._corr_table, crows)

        self._method_text.setPlainText(sci.get("methodology", ""))

    def _fill_table(self, table: QTableWidget, rows: list[tuple]):
        table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(val)))

    def _export_json(self):
        if not self._result:
            return
        path = export_science_json(self._result)
        self._notify_export(path)

    def _export_hourly(self):
        if not self._result:
            return
        path = export_hourly_csv(self._result)
        self._notify_export(path)

    def _export_daily(self):
        if not self._result:
            return
        path = export_daily_csv(self._result)
        self._notify_export(path)

    def _notify_export(self, path: str):
        QMessageBox.information(self, "Export complete", f"Saved to:\n{path}")
        folder = os.path.dirname(path) or SCIENCE_EXPORT_DIR
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder], check=False)
        else:
            subprocess.run(["xdg-open", folder], check=False)
