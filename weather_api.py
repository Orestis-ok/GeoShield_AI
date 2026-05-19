"""
Weather API Integration
"""
import requests


class WeatherAPI:
    def __init__(self):
        # Χρησιμοποιούμε Open-Meteo (δωρεάν, χωρίς API key)
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    
    def get_weather(self, city):
        """Get weather data for city"""
        try:
            # First, get coordinates
            coords = self._geocode(city)
            if not coords:
                return None
            
            # Then get weather
            params = {
                'latitude': coords['lat'],
                'longitude': coords['lon'],
                'current_weather': 'true',
                'hourly': 'precipitation'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data['current_weather']
            
            # Get precipitation from hourly data
            precip = 0
            if 'hourly' in data and 'precipitation' in data['hourly']:
                precip = sum(data['hourly']['precipitation'][:24]) / 24
            
            return {
                'temperature': current['temperature'],
                'wind_speed': current['windspeed'],
                'humidity': 65,  # Estimate (Open-Meteo doesn't provide this)
                'precipitation': precip,
                'condition': self._interpret_weather_code(current['weathercode'])
            }
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    def _geocode(self, city):
        """Convert city name to coordinates"""
        try:
            params = {'name': city, 'count': 1, 'language': 'en', 'format': 'json'}
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                return {
                    'lat': result['latitude'],
                    'lon': result['longitude']
                }
            return None
            
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
    
    def _interpret_weather_code(self, code):
        """Interpret WMO weather code"""
        codes = {
            0: 'Clear',
            1: 'Mainly Clear',
            2: 'Partly Cloudy',
            3: 'Overcast',
            45: 'Foggy',
            48: 'Foggy',
            51: 'Light Drizzle',
            61: 'Rain',
            80: 'Rain Showers',
            95: 'Thunderstorm'
        }
        return codes.get(code, 'Unknown')
