"""
Main dashboard — risk analysis workspace.
"""
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
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
from risk_engine import RiskEngine
from weather_api import WeatherAPI
from database import Database


class RiskCard(QFrame):
    def __init__(self, title: str, icon_char: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(theme.card_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        header = QHBoxLayout()
        icon = QLabel(icon_char)
        icon.setStyleSheet(
            f"font-size: 18px; color: {theme.ACCENT}; background: {theme.BG_INPUT};"
            f"border-radius: 8px; padding: 8px; min-width: 36px; max-width: 36px;"
        )
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(icon)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-weight: 600; font-size: 14px;")
        header.addWidget(title_lbl)
        header.addStretch()
        layout.addLayout(header)

        self._score_lbl = QLabel("—")
        self._score_lbl.setStyleSheet(theme.title_style(22))
        layout.addWidget(self._score_lbl)

        self._level_lbl = QLabel("Awaiting analysis")
        self._level_lbl.setStyleSheet(theme.muted_style())
        layout.addWidget(self._level_lbl)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        layout.addWidget(self._bar)

    def set_risk(self, score: float, level: str):
        self._score_lbl.setText(f"{score:.0f} / 100")
        self._level_lbl.setText(level.upper())
        color = theme.risk_color(level)
        self._level_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {color}; letter-spacing: 1px;"
        )
        self._bar.setValue(int(score))
        self._bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}"
        )


class DashboardPage(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._risk_engine = RiskEngine()
        self._weather_api = WeatherAPI()
        self._database = Database()
        self._analyzing = False
        self._setup_ui()

    def set_user(self, user: dict):
        self._user = user
        name = user.get("full_name", "User")
        self._user_label.setText(name)
        self._avatar.setText(name[0].upper() if name else "?")

    def _setup_ui(self):
        stack = QStackedLayout(self)
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(24, 24, 24, 24)
        body.setSpacing(24)

        body.addWidget(self._build_sidebar(), stretch=0)
        body.addWidget(self._build_main_content(), stretch=1)

        root.addLayout(body)
        stack.addWidget(content)

        self._overlay = self._build_loading_overlay()
        stack.addWidget(self._overlay)
        self._overlay.hide()

    def _build_loading_overlay(self) -> QWidget:
        overlay = QFrame()
        overlay.setStyleSheet(
            f"background-color: rgba(15, 20, 25, 0.85);"
        )
        layout = QVBoxLayout(overlay)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Running analysis")
        title.setStyleSheet(theme.title_style(20))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Fetching weather data and computing risk scores...")
        sub.setStyleSheet(theme.subtitle_style())
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        bar = QProgressBar()
        bar.setRange(0, 0)
        bar.setFixedWidth(280)
        bar.setTextVisible(False)
        layout.addWidget(bar, alignment=Qt.AlignmentFlag.AlignCenter)

        return overlay

    def _build_header(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet(
            f"background-color: {theme.BG_SECONDARY}; border-bottom: 1px solid {theme.BORDER};"
        )
        bar.setFixedHeight(64)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)

        brand = QLabel("GEOSHIELD")
        brand.setStyleSheet(theme.accent_label_style())
        layout.addWidget(brand)

        tagline = QLabel("Disaster Risk Intelligence Platform")
        tagline.setStyleSheet(theme.muted_style())
        layout.addWidget(tagline)

        layout.addStretch()

        self._status_chip = QLabel("Ready")
        self._status_chip.setStyleSheet(
            f"background-color: {theme.BG_INPUT}; color: {theme.SUCCESS};"
            f"padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;"
        )
        layout.addWidget(self._status_chip)

        layout.addSpacing(16)

        self._avatar = QLabel("?")
        self._avatar.setFixedSize(36, 36)
        self._avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._avatar.setStyleSheet(
            f"background-color: {theme.ACCENT_MUTED}; color: {theme.ACCENT};"
            f"border-radius: 18px; font-weight: 700; font-size: 14px;"
        )
        layout.addWidget(self._avatar)

        self._user_label = QLabel("User")
        self._user_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(self._user_label)

        logout_btn = QPushButton("Sign out")
        logout_btn.setProperty("class", "secondary")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

        return bar

    def _build_sidebar(self) -> QWidget:
        panel = QFrame()
        panel.setFixedWidth(340)
        panel.setStyleSheet(theme.card_style())
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Location Analysis")
        title.setStyleSheet(theme.title_style(18))
        layout.addWidget(title)

        desc = QLabel(
            "Enter a city to run a multi-factor risk assessment "
            "using live weather and historical disaster data."
        )
        desc.setStyleSheet(theme.subtitle_style())
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(8)

        loc_lbl = QLabel("City or region")
        loc_lbl.setStyleSheet(theme.muted_style() + "font-weight: 600;")
        layout.addWidget(loc_lbl)

        self._search = QLineEdit()
        self._search.setPlaceholderText("e.g. Athens, Tokyo, New Orleans")
        self._search.returnPressed.connect(self._start_analysis)
        layout.addWidget(self._search)

        self._analyze_btn = QPushButton("Run Risk Analysis")
        self._analyze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._analyze_btn.clicked.connect(self._start_analysis)
        layout.addWidget(self._analyze_btn)

        layout.addSpacing(12)

        weather_title = QLabel("Current Conditions")
        weather_title.setStyleSheet(theme.muted_style() + "font-weight: 600;")
        layout.addWidget(weather_title)

        self._weather_grid = QGridLayout()
        self._weather_labels = {}
        for i, (key, label) in enumerate(
            [
                ("temp", "Temperature"),
                ("humidity", "Humidity"),
                ("wind", "Wind"),
                ("condition", "Condition"),
            ]
        ):
            k = QLabel(label)
            k.setStyleSheet(theme.muted_style())
            v = QLabel("—")
            v.setStyleSheet("font-weight: 600;")
            self._weather_labels[key] = v
            self._weather_grid.addWidget(k, i, 0)
            self._weather_grid.addWidget(v, i, 1)
        layout.addLayout(self._weather_grid)

        layout.addStretch()

        hist = QLabel("Historical events in database")
        hist.setStyleSheet(theme.muted_style())
        layout.addWidget(hist)
        self._hist_count = QLabel("—")
        self._hist_count.setStyleSheet(theme.title_style(20))
        layout.addWidget(self._hist_count)

        return panel

    def _build_main_content(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        header_row = QHBoxLayout()
        results_title = QLabel("Risk Assessment")
        results_title.setStyleSheet(theme.title_style(22))
        header_row.addWidget(results_title)
        header_row.addStretch()

        self._location_lbl = QLabel("No location selected")
        self._location_lbl.setStyleSheet(theme.subtitle_style())
        header_row.addWidget(self._location_lbl)
        layout.addLayout(header_row)

        cards = QHBoxLayout()
        cards.setSpacing(16)
        self._flood_card = RiskCard("Flood Risk", "F")
        self._fire_card = RiskCard("Wildfire Risk", "W")
        self._landslide_card = RiskCard("Landslide Risk", "L")
        cards.addWidget(self._flood_card)
        cards.addWidget(self._fire_card)
        cards.addWidget(self._landslide_card)
        layout.addLayout(cards)

        overall_frame = QFrame()
        overall_frame.setStyleSheet(theme.card_style())
        overall_layout = QVBoxLayout(overall_frame)
        overall_layout.setContentsMargins(24, 20, 24, 20)

        overall_header = QHBoxLayout()
        overall_title = QLabel("Overall Risk Score")
        overall_title.setStyleSheet("font-weight: 600; font-size: 15px;")
        overall_header.addWidget(overall_title)
        overall_header.addStretch()
        self._overall_score = QLabel("—")
        self._overall_score.setStyleSheet(theme.title_style(28))
        overall_header.addWidget(self._overall_score)
        overall_layout.addLayout(overall_header)

        self._overall_bar = QProgressBar()
        self._overall_bar.setRange(0, 100)
        self._overall_bar.setValue(0)
        self._overall_bar.setFixedHeight(12)
        self._overall_bar.setTextVisible(False)
        overall_layout.addWidget(self._overall_bar)

        self._overall_level = QLabel("Run an analysis to see composite risk")
        self._overall_level.setStyleSheet(theme.muted_style())
        overall_layout.addWidget(self._overall_level)

        layout.addWidget(overall_frame)

        map_frame = QFrame()
        map_frame.setStyleSheet(
            theme.card_style()
            + f"min-height: 220px; background-color: {theme.BG_INPUT};"
        )
        map_layout = QVBoxLayout(map_frame)
        map_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        map_title = QLabel("Geographic Coverage")
        map_title.setStyleSheet(theme.title_style(16))
        map_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_layout.addWidget(map_title)

        map_sub = QLabel(
            "Map visualization will display analyzed coordinates.\n"
            "Search a location and run analysis to populate this view."
        )
        map_sub.setStyleSheet(theme.subtitle_style())
        map_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_layout.addWidget(map_sub)

        self._map_coords = QLabel("")
        self._map_coords.setStyleSheet(theme.muted_style())
        self._map_coords.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_layout.addWidget(self._map_coords)

        layout.addWidget(map_frame)
        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _set_status(self, text: str, color: str):
        self._status_chip.setText(text)
        self._status_chip.setStyleSheet(
            f"background-color: {theme.BG_INPUT}; color: {color};"
            f"padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;"
        )

    def _start_analysis(self):
        if self._analyzing:
            return
        city = self._search.text().strip()
        if not city:
            QMessageBox.warning(self, "Input required", "Please enter a city or region name.")
            return

        self._analyzing = True
        self._overlay.show()
        self._overlay.raise_()
        self._analyze_btn.setEnabled(False)
        self._analyze_btn.setText("Analyzing...")
        self._set_status("Analyzing...", theme.WARNING)
        self._location_lbl.setText(city.title())

        QTimer.singleShot(80, lambda: self._perform_analysis(city))

    def _perform_analysis(self, city: str):
        try:
            weather = self._weather_api.get_weather(city)
            if not weather:
                QMessageBox.critical(
                    self,
                    "Analysis failed",
                    f"Could not retrieve weather data for \"{city}\".",
                )
                self._set_status("Error", theme.DANGER)
                return

            risks = self._risk_engine.calculate_risks(
                temperature=weather["temperature"],
                humidity=weather["humidity"],
                wind_speed=weather["wind_speed"],
                precipitation=weather.get("precipitation", 0),
            )
            historical_count = self._database.count_events_near(city)

            self._weather_labels["temp"].setText(f"{weather['temperature']:.1f} °C")
            self._weather_labels["humidity"].setText(f"{weather['humidity']}%")
            self._weather_labels["wind"].setText(f"{weather['wind_speed']:.1f} km/h")
            self._weather_labels["condition"].setText(
                weather.get("condition", "N/A")
            )
            self._hist_count.setText(str(historical_count))

            self._flood_card.set_risk(risks["flood"]["score"], risks["flood"]["level"])
            self._fire_card.set_risk(risks["fire"]["score"], risks["fire"]["level"])
            self._landslide_card.set_risk(
                risks["landslide"]["score"], risks["landslide"]["level"]
            )

            overall = risks["overall"]
            level = self._risk_engine.get_level(overall)
            color = theme.risk_color(level)

            self._overall_score.setText(f"{overall:.0f}")
            self._overall_bar.setValue(int(overall))
            self._overall_bar.setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {color}; border-radius: 6px; }}"
            )
            self._overall_level.setText(f"Composite level: {level.upper()}")
            self._overall_level.setStyleSheet(
                f"color: {color}; font-weight: 600; font-size: 13px;"
            )

            self._map_coords.setText(f"Active region: {city.title()}")
            self._set_status("Analysis complete", theme.SUCCESS)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {e}")
            self._set_status("Error", theme.DANGER)
        finally:
            self._analyzing = False
            self._overlay.hide()
            self._analyze_btn.setEnabled(True)
            self._analyze_btn.setText("Run Risk Analysis")
