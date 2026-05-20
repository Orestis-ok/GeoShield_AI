"""
Risk Calculation Engine
"""

class RiskEngine:
    def calculate_risks(self, temperature, humidity, wind_speed, precipitation=0):
        """Calculate all risk scores"""
        
        flood_score = self._calculate_flood(temperature, humidity, precipitation)
        fire_score = self._calculate_fire(temperature, humidity, wind_speed)
        landslide_score = self._calculate_landslide(precipitation, wind_speed, humidity)
        
        overall = (flood_score * 0.35 + fire_score * 0.35 + landslide_score * 0.30)
        
        return {
            'flood': {'score': flood_score, 'level': self._get_level(flood_score)},
            'fire': {'score': fire_score, 'level': self._get_level(fire_score)},
            'landslide': {'score': landslide_score, 'level': self._get_level(landslide_score)},
            'overall': overall
        }
    
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
