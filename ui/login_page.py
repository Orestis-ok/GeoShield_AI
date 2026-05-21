"""
Premium login form.
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
    QCheckBox,
)

import theme
from auth import AuthManager
from preferences import load_preferences


class LoginPage(QWidget):
    login_success = pyqtSignal(dict)
    go_to_signup = pyqtSignal()

    def __init__(self, auth: AuthManager, parent=None):
        super().__init__(parent)
        self._auth = auth
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        badge = QLabel("PROFESSIONAL")
        badge.setStyleSheet(theme.pro_badge_style())
        badge.setFixedWidth(120)
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        heading = QLabel("Welcome back")
        heading.setStyleSheet(theme.title_style(28))
        layout.addWidget(heading)

        sub = QLabel("Sign in to your GeoShield intelligence workspace")
        sub.setStyleSheet(theme.subtitle_style())
        layout.addWidget(sub)
        layout.addSpacing(8)

        email_lbl = QLabel("Work email")
        email_lbl.setStyleSheet(theme.auth_input_label_style())
        layout.addWidget(email_lbl)
        self._email = QLineEdit()
        self._email.setPlaceholderText("analyst@organization.com")
        layout.addWidget(self._email)

        pass_lbl = QLabel("Password")
        pass_lbl.setStyleSheet(theme.auth_input_label_style())
        layout.addWidget(pass_lbl)
        self._password = QLineEdit()
        self._password.setPlaceholderText("Enter your password")
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.returnPressed.connect(self._on_login)
        layout.addWidget(self._password)

        row = QHBoxLayout()
        prefs = load_preferences()
        self._remember = QCheckBox("Keep me signed in")
        self._remember.setChecked(prefs.get("remember_me", True))
        row.addWidget(self._remember)
        row.addStretch()
        layout.addLayout(row)

        self._error = QLabel("")
        self._error.setStyleSheet(f"color: {theme.DANGER}; font-size: 12px;")
        self._error.setWordWrap(True)
        self._error.hide()
        layout.addWidget(self._error)

        login_btn = QPushButton("Sign in to GeoShield")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setMinimumHeight(46)
        login_btn.clicked.connect(self._on_login)
        layout.addWidget(login_btn)

        footer = QHBoxLayout()
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint = QLabel("New to GeoShield?")
        hint.setStyleSheet(theme.muted_style())
        footer.addWidget(hint)
        signup_link = QPushButton("Create professional account")
        signup_link.setProperty("class", "ghost")
        signup_link.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_link.clicked.connect(self.go_to_signup.emit)
        footer.addWidget(signup_link)
        layout.addLayout(footer)

    def remember_me(self) -> bool:
        return self._remember.isChecked()

    def _show_error(self, message: str):
        self._error.setText(message)
        self._error.show()

    def _on_login(self):
        self._error.hide()
        ok, user, msg = self._auth.login(self._email.text(), self._password.text())
        if ok:
            self.login_success.emit(user)
        else:
            self._show_error(msg)

    def clear_fields(self):
        self._email.clear()
        self._password.clear()
        self._error.hide()

    def set_email(self, email: str):
        self._email.setText(email)
