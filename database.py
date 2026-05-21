"""
Local SQLite database — disasters, analyses, and history.
"""
import json
import sqlite3
from datetime import datetime, timezone

from config import DB_PATH, ensure_sqlite_database


class Database:
    def __init__(self):
        self.db_path = DB_PATH
        ensure_sqlite_database(self.db_path)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disasters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                country TEXT DEFAULT '',
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                year INTEGER NOT NULL,
                description TEXT DEFAULT ''
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                city TEXT NOT NULL,
                display_name TEXT,
                country TEXT DEFAULT '',
                lat REAL,
                lon REAL,
                temperature REAL,
                humidity REAL,
                wind_speed REAL,
                precipitation REAL,
                flood_score REAL,
                fire_score REAL,
                landslide_score REAL,
                overall_score REAL,
                overall_level TEXT,
                weather_json TEXT,
                risks_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self._migrate_disasters(cursor)
        self._seed_disasters(cursor)
        conn.commit()
        conn.close()

    def _migrate_disasters(self, cursor):
        cursor.execute("PRAGMA table_info(disasters)")
        cols = {row[1] for row in cursor.fetchall()}
        if "country" not in cols:
            cursor.execute("ALTER TABLE disasters ADD COLUMN country TEXT DEFAULT ''")
        if "description" not in cols:
            cursor.execute("ALTER TABLE disasters ADD COLUMN description TEXT DEFAULT ''")

    def _seed_disasters(self, cursor):
        cursor.execute("SELECT COUNT(*) FROM disasters")
        if cursor.fetchone()[0] > 0:
            return
        samples = [
            ("Athens", "Greece", "flood", "high", 2020,
             "Severe urban flooding after intense rainfall."),
            ("Athens", "Greece", "fire", "critical", 2018,
             "Wildland-urban interface fire during heatwave."),
            ("Los Angeles", "USA", "fire", "critical", 2018,
             "Large wildfire driven by drought and Santa Ana winds."),
            ("New Orleans", "USA", "flood", "critical", 2005,
             "Catastrophic storm-surge flooding."),
            ("Tokyo", "Japan", "landslide", "high", 2018,
             "Slope failure following prolonged precipitation."),
            ("London", "UK", "flood", "moderate", 2021,
             "River overflow affecting low-lying districts."),
            ("Sydney", "Australia", "fire", "high", 2019,
             "Bushfire season with extreme temperature anomalies."),
        ]
        cursor.executemany(
            """INSERT INTO disasters
               (city, country, event_type, severity, year, description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            samples,
        )

    def count_events_near(self, city: str) -> int:
        return len(self.get_disasters_for_city(city))

    def get_disasters_for_city(self, city: str, limit: int = 25) -> list[dict]:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT city, country, event_type, severity, year, description
               FROM disasters
               WHERE LOWER(city) LIKE LOWER(?)
                  OR LOWER(country) LIKE LOWER(?)
               ORDER BY year DESC
               LIMIT ?""",
            (f"%{city}%", f"%{city}%", limit),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def save_analysis(
        self,
        user_id: int,
        city: str,
        weather: dict,
        risks: dict,
    ) -> None:
        overall = risks["overall"]
        level = risks.get("overall_level") or "low"
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO analyses (
                user_id, city, display_name, country, lat, lon,
                temperature, humidity, wind_speed, precipitation,
                flood_score, fire_score, landslide_score,
                overall_score, overall_level, weather_json, risks_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                city,
                weather.get("display_name", city),
                weather.get("country", ""),
                weather.get("lat"),
                weather.get("lon"),
                weather.get("temperature"),
                weather.get("humidity"),
                weather.get("wind_speed"),
                weather.get("precipitation", 0),
                risks["flood"]["score"],
                risks["fire"]["score"],
                risks["landslide"]["score"],
                overall,
                level,
                json.dumps(weather),
                json.dumps(risks),
            ),
        )
        conn.commit()
        conn.close()

    def get_analysis_history(self, user_id: int, limit: int = 50) -> list[dict]:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, city, display_name, country, overall_score, overall_level,
                      flood_score, fire_score, landslide_score, created_at, lat, lon
               FROM analyses
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (user_id, limit),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def clear_user_history(self, user_id: int) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    def get_user_stats(self, user_id: int) -> dict:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS total, AVG(overall_score) AS avg_score FROM analyses WHERE user_id = ?",
            (user_id,),
        )
        row = dict(cursor.fetchone())
        conn.close()
        return {
            "total_analyses": row["total"] or 0,
            "avg_risk_score": round(row["avg_score"] or 0, 1),
        }
