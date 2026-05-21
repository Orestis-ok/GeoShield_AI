"""
Scientific risk assessment — model decomposition, projections, and diagnostics.
"""
from config import MODEL_CODENAME, MODEL_VERSION


class ScienceEngine:
    WEIGHTS = {"flood": 0.35, "fire": 0.35, "landslide": 0.30}
    THRESHOLDS = {"low": 40, "high": 60, "critical": 75}

    def build_assessment(
        self,
        weather: dict,
        risks: dict,
        historical: list[dict],
    ) -> dict:
        breakdown = self._model_breakdown(weather, risks)
        predictions = self._multi_horizon_predictions(weather, risks)
        diagnostics = self._diagnostics(weather, risks, historical)
        correlations = self._variable_correlations(weather)
        return {
            "model_version": MODEL_VERSION,
            "model_codename": MODEL_CODENAME,
            "weights": self.WEIGHTS,
            "thresholds": self.THRESHOLDS,
            "breakdown": breakdown,
            "predictions": predictions,
            "diagnostics": diagnostics,
            "correlations": correlations,
            "methodology": self._methodology_text(),
        }

    def _model_breakdown(self, weather: dict, risks: dict) -> dict:
        t = weather["temperature"]
        h = weather["humidity"]
        w = weather["wind_speed"]
        p = weather.get("precipitation", 0)
        fwi = weather.get("fire_weather_index_proxy", 0)
        vpd = weather.get("vapor_pressure_deficit_kpa", 0)

        flood_factors = [
            ("Relative humidity", h, "%", self._humidity_flood_contrib(h)),
            ("24h precipitation", p, "mm", min(p * 3, 30)),
            ("Temperature modifier", t, "°C", 15 if t < 15 else 8 if t < 25 else 3),
        ]
        fire_factors = [
            ("Temperature", t, "°C", self._temp_fire_contrib(t)),
            ("Humidity (inverse)", h, "%", self._humidity_fire_contrib(h)),
            ("Wind speed", w, "km/h", self._wind_fire_contrib(w)),
            ("FWI proxy index", fwi, "idx", min(fwi * 0.15, 15)),
        ]
        slide_factors = [
            ("24h precipitation", p, "mm", self._precip_slide_contrib(p)),
            ("Wind speed", w, "km/h", self._wind_slide_contrib(w)),
            ("Saturation (RH>70%)", h, "%", 10 if h > 85 else 6 if h > 70 else 0),
        ]

        return {
            "flood": {
                "score": risks["flood"]["score"],
                "level": risks["flood"]["level"],
                "factors": flood_factors,
                "formula": "S_flood = f(RH) + min(3P,30) + f(T)",
            },
            "fire": {
                "score": risks["fire"]["score"],
                "level": risks["fire"]["level"],
                "factors": fire_factors,
                "formula": "S_fire = f(T) + f(RH⁻¹) + f(W) + 0.15·FWI",
            },
            "landslide": {
                "score": risks["landslide"]["score"],
                "level": risks["landslide"]["level"],
                "factors": slide_factors,
                "formula": "S_slide = f(P) + f(W) + f(saturation)",
            },
            "composite": {
                "score": risks["overall"],
                "level": risks.get("overall_level", "low"),
                "formula": (
                    f"Ψ = {self.WEIGHTS['flood']}·S_flood + "
                    f"{self.WEIGHTS['fire']}·S_fire + "
                    f"{self.WEIGHTS['landslide']}·S_slide"
                ),
            },
            "derived_indices": [
                ("Heat index", weather.get("heat_index_c"), "°C"),
                ("Dew point", weather.get("dewpoint_c"), "°C"),
                ("Vapor pressure deficit", vpd, "kPa"),
                ("FWI proxy", fwi, "0–100"),
                ("Surface pressure", weather.get("surface_pressure_hpa"), "hPa"),
                ("Cloud cover", weather.get("cloud_cover_pct"), "%"),
            ],
        }

    def _multi_horizon_predictions(self, weather: dict, risks: dict) -> list[dict]:
        daily = weather.get("daily", [])
        base = risks["overall"]
        horizons = []

        if daily:
            d1 = daily[0] if len(daily) > 0 else {}
            d3 = daily[2] if len(daily) > 2 else d1
            d7 = daily[6] if len(daily) > 6 else d1

            for label, day, hours, conf_base in [
                ("24-hour outlook", d1, 24, 0.82),
                ("72-hour outlook", d3, 72, 0.71),
                ("7-day outlook", d7, 168, 0.58),
            ]:
                precip = day.get("precip_sum") or 0
                tmax = day.get("temp_max") or weather["temperature"]
                wind = day.get("wind_max") or weather["wind_speed"]
                hum = day.get("humidity_max") or weather["humidity"]
                from risk_engine import RiskEngine

                re = RiskEngine()
                proj = re.calculate_risks(tmax, hum, wind, precip)
                delta = proj["overall"] - base
                horizons.append({
                    "horizon": label,
                    "hours": hours,
                    "projected_overall": proj["overall"],
                    "projected_level": proj["overall_level"],
                    "delta_from_current": round(delta, 1),
                    "flood": proj["flood"]["score"],
                    "fire": proj["fire"]["score"],
                    "landslide": proj["landslide"]["score"],
                    "confidence_pct": round(conf_base * 100 - abs(delta) * 0.15, 1),
                    "drivers": self._prediction_drivers(day, delta),
                })
        else:
            horizons.append({
                "horizon": "24-hour outlook",
                "hours": 24,
                "projected_overall": base,
                "projected_level": risks.get("overall_level", "low"),
                "delta_from_current": 0,
                "confidence_pct": 75,
                "drivers": ["Insufficient forecast grid — using current conditions"],
            })
        return horizons

    def _prediction_drivers(self, day: dict, delta: float) -> list[str]:
        drivers = []
        if (day.get("precip_sum") or 0) > 10:
            drivers.append("Elevated precipitation sum in forecast window")
        if (day.get("temp_max") or 0) > 32:
            drivers.append("Thermal stress above seasonal norm")
        if (day.get("wind_max") or 0) > 30:
            drivers.append("Wind field supports fire/landslide coupling")
        if not drivers:
            drivers.append("Stable synoptic pattern expected")
        if delta > 8:
            drivers.append(f"Net escalation of +{delta:.0f} composite points projected")
        elif delta < -8:
            drivers.append(f"Net mitigation of {delta:.0f} composite points projected")
        return drivers

    def _diagnostics(self, weather: dict, risks: dict, historical: list) -> dict:
        stats = weather.get("hourly_stats", {})
        hist_scores = [70 if h.get("severity") == "critical" else 55 for h in historical]
        archive_mean = sum(hist_scores) / len(hist_scores) if hist_scores else 40
        anomaly = risks["overall"] - archive_mean

        return {
            "archive_events": len(historical),
            "archive_baseline_score": round(archive_mean, 1),
            "composite_anomaly": round(anomaly, 1),
            "anomaly_interpretation": (
                "Above regional historical stress" if anomaly > 10
                else "Below regional historical stress" if anomaly < -10
                else "Within historical envelope"
            ),
            "data_quality": {
                "hourly_points": len(weather.get("hourly", [])),
                "forecast_days": len(weather.get("daily", [])),
                "elevation_available": weather.get("elevation_m") is not None,
            },
            "volatility": {
                "temperature_std_c": round(stats.get("temp_std", 0), 2),
                "precip_48h_mm": round(stats.get("precip_total_48h", 0), 2),
                "wind_range_kmh": round(
                    (stats.get("wind_max", 0) - stats.get("wind_mean", 0)), 2
                ),
            },
            "uncertainty_band": {
                "overall_low": max(0, risks["overall"] - 8),
                "overall_high": min(100, risks["overall"] + 8),
                "note": "±8 pts reflects parameter uncertainty in empirical model",
            },
        }

    def _variable_correlations(self, weather: dict) -> list[dict]:
        hourly = weather.get("hourly", [])[:24]
        if len(hourly) < 6:
            return []
        temps = [h["temperature"] or 0 for h in hourly]
        precs = [h["precipitation"] or 0 for h in hourly]
        winds = [h["wind"] or 0 for h in hourly]
        hums = [h["humidity"] or 0 for h in hourly]
        return [
            {"pair": "Temperature ↔ Humidity", "r": _pearson(temps, hums)},
            {"pair": "Precipitation ↔ Humidity", "r": _pearson(precs, hums)},
            {"pair": "Wind ↔ Temperature", "r": _pearson(winds, temps)},
            {"pair": "Precipitation ↔ Wind", "r": _pearson(precs, winds)},
        ]

    def _methodology_text(self) -> str:
        return f"""GEOSHIELD SCIENTIFIC METHODOLOGY — {MODEL_VERSION} ({MODEL_CODENAME})

1. DATA INGESTION
   Meteorological fields are sourced from Open-Meteo (ECMWF/NOAA blended gridded products).
   Hourly resolution: temperature, relative humidity, precipitation, wind, gusts, cloud cover,
   surface pressure, dew point. Daily aggregates provide 7-day deterministic forecast.

2. HAZARD SCORING (EMPIRICAL COMPOSITE)
   Flood (S_flood): humidity saturation + precipitation accumulation + temperature modifier.
   Wildfire (S_fire): thermal load + inverse humidity + wind-driven spread + FWI proxy.
   Landslide (S_slide): antecedent rainfall + wind stress + soil saturation proxy.

3. COMPOSITE INDEX
   Ψ = 0.35·S_flood + 0.35·S_fire + 0.30·S_slide  (bounded 0–100)
   Classification: LOW <40 | MODERATE 40–59 | HIGH 60–74 | CRITICAL ≥75

4. PROJECTIONS
   Multi-horizon outlook applies daily forecast extrema through the same scoring functions.
   Confidence decays with lead time (24h: ~82%, 72h: ~71%, 7d: ~58% baseline).

5. DIAGNOSTICS
   Archive anomaly compares Ψ against curated disaster-severity baseline for the region.
   Hourly correlations (Pearson r) expose coupling between drivers for expert review.

6. LIMITATIONS
   This system provides decision-support indices, not certified probabilistic forecasts.
   Validate against national hydrometeorological services before life-safety decisions.

Author: Orestis Kerkines · GeoShield Pro Research Stack
"""

    def _humidity_flood_contrib(self, h):
        if h > 80: return 35
        if h > 65: return 25
        if h > 50: return 15
        return 5

    def _temp_fire_contrib(self, t):
        if t > 35: return 40
        if t > 30: return 30
        if t > 25: return 20
        if t > 20: return 10
        return 0

    def _humidity_fire_contrib(self, h):
        if h < 20: return 30
        if h < 35: return 25
        if h < 50: return 15
        return 5

    def _wind_fire_contrib(self, w):
        if w > 40: return 20
        if w > 25: return 15
        if w > 15: return 10
        return 3

    def _precip_slide_contrib(self, p):
        if p > 50: return 45
        if p > 25: return 35
        if p > 10: return 25
        if p > 5: return 15
        return 5

    def _wind_slide_contrib(self, w):
        if w > 50: return 20
        if w > 30: return 15
        if w > 20: return 10
        return 3


def _pearson(x: list, y: list) -> float:
    n = min(len(x), len(y))
    if n < 3:
        return 0.0
    mx, my = sum(x) / n, sum(y) / n
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    den = (sum((x[i] - mx) ** 2 for i in range(n)) * sum((y[i] - my) ** 2 for i in range(n))) ** 0.5
    return round(num / den, 3) if den else 0.0
