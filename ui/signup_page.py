"""
Premium registration form.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QProgressBar,
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        heading = QLabel("Start your trial workspace")
        heading.setStyleSheet(theme.title_style(26))
        layout.addWidget(heading)

        sub = QLabel(
            "Full access to live weather intelligence, composite risk scoring, "
            "and exportable reports — built for operations teams."
        )
        sub.setStyleSheet(theme.subtitle_style())
        sub.setWordWrap(True)
        layout.addWidget(sub)
        layout.addSpacing(4)

        for label_text, placeholder, attr, secret in [
            ("Full name", "Alex Morgan", "_full_name", False),
            ("Work email", "you@company.com", "_email", False),
            ("Password", "Minimum 6 characters", "_password", True),
        ]:
            lbl = QLabel(label_text)
            lbl.setStyleSheet(theme.auth_input_label_style())
            layout.addWidget(lbl)
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            if secret:
                field.setEchoMode(QLineEdit.EchoMode.Password)
                field.textChanged.connect(self._update_strength)
            setattr(self, attr, field)
            layout.addWidget(field)

        strength_row = QHBoxLayout()
        self._strength_bar = QProgressBar()
        self._strength_bar.setRange(0, 100)
        self._strength_bar.setFixedHeight(6)
        self._strength_bar.setTextVisible(False)
        strength_row.addWidget(self._strength_bar, stretch=1)
        self._strength_lbl = QLabel("")
        self._strength_lbl.setStyleSheet(theme.muted_style())
        strength_row.addWidget(self._strength_lbl)
        layout.addLayout(strength_row)

        self._terms = QCheckBox(
            "I agree to local data processing and GeoShield terms of use"
        )
        layout.addWidget(self._terms)

        self._error = QLabel("")
        self._error.setStyleSheet(f"color: {theme.DANGER}; font-size: 12px;")
        self._error.setWordWrap(True)
        self._error.hide()
        layout.addWidget(self._error)

        signup_btn = QPushButton("Create account & continue")
        signup_btn.setMinimumHeight(46)
        signup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_btn.clicked.connect(self._on_signup)
        layout.addWidget(signup_btn)

        footer = QHBoxLayout()
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.addWidget(QLabel("Already registered?"))
        login_link = QPushButton("Sign in")
        login_link.setProperty("class", "ghost")
        login_link.clicked.connect(self.go_to_login.emit)
        footer.addWidget(login_link)
        layout.addLayout(footer)

    def _update_strength(self, text: str):
        score = min(100, len(text) * 12 + (10 if any(c.isdigit() for c in text) else 0))
        self._strength_bar.setValue(score)
        if len(text) < 6:
            self._strength_lbl.setText("Weak")
            color = theme.DANGER
        elif score < 50:
            self._strength_lbl.setText("Fair")
            color = theme.WARNING
        else:
            self._strength_lbl.setText("Strong")
            color = theme.SUCCESS
        self._strength_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background: {color}; border-radius: 3px; }}"
        )

    def _show_error(self, message: str):
        self._error.setText(message)
        self._error.show()

    def _on_signup(self):
        self._error.hide()
        if not self._terms.isChecked():
            self._show_error("Please accept the terms to create your account.")
            return
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
        self._terms.setChecked(False)
        self._strength_bar.setValue(0)
        self._strength_lbl.clear()
        self._error.hide()
