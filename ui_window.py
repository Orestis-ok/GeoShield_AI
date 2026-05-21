"""
Legacy entry point — redirects to the new app shell.

Use main.py to launch the application.
"""
from ui.app_window import AppWindow

# Backward compatibility
MainWindow = AppWindow
