"""Scientific data export — CSV and JSON for research workflows."""
import csv
import json
import os
from datetime import datetime

from config import SCIENCE_EXPORT_DIR, MODEL_VERSION, AUTHOR_NAME


def export_science_json(result: dict) -> str:
    os.makedirs(SCIENCE_EXPORT_DIR, exist_ok=True)
    city = result["city"].replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SCIENCE_EXPORT_DIR, f"{city}_{ts}_science.json")
    payload = {
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "model_version": MODEL_VERSION,
            "author": AUTHOR_NAME,
            "location": result.get("weather", {}).get("display_name", result["city"]),
        },
        "analysis": result,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    return path


def export_hourly_csv(result: dict) -> str:
    os.makedirs(SCIENCE_EXPORT_DIR, exist_ok=True)
    city = result["city"].replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SCIENCE_EXPORT_DIR, f"{city}_{ts}_hourly.csv")
    hourly = result.get("weather", {}).get("hourly", [])
    if not hourly:
        return path
    fields = list(hourly[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(hourly)
    return path


def export_daily_csv(result: dict) -> str:
    os.makedirs(SCIENCE_EXPORT_DIR, exist_ok=True)
    city = result["city"].replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SCIENCE_EXPORT_DIR, f"{city}_{ts}_daily_forecast.csv")
    daily = result.get("weather", {}).get("daily", [])
    if not daily:
        return path
    fields = list(daily[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(daily)
    return path
