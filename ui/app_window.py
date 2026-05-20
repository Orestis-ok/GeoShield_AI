"""
Main application shell — screen navigation.
"""
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout

import theme
from auth import AuthManager
from ui.loading_screen import LoadingScreen
from ui.login_page import LoginPage
from ui.signup_page import SignupPage
from ui.dashboard_page import DashboardPage


class AppWindow(QMainWindow):
    PAGE_LOADING = 0
    PAGE_LOGIN = 1
    PAGE_SIGNUP = 2
    PAGE_DASHBOARD = 3

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoShield — Disaster Risk Intelligence")
        self.setMinimumSize(1280, 800)
        self.resize(1400, 900)

        self._auth = AuthManager()
        self._current_user = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        self._loading = LoadingScreen()
        self._login = LoginPage(self._auth)
        self._signup = SignupPage(self._auth)
        self._dashboard = DashboardPage()

        for page in (self._loading, self._login, self._signup, self._dashboard):
            self._stack.addWidget(page)

        self._connect_signals()
        self._go_to(self.PAGE_LOADING)
        self._loading.start()

    def _connect_signals(self):
        self._loading.finished.connect(self._on_loading_done)
        self._login.login_success.connect(self._on_auth_success)
        self._login.go_to_signup.connect(lambda: self._go_to(self.PAGE_SIGNUP))
        self._signup.signup_success.connect(self._on_auth_success)
        self._signup.go_to_login.connect(self._on_go_login)
        self._dashboard.logout_requested.connect(self._on_logout)

    def _go_to(self, index: int):
        self._stack.setCurrentIndex(index)

    def _on_loading_done(self):
        self._go_to(self.PAGE_LOGIN)

    def _on_auth_success(self, user: dict):
        self._current_user = user
        self._dashboard.set_user(user)
        self._go_to(self.PAGE_DASHBOARD)

    def _on_go_login(self):
        self._signup.clear_fields()
        self._go_to(self.PAGE_LOGIN)

    def _on_logout(self):
        self._current_user = None
        self._login.clear_fields()
        self._signup.clear_fields()
        self._go_to(self.PAGE_LOGIN)
