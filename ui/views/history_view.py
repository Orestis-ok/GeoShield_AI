"""
Analysis history and disaster archive.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QFrame,
)

import theme
from database import Database
from ui.widgets import SectionTitle


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

        layout.addWidget(
            SectionTitle(
                "History & Archives",
                "Your past analyses and regional disaster records from the GeoShield database.",
            )
        )

        layout.addWidget(QLabel("Your analyses"))
        self._history_table = self._make_table(
            ["Date", "Location", "Composite score", "Risk level"]
        )
        layout.addWidget(self._history_table)

        layout.addWidget(QLabel("Regional disaster archive (latest search)"))
        self._disaster_table = self._make_table(
            ["City", "Country", "Type", "Severity", "Year", "Details"]
        )
        layout.addWidget(self._disaster_table)

        self._empty = QLabel("Sign in and run analyses to build your history.")
        self._empty.setStyleSheet(theme.muted_style())
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty)

    def _make_table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setMinimumHeight(180)
        return table

    def set_user(self, user: dict | None):
        self._user = user
        self.refresh()

    def refresh(self, disasters: list[dict] | None = None):
        if not self._user:
            self._history_table.setRowCount(0)
            self._disaster_table.setRowCount(0)
            self._empty.show()
            return

        self._empty.hide()
        rows = self._db.get_analysis_history(self._user["id"])
        self._history_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            created = r["created_at"][:16] if r.get("created_at") else "—"
            self._history_table.setItem(i, 0, QTableWidgetItem(created))
            self._history_table.setItem(
                i, 1, QTableWidgetItem(r.get("display_name", r["city"]))
            )
            self._history_table.setItem(
                i, 2, QTableWidgetItem(f"{r['overall_score']:.0f}")
            )
            level_item = QTableWidgetItem(r["overall_level"].upper())
            level_item.setForeground(QColor(theme.risk_color(r["overall_level"])))
            self._history_table.setItem(i, 3, level_item)

        disasters = disasters or []
        self._disaster_table.setRowCount(len(disasters))
        for i, d in enumerate(disasters):
            self._disaster_table.setItem(i, 0, QTableWidgetItem(d["city"]))
            self._disaster_table.setItem(i, 1, QTableWidgetItem(d.get("country", "")))
            self._disaster_table.setItem(i, 2, QTableWidgetItem(d["event_type"]))
            self._disaster_table.setItem(i, 3, QTableWidgetItem(d["severity"]))
            self._disaster_table.setItem(i, 4, QTableWidgetItem(str(d["year"])))
            self._disaster_table.setItem(i, 5, QTableWidgetItem(d.get("description", "")))
