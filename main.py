"""
GeoShield Pro — Desktop Application
"""
import sys

from PyQt6.QtWidgets import QApplication

import theme
from ui_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GeoShield Pro")
    app.setStyleSheet(theme.GLOBAL_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
