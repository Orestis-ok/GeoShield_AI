"""
Local user authentication (SQLite).
"""
import hashlib
import secrets
import sqlite3

from config import DB_PATH, ensure_sqlite_database


class AuthManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        ensure_sqlite_database(self.db_path)
        self._init_users_table()

    def _init_users_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

    def register(self, email: str, full_name: str, password: str) -> tuple[bool, str]:
        email = email.strip().lower()
        full_name = full_name.strip()

        if not email or "@" not in email:
            return False, "Please enter a valid email address."
        if len(full_name) < 2:
            return False, "Name must be at least 2 characters."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."

        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, full_name, password_hash, salt) VALUES (?, ?, ?, ?)",
                (email, full_name, password_hash, salt),
            )
            conn.commit()
            conn.close()
            return True, ""
        except sqlite3.IntegrityError:
            return False, "An account with this email already exists."

    def login(self, email: str, password: str) -> tuple[bool, dict | None, str]:
        email = email.strip().lower()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, full_name, password_hash, salt FROM users WHERE email = ?",
            (email,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return False, None, "Invalid email or password."

        user_id, user_email, full_name, stored_hash, salt = row
        if self._hash_password(password, salt) != stored_hash:
            return False, None, "Invalid email or password."

        return True, {"id": user_id, "email": user_email, "full_name": full_name}, ""

    def get_user_by_id(self, user_id: int) -> dict | None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, full_name FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {"id": row[0], "email": row[1], "full_name": row[2]}

    def get_user_by_email(self, email: str) -> dict | None:
        email = email.strip().lower()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, full_name FROM users WHERE email = ?",
            (email,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {"id": row[0], "email": row[1], "full_name": row[2]}
