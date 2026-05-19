"""
Main Application Window
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLineEdit, QLabel, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
import os

from risk_engine import RiskEngine
from weather_api import WeatherAPI
from database import Database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoShield AI - Disaster Risk Analysis")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.risk_engine = RiskEngine()
        self.weather_api = WeatherAPI()
        self.database = Database()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left Panel - Controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=1)
        
        # Right Panel - Map
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=3)
        
    def create_left_panel(self):
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("🛡️ GeoShield AI")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #3b82f6;")
        layout.addWidget(title)
        
        # Search section
        search_label = QLabel("Search Location:")
        search_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter city name (e.g., Athens)")
        self.search_input.returnPressed.connect(self.search_location)
        layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 Analyze Risk")
        search_btn.clicked.connect(self.search_location)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        layout.addWidget(search_btn)
        
        # Results area
        results_label = QLabel("Risk Assessment Results:")
        results_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #1f1f1f;
                color: white;
                border: 1px solid #3b82f6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
            }
        """)
        layout.addWidget(self.results_text)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #10b981; margin-top: 10px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return panel
        
    def create_right_panel(self):
        """Create right map panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Map placeholder
        map_label = QLabel("Interactive Map")
        map_label.setStyleSheet("""
            QLabel {
                background-color: #0a0a0a;
                color: #3b82f6;
                font-size: 18px;
                padding: 20px;
                border: 2px solid #3b82f6;
                border-radius: 10px;
            }
        """)
        map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(map_label)
        
        # Instructions
        instructions = QLabel(
            "📍 Enter a city name in the search box\n"
            "🔍 Click 'Analyze Risk' to see results\n"
            "⚠️ View flood, fire, and landslide risks"
        )
        instructions.setStyleSheet("color: #a3a3a3; padding: 20px;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        return panel
        
    def search_location(self):
        """Search for location and analyze risk"""
        city = self.search_input.text().strip()
        
        if not city:
            QMessageBox.warning(self, "Input Error", "Please enter a city name")
            return
            
        self.status_label.setText(f"Analyzing {city}...")
        self.status_label.setStyleSheet("color: #f59e0b;")
        
        # Use QTimer to prevent UI freeze
        QTimer.singleShot(100, lambda: self.perform_analysis(city))
        
    def perform_analysis(self, city):
        """Perform risk analysis"""
        try:
            # Get weather data
            weather = self.weather_api.get_weather(city)
            
            if not weather:
                QMessageBox.critical(self, "Error", f"Could not fetch weather data for {city}")
                self.status_label.setText("Error")
                self.status_label.setStyleSheet("color: #ef4444;")
                return
            
            # Calculate risks
            risks = self.risk_engine.calculate_risks(
                temperature=weather['temperature'],
                humidity=weather['humidity'],
                wind_speed=weather['wind_speed'],
                precipitation=weather.get('precipitation', 0)
            )
            
            # Get historical events
            historical_count = self.database.count_events_near(city)
            
            # Display results
            self.display_results(city, weather, risks, historical_count)
            
            self.status_label.setText("Analysis Complete ✓")
            self.status_label.setStyleSheet("color: #10b981;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")
            self.status_label.setText("Error")
            self.status_label.setStyleSheet("color: #ef4444;")
            
    def display_results(self, city, weather, risks, historical_count):
        """Display analysis results"""
        
        def risk_color(level):
            colors = {'low': '🟢', 'moderate': '🟡', 'high': '🟠', 'critical': '🔴'}
            return colors.get(level, '⚪')
        
        result = f"""
═══════════════════════════════════════
  🛡️  GEOSHIELD AI - RISK REPORT
═══════════════════════════════════════

📍 LOCATION: {city.upper()}

🌤️  WEATHER CONDITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Temperature:  {weather['temperature']:.1f}°C
  Humidity:     {weather['humidity']}%
  Wind Speed:   {weather['wind_speed']:.1f} km/h
  Condition:    {weather.get('condition', 'N/A')}

⚠️  RISK ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  🌊 FLOOD RISK
     Score: {risks['flood']['score']:.1f}/100
     Level: {risk_color(risks['flood']['level'])} {risks['flood']['level'].upper()}
     
  🔥 WILDFIRE RISK
     Score: {risks['fire']['score']:.1f}/100
     Level: {risk_color(risks['fire']['level'])} {risks['fire']['level'].upper()}
     
  ⛰️  LANDSLIDE RISK
     Score: {risks['landslide']['score']:.1f}/100
     Level: {risk_color(risks['landslide']['level'])} {risks['landslide']['level'].upper()}

📊 OVERALL RISK: {risks['overall']:.1f}/100

📜 HISTORICAL DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Past disasters in region: {historical_count}

═══════════════════════════════════════
        """
        
        self.results_text.setPlainText(result)
