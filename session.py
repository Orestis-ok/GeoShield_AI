"""Persistent session (remember me)."""
import json
import os

from config import SESSION_PATH


def save_session(user: dict, remember: bool = True) -> None:
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    payload = {
        "user_id": user["id"] if remember else None,
        "email": user["email"],
        "remember": remember,
    }
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def load_session() -> dict | None:
    if not os.path.exists(SESSION_PATH):
        return None
    try:
        with open(SESSION_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def clear_session() -> None:
    if os.path.exists(SESSION_PATH):
        os.remove(SESSION_PATH)
