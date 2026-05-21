"""Background workers for non-blocking API calls."""
from PyQt6.QtCore import QThread, pyqtSignal

from database import Database
from risk_engine import RiskEngine
from weather_api import WeatherAPI


class AnalysisWorker(QThread):
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, city: str, user_id: int | None = None):
        super().__init__()
        self.city = city
        self.user_id = user_id
        self._weather = WeatherAPI()
        self._risk = RiskEngine()
        self._db = Database()

    def run(self):
        try:
            weather = self._weather.get_weather(self.city)
            if not weather:
                self.failed.emit(
                    f'Could not retrieve weather data for "{self.city}". '
                    "Check the location name and your internet connection."
                )
                return

            risks = self._risk.calculate_risks(
                temperature=weather["temperature"],
                humidity=weather["humidity"],
                wind_speed=weather["wind_speed"],
                precipitation=weather.get("precipitation", 0),
            )
            recommendations = self._risk.get_recommendations(risks)
            historical = self._db.get_disasters_for_city(self.city)
            historical_count = len(historical)

            if self.user_id:
                self._db.save_analysis(
                    self.user_id,
                    self.city,
                    weather,
                    risks,
                )

            self.finished.emit(
                {
                    "city": self.city,
                    "weather": weather,
                    "risks": risks,
                    "recommendations": recommendations,
                    "historical": historical,
                    "historical_count": historical_count,
                }
            )
        except Exception as e:
            self.failed.emit(str(e))
