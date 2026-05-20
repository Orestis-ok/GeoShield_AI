"""
Sign up page.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
)

import theme
from auth import AuthManager


class SignupPage(QWidget):
    signup_success = pyqtSignal(dict)
    go_to_login = pyqtSignal()

    def __init__(self, auth: AuthManager, parent=None):
        super().__init__(parent)
        self._auth = auth
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet(theme.card_style() + "padding: 8px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(14)

        logo = QLabel("GEOSHIELD")
        logo.setStyleSheet(theme.accent_label_style() + "letter-spacing: 4px;")
        card_layout.addWidget(logo)

        heading = QLabel("Create your account")
        heading.setStyleSheet(theme.title_style(24))
        card_layout.addWidget(heading)

        sub = QLabel("Start analyzing geographic disaster risks")
        sub.setStyleSheet(theme.subtitle_style())
        card_layout.addWidget(sub)

        card_layout.addSpacing(4)

        fields = [
            ("Full name", "Your name", "_full_name", False),
            ("Email", "you@company.com", "_email", False),
            ("Password", "At least 6 characters", "_password", True),
        ]
        for label_text, placeholder, attr, is_password in fields:
            lbl = QLabel(label_text)
            lbl.setStyleSheet(theme.muted_style() + "font-weight: 600;")
            card_layout.addWidget(lbl)
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            if is_password:
                field.setEchoMode(QLineEdit.EchoMode.Password)
            setattr(self, attr, field)
            card_layout.addWidget(field)

        self._error = QLabel("")
        self._error.setStyleSheet(f"color: {theme.DANGER}; font-size: 12px;")
        self._error.setWordWrap(True)
        self._error.hide()
        card_layout.addWidget(self._error)

        signup_btn = QPushButton("Create account")
        signup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_btn.clicked.connect(self._on_signup)
        card_layout.addWidget(signup_btn)

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(QLabel("Already have an account?"))
        login_link = QPushButton("Sign in")
        login_link.setProperty("class", "ghost")
        login_link.setCursor(Qt.CursorShape.PointingHandCursor)
        login_link.clicked.connect(self.go_to_login.emit)
        row.addWidget(login_link)
        card_layout.addLayout(row)

        outer.addWidget(card)

    def _show_error(self, message: str):
        self._error.setText(message)
        self._error.show()

    def _on_signup(self):
        self._error.hide()
        ok, msg = self._auth.register(
            self._email.text(),
            self._full_name.text(),
            self._password.text(),
        )
        if not ok:
            self._show_error(msg)
            return

        login_ok, user, login_msg = self._auth.login(
            self._email.text(),
            self._password.text(),
        )
        if login_ok:
            self.signup_success.emit(user)
        else:
            self._show_error(login_msg)

    def clear_fields(self):
        self._full_name.clear()
        self._email.clear()
        self._password.clear()
        self._error.hide()
