import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json

# NASA POWER API Integration
class NASADataFetcher:
    """Fetches real NASA climate data"""
    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    def __init__(self):
        self.cache = {}
    
    def get_climate_data(self, lat, lon, start_date, end_date):
        """Fetch temperature, precipitation, soil moisture data"""
        # Parameters: T2M (temp), PRECTOTCORR (precip), GWETROOT (soil moisture)
        params = {
            'parameters': 'T2M,PRECTOTCORR,GWETROOT,ALLSKY_SFC_SW_DWN',
            'community': 'AG',
            'longitude': lon,
            'latitude': lat,
            'start': start_date.strftime('%Y%m%d'),
            'end': end_date.strftime('%Y%m%d'),
            'format': 'JSON'
        }
        
        cache_key = f"{lat}_{lon}_{start_date}_{end_date}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.cache[cache_key] = data
            return data
        except Exception as e:
            st.error(f"API Error: {e}. Using sample data.")
            return self._get_sample_data()
    
    def _get_sample_data(self):
        """Fallback sample data if API fails"""
        dates = pd.date_range(end=datetime.now(), periods=30)
        return {
            'properties': {
                'parameter': {
                    'T2M': {date.strftime('%Y%m%d'): 20 + i % 10 for i, date in enumerate(dates)},
                    'PRECTOTCORR': {date.strftime('%Y%m%d'): 2.5 + (i % 5) for i, date in enumerate(dates)},
                    'GWETROOT': {date.strftime('%Y%m%d'): 0.3 + (i % 3) * 0.1 for i, date in enumerate(dates)},
                    'ALLSKY_SFC_SW_DWN': {date.strftime('%Y%m%d'): 5.5 for i, date in enumerate(dates)}
                }
            }
        }

# Game Logic Engine
class FarmingSimulator:
    """Core game logic and decision processing"""
    
    def __init__(self, crop_type, location):
        self.crop_type = crop_type
        self.location = location
        self.nasa_data = None
        self.decisions = {
            'irrigation': 0,
            'fertilizer': 0,
            'planting_date': None
        }
        self.crop_health = 100
        self.water_usage = 0
        self.fertilizer_cost = 0
        
    def load_nasa_data(self, nasa_fetcher):
        """Load 30 days of NASA data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        self.nasa_data = nasa_fetcher.get_climate_data(
            self.location['lat'],
            self.location['lon'],
            start_date,
            end_date
        )
    
    def analyze_conditions(self):
        """Analyze NASA data for farming recommendations"""
        if not self.nasa_data:
            return {}
        
        params = self.nasa_data['properties']['parameter']
        
        # Calculate averages
        temps = list(params['T2M'].values())
        precip = list(params['PRECTOTCORR'].values())
        soil_moisture = list(params['GWETROOT'].values())
        
        avg_temp = sum(temps) / len(temps)
        avg_precip = sum(precip) / len(precip)
        avg_soil = sum(soil_moisture) / len(soil_moisture)
        
        return {
            'avg_temperature': round(avg_temp, 1),
            'avg_precipitation': round(avg_precip, 2),
            'avg_soil_moisture': round(avg_soil, 2),
            'recommendation': self._generate_recommendation(avg_temp, avg_precip, avg_soil)
        }
    
    def _generate_recommendation(self, temp, precip, soil):
        """Generate farming recommendations based on data"""
        recommendations = []
        
        if soil < 0.3:
            recommendations.append("⚠️ Low soil moisture - consider irrigation")
        if precip < 2.0:
            recommendations.append("☀️ Low rainfall - monitor water needs")
        if temp > 30:
            recommendations.append("🌡️ High temperatures - crops may need extra water")
        if soil > 0.5 and precip > 5:
            recommendations.append("💧 High moisture - reduce irrigation to avoid overwatering")
            
        return recommendations if recommendations else ["✅ Conditions are optimal"]
    
    def make_decision(self, decision_type, value):
        """Record player decision"""
        self.decisions[decision_type] = value
    
    def calculate_yield(self):
        """Calculate crop yield based on decisions and NASA data"""
        if not self.nasa_data:
            return 0, "No data available"
        
        analysis = self.analyze_conditions()
        base_yield = 100  # Base yield percentage
        
        # Factor in irrigation decisions
        soil_moisture = analysis['avg_soil_moisture']
        irrigation = self.decisions['irrigation']
        
        # Optimal soil moisture: 0.3-0.5
        if soil_moisture < 0.3:
            if irrigation >= 50:  # Player compensated with irrigation
                base_yield += 10
            else:
                base_yield -= 30  # Crop suffered from drought
        elif soil_moisture > 0.5:
            if irrigation <= 30:  # Player wisely reduced irrigation
                base_yield += 15
            else:
                base_yield -= 20  # Overwatering
        
        # Factor in fertilizer
        fertilizer = self.decisions['fertilizer']
        if 40 <= fertilizer <= 60:  # Optimal range
            base_yield += 20
        elif fertilizer > 80:
            base_yield -= 10  # Over-fertilization
        elif fertilizer < 20:
            base_yield -= 15  # Under-fertilization
        
        # Calculate costs
        self.water_usage = irrigation * 10  # liters per unit
        self.fertilizer_cost = fertilizer * 5  # $ per unit
        
        # Generate feedback
        feedback = self._generate_feedback(base_yield, analysis)
        
        return max(0, min(150, base_yield)), feedback
    
    def _generate_feedback(self, yield_pct, analysis):
        """Generate educational feedback"""
        feedback = []
        
        if yield_pct > 110:
            feedback.append("🎉 Excellent! You used NASA data effectively!")
        elif yield_pct > 90:
            feedback.append("👍 Good job! Your decisions aligned with the data.")
        else:
            feedback.append("📚 Review the NASA data - it shows important patterns.")
        
        feedback.append(f"Avg Temperature: {analysis['avg_temperature']}°C")
        feedback.append(f"Avg Soil Moisture: {analysis['avg_soil_moisture']}")
        
        return "\n".join(feedback)

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = None
    st.session_state.nasa_fetcher = NASADataFetcher()

def start_new_game():
    """Initialize new game"""
    st.session_state.game_state = FarmingSimulator(
        crop_type='wheat',
        location={'lat': 37.5, 'lon': -95.5, 'name': 'Kansas, USA'}
    )
    st.session_state.game_state.load_nasa_data(st.session_state.nasa_fetcher)

# Export for other modules
__all__ = ['FarmingSimulator', 'NASADataFetcher', 'start_new_game']
