"""
Analysis history and regional disaster archive.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QHBoxLayout,
)

import theme
from database import Database
from ui.widgets import SectionTitle, MetricPill


class HistoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._db = Database()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(20)

        head = QHBoxLayout()
        head.addWidget(
            SectionTitle(
                "History & Archives",
                "Your saved intelligence runs and curated regional disaster records.",
            ),
            stretch=1,
        )
        self._count_pill = MetricPill("0 analyses", theme.ACCENT)
        head.addWidget(self._count_pill, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(head)

        layout.addWidget(QLabel("Your analyses"))
        self._history_table = self._make_table(
            ["Date", "Location", "Flood", "Fire", "Landslide", "Composite", "Level"]
        )
        layout.addWidget(self._history_table)

        layout.addWidget(QLabel("Regional disaster archive"))
        self._disaster_table = self._make_table(
            ["City", "Country", "Type", "Severity", "Year", "Details"]
        )
        layout.addWidget(self._disaster_table)

        self._empty = QFrame()
        self._empty.setStyleSheet(theme.card_style())
        el = QVBoxLayout(self._empty)
        el.setContentsMargins(32, 40, 32, 40)
        msg = QLabel("Sign in and run analyses to build your intelligence history.")
        msg.setStyleSheet(theme.subtitle_style())
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.addWidget(msg)
        layout.addWidget(self._empty)

    def _make_table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setMinimumHeight(200)
        return table

    def set_user(self, user: dict | None):
        self._user = user
        self.refresh()

    def refresh(self, disasters: list[dict] | None = None):
        if not self._user:
            self._history_table.setRowCount(0)
            self._disaster_table.setRowCount(0)
            self._empty.show()
            self._count_pill.setText("0 analyses")
            return

        self._empty.hide()
        rows = self._db.get_analysis_history(self._user["id"])
        self._count_pill.setText(f"{len(rows)} analyses")
        self._count_pill.setStyleSheet(theme.status_chip_style(theme.ACCENT))

        self._history_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            created = (r.get("created_at") or "—")[:16]
            self._history_table.setItem(i, 0, QTableWidgetItem(created))
            self._history_table.setItem(
                i, 1, QTableWidgetItem(r.get("display_name", r["city"]))
            )
            self._history_table.setItem(
                i, 2, QTableWidgetItem(f"{r.get('flood_score', 0):.0f}")
            )
            self._history_table.setItem(
                i, 3, QTableWidgetItem(f"{r.get('fire_score', 0):.0f}")
            )
            self._history_table.setItem(
                i, 4, QTableWidgetItem(f"{r.get('landslide_score', 0):.0f}")
            )
            self._history_table.setItem(
                i, 5, QTableWidgetItem(f"{r.get('overall_score', 0):.0f}")
            )
            level_item = QTableWidgetItem(r["overall_level"].upper())
            level_item.setForeground(QColor(theme.risk_color(r["overall_level"])))
            self._history_table.setItem(i, 6, level_item)

        if disasters is None and rows:
            disasters = self._db.get_disasters_for_city(rows[0]["city"])
        disasters = disasters or []
        self._disaster_table.setRowCount(len(disasters))
        for i, d in enumerate(disasters):
            self._disaster_table.setItem(i, 0, QTableWidgetItem(d["city"]))
            self._disaster_table.setItem(i, 1, QTableWidgetItem(d.get("country", "")))
            self._disaster_table.setItem(i, 2, QTableWidgetItem(d["event_type"]))
            sev = QTableWidgetItem(d["severity"])
            sev.setForeground(
                QColor(
                    theme.risk_color(
                        "critical" if d["severity"] == "critical" else "high"
                    )
                )
            )
            self._disaster_table.setItem(i, 3, sev)
            self._disaster_table.setItem(i, 4, QTableWidgetItem(str(d["year"])))
            self._disaster_table.setItem(
                i, 5, QTableWidgetItem(d.get("description", ""))
            )
