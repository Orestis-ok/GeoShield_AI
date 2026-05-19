"""
GeoShield AI - Desktop Application
Standalone Windows executable
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GeoShield AI")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
