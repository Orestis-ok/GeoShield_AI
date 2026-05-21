"""
Risk Calculation Engine
"""

class RiskEngine:
    def calculate_risks(self, temperature, humidity, wind_speed, precipitation=0):
        """Calculate all risk scores"""
        
        flood_score = self._calculate_flood(temperature, humidity, precipitation)
        fire_score = self._calculate_fire(temperature, humidity, wind_speed)
        landslide_score = self._calculate_landslide(precipitation, wind_speed, humidity)
        
        overall = flood_score * 0.35 + fire_score * 0.35 + landslide_score * 0.30

        return {
            "flood": {"score": flood_score, "level": self._get_level(flood_score)},
            "fire": {"score": fire_score, "level": self._get_level(fire_score)},
            "landslide": {
                "score": landslide_score,
                "level": self._get_level(landslide_score),
            },
            "overall": overall,
            "overall_level": self._get_level(overall),
        }

    def get_recommendations(self, risks: dict) -> dict[str, str]:
        """Operational guidance keyed by hazard."""
        recs = {}
        flood = risks["flood"]
        fire = risks["fire"]
        slide = risks["landslide"]
        overall = risks.get("overall_level", self.get_level(risks["overall"]))

        if flood["level"] in ("high", "critical"):
            recs["flood"] = (
                "Activate flood monitoring: review drainage, pre-position pumps, "
                "and brief field teams on evacuation routes for low-lying assets."
            )
        elif flood["level"] == "moderate":
            recs["flood"] = (
                "Increase precipitation surveillance; inspect retention basins "
                "and confirm emergency contacts for watershed stakeholders."
            )
        else:
            recs["flood"] = (
                "Flood indicators within normal bounds; maintain seasonal "
                "readiness checks and hydrology dashboard reviews."
            )

        if fire["level"] in ("high", "critical"):
            recs["fire"] = (
                "Elevate wildfire posture: restrict hot work, stage fire "
                "suppression resources, and monitor wind shifts hourly."
            )
        elif fire["level"] == "moderate":
            recs["fire"] = (
                "Dryness and wind support elevated ignition risk; audit "
                "vegetation clearance and verify mutual-aid agreements."
            )
        else:
            recs["fire"] = (
                "Wildfire potential subdued; continue standard fuel-management "
                "and public communication protocols."
            )

        if slide["level"] in ("high", "critical"):
            recs["landslide"] = (
                "Slope instability likely: geotechnical inspection recommended "
                "for cut slopes, retaining walls, and transport corridors."
            )
        elif slide["level"] == "moderate":
            recs["landslide"] = (
                "Rainfall stress on slopes warrants increased patrols and "
                "temporary restrictions on heavy equipment near embankments."
            )
        else:
            recs["landslide"] = (
                "Landslide indicators stable; document baseline conditions "
                "for seasonal comparison."
            )

        if overall in ("high", "critical"):
            recs["overall"] = (
                "Composite risk is ELEVATED — convene operations briefing, "
                "validate continuity plans, and enable stakeholder alert channel."
            )
        elif overall == "moderate":
            recs["overall"] = (
                "Regional conditions warrant heightened awareness; schedule "
                "a 24-hour reassessment cycle until scores normalize."
            )
        else:
            recs["overall"] = (
                "Portfolio risk within acceptable planning thresholds; "
                "continue routine monitoring cadence."
            )
        return recs
    
    def _calculate_flood(self, temp, humidity, precip):
        """Calculate flood risk"""
        score = 0.0
        
        if humidity > 80:
            score += 35
        elif humidity > 65:
            score += 25
        elif humidity > 50:
            score += 15
        else:
            score += 5
        
        score += min(precip * 3, 30)
        
        if temp < 15:
            score += 15
        elif temp < 25:
            score += 8
        else:
            score += 3
        
        return min(score, 100)
    
    def _calculate_fire(self, temp, humidity, wind):
        """Calculate fire risk"""
        score = 0.0
        
        if temp > 35:
            score += 40
        elif temp > 30:
            score += 30
        elif temp > 25:
            score += 20
        elif temp > 20:
            score += 10
        
        if humidity < 20:
            score += 30
        elif humidity < 35:
            score += 25
        elif humidity < 50:
            score += 15
        else:
            score += 5
        
        if wind > 40:
            score += 20
        elif wind > 25:
            score += 15
        elif wind > 15:
            score += 10
        else:
            score += 3
        
        return min(score, 100)
    
    def _calculate_landslide(self, precip, wind, humidity):
        """Calculate landslide risk"""
        score = 0.0
        
        if precip > 50:
            score += 45
        elif precip > 25:
            score += 35
        elif precip > 10:
            score += 25
        elif precip > 5:
            score += 15
        else:
            score += 5
        
        if wind > 50:
            score += 20
        elif wind > 30:
            score += 15
        elif wind > 20:
            score += 10
        else:
            score += 3
        
        if humidity > 85:
            score += 10
        elif humidity > 70:
            score += 6
        
        return min(score, 100)
    
    def get_level(self, score):
        """Convert score to risk level"""
        if score >= 75:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'moderate'
        else:
            return 'low'

    def _get_level(self, score):
        return self.get_level(score)
