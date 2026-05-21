"""
Weather API — Open-Meteo geocoding and comprehensive meteorological datasets.
"""
import math
import statistics
from datetime import datetime

import requests


class WeatherAPI:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    def get_comprehensive(self, city: str) -> dict | None:
        """Full dataset for operational and scientific analysis."""
        try:
            geo = self._geocode(city)
            if not geo:
                return None

            params = {
                "latitude": geo["lat"],
                "longitude": geo["lon"],
                "current_weather": "true",
                "hourly": ",".join([
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "rain",
                    "windspeed_10m",
                    "windgusts_10m",
                    "cloudcover",
                    "surface_pressure",
                    "dewpoint_2m",
                ]),
                "daily": ",".join([
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "windspeed_10m_max",
                    "relative_humidity_2m_max",
                    "weathercode",
                ]),
                "forecast_days": 7,
                "timezone": "auto",
            }
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            current = data["current_weather"]
            hourly = data.get("hourly", {})
            daily = data.get("daily", {})

            display = geo.get("name", city)
            if geo.get("admin1"):
                display = f"{display}, {geo['admin1']}"
            if geo.get("country"):
                display = f"{display}, {geo['country']}"

            h_precip = _series(hourly, "precipitation", 24)
            h_humidity = _series(hourly, "relative_humidity_2m", 24)
            h_temp = _series(hourly, "temperature_2m", 24)
            h_wind = _series(hourly, "windspeed_10m", 24)
            h_gust = _series(hourly, "windgusts_10m", 24)
            h_pressure = _series(hourly, "surface_pressure", 24)
            h_cloud = _series(hourly, "cloudcover", 24)
            h_dew = _series(hourly, "dewpoint_2m", 24)

            precip_24h = sum(h_precip) if h_precip else 0.0
            humidity = statistics.mean(h_humidity) if h_humidity else 55.0
            temp = float(current["temperature"])
            wind = float(current["windspeed"])
            pressure = statistics.mean(h_pressure) if h_pressure else 1013.0
            cloud = statistics.mean(h_cloud) if h_cloud else 0.0
            dew = statistics.mean(h_dew) if h_dew else temp - 5

            hourly_rows = _build_hourly_rows(hourly, 48)

            daily_rows = []
            if daily.get("time"):
                for i, day in enumerate(daily["time"][:7]):
                    daily_rows.append({
                        "date": day,
                        "temp_max": _at(daily, "temperature_2m_max", i),
                        "temp_min": _at(daily, "temperature_2m_min", i),
                        "precip_sum": _at(daily, "precipitation_sum", i),
                        "wind_max": _at(daily, "windspeed_10m_max", i),
                        "humidity_max": _at(daily, "relative_humidity_2m_max", i),
                        "weathercode": int(_at(daily, "weathercode", i) or 0),
                        "condition": self._interpret_weather_code(
                            int(_at(daily, "weathercode", i) or 0)
                        ),
                    })

            return {
                "temperature": temp,
                "wind_speed": wind,
                "wind_gust": float(h_gust[0]) if h_gust else wind * 1.2,
                "humidity": float(humidity),
                "precipitation": float(precip_24h),
                "precipitation_mean_hourly": precip_24h / 24 if precip_24h else 0,
                "condition": self._interpret_weather_code(current["weathercode"]),
                "weathercode": int(current["weathercode"]),
                "lat": geo["lat"],
                "lon": geo["lon"],
                "elevation_m": geo.get("elevation"),
                "display_name": display,
                "country": geo.get("country", ""),
                "admin1": geo.get("admin1", ""),
                "timezone": data.get("timezone", "UTC"),
                "fetched_at": datetime.utcnow().isoformat() + "Z",
                "surface_pressure_hpa": float(pressure),
                "cloud_cover_pct": float(cloud),
                "dewpoint_c": float(dew),
                "heat_index_c": _heat_index(temp, humidity),
                "vapor_pressure_deficit_kpa": _vpd(temp, humidity),
                "fire_weather_index_proxy": _fwi_proxy(temp, humidity, wind, precip_24h),
                "hourly": hourly_rows,
                "daily": daily_rows,
                "hourly_stats": {
                    "temp_min": min(h_temp) if h_temp else temp,
                    "temp_max": max(h_temp) if h_temp else temp,
                    "temp_mean": statistics.mean(h_temp) if h_temp else temp,
                    "temp_std": statistics.pstdev(h_temp) if len(h_temp) > 1 else 0,
                    "humidity_min": min(h_humidity) if h_humidity else humidity,
                    "humidity_max": max(h_humidity) if h_humidity else humidity,
                    "precip_total_48h": sum(_series(hourly, "precipitation", 48)),
                    "wind_max": max(h_wind) if h_wind else wind,
                    "wind_mean": statistics.mean(h_wind) if h_wind else wind,
                },
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return None

    def get_weather(self, city: str) -> dict | None:
        """Backward-compatible summary payload."""
        full = self.get_comprehensive(city)
        if not full:
            return None
        return {k: full[k] for k in full if k not in ("hourly", "daily", "hourly_stats")}

    def _geocode(self, city: str) -> dict | None:
        try:
            params = {"name": city, "count": 1, "language": "en", "format": "json"}
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "results" not in data or not data["results"]:
                return None
            r = data["results"][0]
            return {
                "lat": r["latitude"],
                "lon": r["longitude"],
                "name": r.get("name", city),
                "country": r.get("country", ""),
                "admin1": r.get("admin1", ""),
                "elevation": r.get("elevation"),
            }
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

    def _interpret_weather_code(self, code: int) -> str:
        codes = {
            0: "Clear",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Rime fog",
            51: "Light drizzle",
            61: "Rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Snow",
            80: "Rain showers",
            95: "Thunderstorm",
        }
        return codes.get(code, "Variable")


def _series(hourly: dict, key: str, n: int) -> list[float]:
    vals = hourly.get(key, [])[:n]
    return [float(v) if v is not None else 0.0 for v in vals]


def _at(daily: dict, key: str, i: int):
    arr = daily.get(key, [])
    return arr[i] if i < len(arr) else None


def _build_hourly_rows(hourly: dict, n: int) -> list[dict]:
    times = hourly.get("time", [])[:n]
    rows = []
    for i, t in enumerate(times):
        rows.append({
            "time": t,
            "temperature": _at(hourly, "temperature_2m", i),
            "humidity": _at(hourly, "relative_humidity_2m", i),
            "precipitation": _at(hourly, "precipitation", i) or 0,
            "wind": _at(hourly, "windspeed_10m", i),
            "wind_gust": _at(hourly, "windgusts_10m", i),
            "pressure": _at(hourly, "surface_pressure", i),
            "cloud": _at(hourly, "cloudcover", i),
            "dewpoint": _at(hourly, "dewpoint_2m", i),
        })
    return rows


def _heat_index(temp_c: float, rh: float) -> float:
    if temp_c < 27:
        return temp_c
    t_f = temp_c * 9 / 5 + 32
    hi = (
        -42.379 + 2.04901523 * t_f + 10.14333127 * rh
        - 0.22475541 * t_f * rh - 0.00683783 * t_f ** 2
        - 0.05481717 * rh ** 2 + 0.00122874 * t_f ** 2 * rh
        + 0.00085282 * t_f * rh ** 2 - 0.00000199 * t_f ** 2 * rh ** 2
    )
    return round((hi - 32) * 5 / 9, 2)


def _vpd(temp_c: float, rh: float) -> float:
    es = 0.6108 * math.exp(17.27 * temp_c / (temp_c + 237.3))
    ea = es * rh / 100
    return round(max(es - ea, 0), 3)


def _fwi_proxy(temp: float, humidity: float, wind: float, precip: float) -> float:
    dryness = max(0, 100 - humidity) / 100
    temp_factor = min(temp / 40, 1.2)
    wind_factor = min(wind / 50, 1.0)
    precip_damp = max(0, 1 - precip / 30)
    return round(100 * dryness * temp_factor * wind_factor * precip_damp, 1)
