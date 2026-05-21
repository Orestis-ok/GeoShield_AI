"""
Main application shell — screen navigation.
"""
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout

from auth import AuthManager
from session import load_session, save_session, clear_session
from preferences import load_preferences, save_preferences
from ui.loading_screen import LoadingScreen
from ui.login_page import LoginPage
from ui.signup_page import SignupPage
from ui.auth_layout import build_auth_page
from ui.shell_page import ShellPage


class AppWindow(QMainWindow):
    PAGE_LOADING = 0
    PAGE_LOGIN = 1
    PAGE_SIGNUP = 2
    PAGE_SHELL = 3

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoShield Pro — Disaster Risk Intelligence")
        self.setMinimumSize(1320, 820)
        self.resize(1440, 920)

        self._auth = AuthManager()
        self._current_user = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        self._loading = LoadingScreen()
        self._login_form = LoginPage(self._auth)
        self._signup_form = SignupPage(self._auth)
        self._login = build_auth_page(self._login_form)
        self._signup = build_auth_page(self._signup_form)
        self._shell = ShellPage()

        for page in (self._loading, self._login, self._signup, self._shell):
            self._stack.addWidget(page)

        self._connect_signals()
        self._go_to(self.PAGE_LOADING)
        self._loading.start()

    def _connect_signals(self):
        self._loading.finished.connect(self._on_loading_done)
        self._login_form.login_success.connect(self._on_login_success)
        self._login_form.go_to_signup.connect(lambda: self._go_to(self.PAGE_SIGNUP))
        self._signup_form.signup_success.connect(self._on_login_success)
        self._signup_form.go_to_login.connect(self._on_go_login)
        self._shell.logout_requested.connect(self._on_logout)

    def _go_to(self, index: int):
        self._stack.setCurrentIndex(index)

    def _on_loading_done(self):
        session = load_session()
        prefs = load_preferences()
        if session and session.get("remember") and session.get("user_id"):
            user = self._auth.get_user_by_id(session["user_id"])
            if not user and session.get("email"):
                user = self._auth.get_user_by_email(session["email"])
            if user:
                self._enter_workspace(user)
                return
        email = session.get("email", "") if session else ""
        if email:
            self._login_form.set_email(email)
        self._go_to(self.PAGE_LOGIN)

    def _on_login_success(self, user: dict):
        remember = self._login_form.remember_me()
        prefs = load_preferences()
        prefs["remember_me"] = remember
        save_preferences(prefs)
        save_session(user, remember=remember)
        self._enter_workspace(user)

    def _enter_workspace(self, user: dict):
        self._current_user = user
        self._shell.set_user(user)
        self._go_to(self.PAGE_SHELL)

    def _on_go_login(self):
        self._signup_form.clear_fields()
        self._go_to(self.PAGE_LOGIN)

    def _on_logout(self):
        self._current_user = None
        clear_session()
        self._login_form.clear_fields()
        self._signup_form.clear_fields()
        self._go_to(self.PAGE_LOGIN)
