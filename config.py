"""Application configuration."""
import os
import sys
from pathlib import Path

APP_NAME = "GeoShield Pro"
APP_TAGLINE = "Enterprise Disaster Risk Intelligence"
APP_VERSION = "2.1.0"
APP_BUILD = "2026.05"
ORG_NAME = "GeoShield Technologies"
AUTHOR_NAME = "Orestis Kerkines"
AUTHOR_CREDIT = "By Orestis Kerkines"
MODEL_VERSION = "GS-RM-2.1"
MODEL_CODENAME = "Tri-Hazard Composite Engine"

_SQLITE_MAGIC = b"SQLite format 3\x00"


def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR = app_base_dir()
DATA_DIR = BASE_DIR / "data"
DB_PATH = str(DATA_DIR / "geoshield.db")
SESSION_PATH = str(DATA_DIR / "session.json")
REPORTS_DIR = str(DATA_DIR / "reports")
SCIENCE_EXPORT_DIR = str(DATA_DIR / "science_exports")

QUICK_LOCATIONS = [
    "Athens",
    "Tokyo",
    "New Orleans",
    "Los Angeles",
    "London",
    "Sydney",
    "Miami",
    "Jakarta",
]


def ensure_sqlite_database(db_path: str) -> None:
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    if not os.path.isfile(db_path):
        return
    try:
        if os.path.getsize(db_path) < 16:
            raise ValueError("too small")
        with open(db_path, "rb") as f:
            if f.read(16) != _SQLITE_MAGIC:
                raise ValueError("invalid header")
    except (OSError, ValueError):
        os.remove(db_path)
