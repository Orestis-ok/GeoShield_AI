"""
Login page.
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


class LoginPage(QWidget):
    login_success = pyqtSignal(dict)
    go_to_signup = pyqtSignal()

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
        card_layout.setSpacing(16)

        logo = QLabel("GEOSHIELD")
        logo.setStyleSheet(theme.accent_label_style() + "letter-spacing: 4px;")
        card_layout.addWidget(logo)

        heading = QLabel("Welcome back")
        heading.setStyleSheet(theme.title_style(24))
        card_layout.addWidget(heading)

        sub = QLabel("Sign in to access disaster risk analysis")
        sub.setStyleSheet(theme.subtitle_style())
        card_layout.addWidget(sub)

        card_layout.addSpacing(8)

        email_lbl = QLabel("Email")
        email_lbl.setStyleSheet(theme.muted_style() + "font-weight: 600;")
        card_layout.addWidget(email_lbl)

        self._email = QLineEdit()
        self._email.setPlaceholderText("you@company.com")
        card_layout.addWidget(self._email)

        pass_lbl = QLabel("Password")
        pass_lbl.setStyleSheet(theme.muted_style() + "font-weight: 600;")
        card_layout.addWidget(pass_lbl)

        self._password = QLineEdit()
        self._password.setPlaceholderText("Enter your password")
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.returnPressed.connect(self._on_login)
        card_layout.addWidget(self._password)

        self._error = QLabel("")
        self._error.setStyleSheet(f"color: {theme.DANGER}; font-size: 12px;")
        self._error.setWordWrap(True)
        self._error.hide()
        card_layout.addWidget(self._error)

        card_layout.addSpacing(4)

        login_btn = QPushButton("Sign in")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self._on_login)
        card_layout.addWidget(login_btn)

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(QLabel("Don't have an account?"))
        signup_link = QPushButton("Create account")
        signup_link.setProperty("class", "ghost")
        signup_link.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_link.clicked.connect(self.go_to_signup.emit)
        row.addWidget(signup_link)
        card_layout.addLayout(row)

        outer.addWidget(card)

    def _show_error(self, message: str):
        self._error.setText(message)
        self._error.show()

    def _on_login(self):
        self._error.hide()
        ok, user, msg = self._auth.login(
            self._email.text(),
            self._password.text(),
        )
        if ok:
            self.login_success.emit(user)
        else:
            self._show_error(msg)

    def clear_fields(self):
        self._email.clear()
        self._password.clear()
        self._error.hide()
