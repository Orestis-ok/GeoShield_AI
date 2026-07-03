"""User-facing application preferences (local JSON)."""
import json
import os

from config import DATA_DIR

PREFS_PATH = str(DATA_DIR / "preferences.json")

DEFAULTS = {
    "temperature_unit": "celsius",
    "default_location": "",
    "map_style": "dark",
    "remember_me": True,
    "auto_open_reports": True,
    "show_disaster_markers": True,
    "notifications_enabled": True,
}


def load_preferences() -> dict:
    prefs = dict(DEFAULTS)
    if os.path.isfile(PREFS_PATH):
        try:
            with open(PREFS_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                prefs.update(stored)
        except (json.JSONDecodeError, OSError):
            pass
    return prefs


def save_preferences(prefs: dict) -> None:
    os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
    merged = dict(DEFAULTS)
    merged.update(prefs)
    with open(PREFS_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)


def format_temperature(celsius: float, unit: str | None = None) -> str:
    prefs = load_preferences()
    unit = unit or prefs.get("temperature_unit", "celsius")
    if unit == "fahrenheit":
        return f"{celsius * 9 / 5 + 32:.1f} °F"
    return f"{celsius:.1f} °C"
