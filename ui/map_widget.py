"""
Interactive geographic map — Leaflet via Qt WebEngine (static fallback).
"""
import json

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

import theme

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings

    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    QWebEngineView = None

from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl as NetUrl


def _leaflet_html(lat: float, lon: float, zoom: int, style: str, markers: list) -> str:
    tile_urls = {
        "dark": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        "streets": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    }
    tile = tile_urls.get(style, tile_urls["dark"])
    markers_js = json.dumps(markers)
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body, #map {{ margin:0; padding:0; height:100%; width:100%; background:#060a10; }}
  .leaflet-control-attribution {{ font-size:9px; opacity:0.6; }}
</style>
</head><body>
<div id="map"></div>
<script>
  const map = L.map('map', {{ zoomControl: true }}).setView([{lat}, {lon}], {zoom});
  L.tileLayer('{tile}', {{
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }}).addTo(map);
  const markers = {markers_js};
  const bounds = [];
  markers.forEach(m => {{
    const icon = L.divIcon({{
      className: '',
      html: '<div style="background:' + (m.color || '#3b9eff') + ';width:14px;height:14px;border-radius:50%;border:2px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.4)"></div>',
      iconSize: [14, 14], iconAnchor: [7, 7]
    }});
    const mk = L.marker([m.lat, m.lon], {{ icon }}).addTo(map);
    if (m.label) mk.bindPopup('<b>' + m.label + '</b>' + (m.detail ? '<br/>' + m.detail : ''));
    bounds.push([m.lat, m.lon]);
  }});
  if (bounds.length > 1) map.fitBounds(bounds, {{ padding: [40, 40] }});
</script>
</body></html>"""


class InteractiveMapWidget(QFrame):
    """Pan/zoom Leaflet map when WebEngine is available."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lat = None
        self._lon = None
        self._map_style = "dark"
        self._markers: list[dict] = []
        self.setMinimumHeight(320)
        self.setStyleSheet(theme.card_style() + "padding: 0;")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(
            f"background:{theme.BG_SECONDARY}; border-bottom:1px solid {theme.BORDER};"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 10, 16, 10)
        title = QLabel("Interactive Coverage Map")
        title.setStyleSheet("font-weight:700; font-size:13px;")
        hl.addWidget(title)
        hl.addStretch()
        self._coords_lbl = QLabel("Awaiting analysis")
        self._coords_lbl.setStyleSheet(theme.muted_style())
        hl.addWidget(self._coords_lbl)
        layout.addWidget(header)

        if HAS_WEBENGINE:
            self._view = QWebEngineView()
            settings = self._view.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            self._view.setStyleSheet(f"background:{theme.BG_INPUT};")
            self._show_placeholder()
            layout.addWidget(self._view, stretch=1)
        else:
            self._fallback = QLabel("Install PyQt6-WebEngine for interactive maps")
            self._fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._fallback.setMinimumHeight(280)
            self._fallback.setStyleSheet(
                f"background:{theme.BG_INPUT}; color:{theme.TEXT_MUTED};"
            )
            self._nam = QNetworkAccessManager(self)
            self._nam.finished.connect(self._on_static_loaded)
            layout.addWidget(self._fallback, stretch=1)

    def _show_placeholder(self):
        html = _leaflet_html(20, 0, 2, self._map_style, [])
        self._view.setHtml(html, QUrl("https://geoshield.local/"))

    def set_map_style(self, style: str):
        self._map_style = style
        if self._lat is not None:
            self._render()

    def load_analysis(
        self,
        lat: float,
        lon: float,
        label: str = "",
        disasters: list[dict] | None = None,
        overall_level: str = "low",
    ):
        self._lat = lat
        self._lon = lon
        self._coords_lbl.setText(f"{lat:.4f}°, {lon:.4f}° · {label or 'Region'}")
        color = theme.risk_color(overall_level)
        self._markers = [
            {
                "lat": lat,
                "lon": lon,
                "label": label or "Analysis point",
                "detail": f"Composite risk: {overall_level.upper()}",
                "color": color,
            }
        ]
        for i, d in enumerate(disasters or []):
            offset = 0.012 * (i + 1)
            self._markers.append({
                "lat": lat + offset,
                "lon": lon + offset * 0.7,
                "label": f"{d.get('event_type', 'event').title()} · {d.get('year', '')}",
                "detail": d.get("description", d.get("severity", "")),
                "color": theme.risk_color(
                    "critical" if d.get("severity") == "critical" else "high"
                ),
            })
        self._render()

    def _render(self):
        if not HAS_WEBENGINE or self._lat is None:
            if not HAS_WEBENGINE and self._lat is not None:
                self._load_static(self._lat, self._lon)
            return
        html = _leaflet_html(
            self._lat, self._lon, 10, self._map_style, self._markers[:12]
        )
        self._view.setHtml(html, QUrl("https://geoshield.local/"))

    def _load_static(self, lat: float, lon: float):
        self._fallback.setText("Loading map…")
        url = (
            "https://staticmap.openstreetmap.de/staticmap.php"
            f"?center={lat},{lon}&zoom=9&size=800x400&markers={lat},{lon},lightblue1"
        )
        req = QNetworkRequest(NetUrl(url))
        req.setRawHeader(b"User-Agent", b"GeoShield/1.0")
        self._nam.get(req)

    def _on_static_loaded(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            pix = QPixmap()
            if pix.loadFromData(reply.readAll()):
                self._fallback.setPixmap(
                    pix.scaled(
                        self._fallback.size(),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                return
        self._fallback.setText("Map preview unavailable")
        reply.deleteLater()

    def clear_map(self):
        self._lat = self._lon = None
        self._markers = []
        self._coords_lbl.setText("Awaiting analysis")
        if HAS_WEBENGINE:
            self._show_placeholder()
        elif hasattr(self, "_fallback"):
            self._fallback.setPixmap(QPixmap())
            self._fallback.setText("Run an analysis to explore the region")
