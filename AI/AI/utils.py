"""
utils.py - Helper utilities for Food Supply Chain Loss Predictor
"""

import math
import pickle
import json
import os
import re
import requests
import functools
import numpy as np
import colorsys
from typing import Any, Dict, List, Tuple
from PIL import Image, ImageFilter, ImageStat

# ─── Food type encoding map (Numerical Encoding) ──────────────────────────────────
# Categorized exactly as requested by USER

def get_foods_by_category(category_name: str) -> List[str]:
    """Return foods list for given category."""
    return FOOD_CATEGORIES.get(category_name, [])

FOOD_TYPE_MAP = {
    # Fruits
    'Apple': 0, 'Banana': 1, 'Mango': 2, 'Orange': 3, 'Grapes': 4,
    'Papaya': 5, 'Pineapple': 6, 'Guava': 7, 'Watermelon': 8,
    # Vegetables
    'Potato': 9, 'Tomato': 10, 'Onion': 11, 'Carrot': 12, 'Cabbage': 13,
    'Cauliflower': 14, 'Brinjal': 15, 'Okra': 16, 'Spinach': 17,
    # Grains
    'Rice': 18, 'Wheat': 19, 'Maize': 20, 'Barley': 21, 'Lentil': 22,
    'Chickpea': 23, 'Green gram': 24,
    # Dairy
    'Milk': 25, 'Butter': 26, 'Cheese': 27, 'Paneer': 28, 'Egg': 29,
    'Fish': 30, 'Chicken': 31,
    # Frozen
    'Frozen peas': 32, 'Frozen corn': 33, 'Ice cream': 34,
    'Ready meals': 35, 'Meat products': 36,
}

FOOD_CATEGORIES = {
    'Fruits': ['Apple','Banana','Mango','Orange','Grapes','Papaya','Pineapple','Guava','Watermelon'],
    'Vegetables': ['Potato','Tomato','Onion','Carrot','Cabbage','Cauliflower','Brinjal','Okra','Spinach'],
    'Grains': ['Rice','Wheat','Maize','Barley','Lentil','Chickpea','Green gram'],
    'Dairy': ['Milk','Butter','Cheese','Paneer','Egg','Fish','Chicken'],
    'Frozen': ['Frozen peas','Frozen corn','Ice cream','Ready meals','Meat products'],
}

RISK_LABELS = {0: 'Low', 1: 'Moderate', 2: 'High'}
RISK_COLORS = {'Low': 'success', 'Moderate': 'warning', 'High': 'danger'}


def validate_email(email: str) -> bool:
    """Validate email with regex."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and '@' in email


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two geo-coordinates."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a)), 2)


def get_midpoint(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, float]:
    """Return geographic midpoint."""
    return ((lat1 + lat2) / 2, (lon1 + lon2) / 2)


def load_model() -> Tuple[Any, Any]:
    """Load trained model and scaler."""
    with open('models/model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler


def predict_risk(temperature: float, humidity: float, rainfall: float, transit_time: float,
                  storage_duration: float, food_type_name: str) -> Dict[str, Any]:
    """Run ML prediction and return structured result."""
    try:
        model, scaler = load_model()
        food_enc = FOOD_TYPE_MAP.get(food_type_name, 0)
        features = np.array([[temperature, humidity, rainfall,
                               transit_time, storage_duration, food_enc]])
        scaled = scaler.transform(features)
        proba = model.predict_proba(scaled)[0]
        label_idx = int(np.argmax(proba))
        risk = RISK_LABELS[label_idx]
        confidence = round(float(proba[label_idx]) * 100, 1)

        # Estimate loss percentage
        base_losses = [5, 20, 50]
        loss_pct = round(sum(p * l for p, l in zip(proba, base_losses)), 1)

        return {
            'risk_level': risk,
            'risk_index': label_idx,
            'confidence': confidence,
            'loss_percentage': loss_pct,
            'probabilities': {
                'Low': round(float(proba[0]) * 100, 1),
                'Moderate': round(float(proba[1]) * 100, 1),
                'High': round(float(proba[2]) * 100, 1),
            }
        }
    except Exception as e:
        print(f"[ERROR] predict_risk: {str(e)}")
        # Fallback to heuristic if model fails
        return {
            'risk_level': 'Moderate',
            'risk_index': 1,
            'confidence': 0.0,
            'loss_percentage': 25.0,
            'probabilities': {'Low': 33, 'Moderate': 33, 'High': 33}
        }


def generate_routes(src_lat: float, src_lon: float, dst_lat: float, dst_lon: float, risk_level: str, transit_time: float) -> List[Dict[str, Any]]:
    """Generate 3 route options w/ comparison. Best=green polyline. Fallback simulated."""
    base_dist = haversine(src_lat, src_lon, dst_lat, dst_lon)
    risk_penalty = {'Low': 0, 'Moderate': 10, 'High': 25}.get(risk_level, 10)
    
    # Route profiles (for future OSRM)
    route_profiles = [
        {'name': 'Optimal (Best)', 'dist_mult': 1.0, 'time_mult': 1.0, 'score_base': 100, 'color': 'green'},
        {'name': 'Alternate', 'dist_mult': 1.15, 'time_mult': 1.2, 'score_base': 85, 'color': 'orange'},
        {'name': 'Risky', 'dist_mult': 0.9, 'time_mult': 0.85, 'score_base': 60, 'color': 'red'}
    ]
    
    routes = []
    for i, profile in enumerate(route_profiles):
        waypoints = [
            [src_lat, src_lon],
            [(src_lat + dst_lat)/2 + (0.1 if i==1 else -0.1 if i==2 else 0), (src_lon + dst_lon)/2 + (0.2 if i==1 else -0.2 if i==2 else 0)],
            [dst_lat, dst_lon]
        ]
        routes.append({
            'name': profile['name'],
            'color': profile['color'],
            'distance': round(base_dist * profile['dist_mult'], 1),
            'estimated_time': round(transit_time * profile['time_mult'], 1),
            'score': max(0, profile['score_base'] - risk_penalty),
            # Provide both keys used across templates: 'coords' (older) and 'waypoints' (newer)
            'coords': waypoints,
            'waypoints': waypoints,
            'label': f"Score: {profile['score_base']}% {'(RECOMMENDED)' if i==0 else ''}"
        })
    
    return routes


def get_vehicle_recommendations(food_type: str) -> Dict[str, Any]:
    """Recommend best vehicle + comparison for food type."""
    food_enc = FOOD_TYPE_MAP.get(food_type, 0)
    
    # Vehicle options w/perishability scores (0-100, higher=better)
    options = [
        {'name': 'Refrigerated Truck', 'cost': 'High', 'perishable_score': 95, 'dry_score': 40},
        {'name': 'Ventilated Truck', 'cost': 'Medium', 'perishable_score': 80, 'dry_score': 70},
        {'name': 'Open Truck', 'cost': 'Low', 'perishable_score': 30, 'dry_score': 90}
    ]
    
    # Score based on food
    if food_enc in [25,26,27,28,29,30,31,32,33,34,35,36]:  # Perishables
        for opt in options:
            opt['total_score'] = opt['perishable_score']
    elif food_enc in [0,1,2,3,4,5,6,7,8,10,13,14,15,16,17]:  # Fruits/Veg
        for opt in options:
            opt['total_score'] = (opt['perishable_score'] + opt['dry_score']) / 2
    else:  # Grains/Dry
        for opt in options:
            opt['total_score'] = opt['dry_score']
    
    # Sort by score, return top 3
    options.sort(key=lambda x: x['total_score'], reverse=True)
    return {
        'best': options[0],
        'alternates': options[1:],
        'comparison': options
    }


def get_safety_recommendations(risk_level: str, food_type: str, temperature: float) -> List[str]:
    """Safety recommendations based on risk/food/weather."""
    recs = []
    
    if risk_level == 'High':
        recs.extend([
            'Emergency kit: Fire extinguisher, first aid, spare tires',
            'Two drivers for long hauls (>8hrs)',
            'GPS tracking enabled - share live location'
        ])
    elif risk_level == 'Moderate':
        recs.append('Carry backup cooling packs and temperature logger')
    
    # Food-specific
    if 'Milk' in food_type or 'Fish' in food_type or 'Chicken' in food_type:
        recs.extend(['PPE: Insulated gloves, spill containment kit', 'Leak-proof containers mandatory'])
    elif 'Banana' in food_type or 'Tomato' in food_type:
        recs.append('Avoid stacking - use padded dividers to prevent bruising')
    
    if temperature > 35:
        recs.append('Hydration: Carry 10L water/driver/shift. Heat stroke protocol ready')
    
    recs.append('General: Speed <80km/h, rest every 4hrs, no phone use while driving')
    return recs


def get_simulated_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Return simulated weather data based on lat/lon."""
    import random
    random.seed(int(abs(lat * lon) * 100) % 1000)
    temp = round(random.uniform(18, 42), 1)
    humidity = round(random.uniform(30, 90), 1)
    conditions = random.choice(['Clear', 'Partly Cloudy', 'Overcast', 'Light Rain', 'Heavy Rain'])
    return {'temperature': temp, 'humidity': humidity, 'condition': conditions}


def fetch_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch weather using OpenWeather API if available; otherwise simulated."""
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    if api_key:
        try:
            url = 'https://api.openweathermap.org/data/2.5/weather'
            params = {'lat': lat, 'lon': lon, 'units': 'metric', 'appid': api_key}
            response = requests.get(url, params=params, timeout=6)
            response.raise_for_status()
            payload = response.json()
            return {
                'temperature': round(payload['main']['temp'], 1),
                'humidity': round(payload['main']['humidity'], 1),
                'condition': payload['weather'][0]['main']
            }
        except Exception:
            pass
    return get_simulated_weather(lat, lon)


def load_markets() -> List[Dict[str, Any]]:
    """Load market definitions from data/markets.json."""
    markets_file = os.path.join('data', 'markets.json')
    if not os.path.exists(markets_file):
        return []
    try:
        with open(markets_file, 'r', encoding='utf-8') as fp:
            return json.load(fp)
    except Exception:
        return []


def find_nearest_market(lat: float, lon: float) -> Tuple[Dict[str, Any] | None, float]:
    """Return the nearest mandi market for a coordinate pair."""
    markets = load_markets()
    if not markets:
        return None, 0.0
    nearest = min(markets, key=lambda m: haversine(lat, lon, m['lat'], m['lon']))
    return nearest, haversine(lat, lon, nearest['lat'], nearest['lon'])


# ─── ADVANCED FEATURE: Shelf-Life Prediction ──────────────────────────────────
@functools.lru_cache(maxsize=128)
def predict_shelf_life(food_type: str, temperature: float, humidity: float, storage_duration: float) -> Dict[str, Any]:
    """Predict remaining shelf-life in hours/days."""
    food_enc = FOOD_TYPE_MAP.get(food_type, 0)
    
    # Base shelf life (hours) by category
    base_shelf_life = {
        # Fruits (encoded 0-8)
        0: 120, 1: 96, 2: 240, 3: 168, 4: 144, 5: 240, 6: 360, 7: 336, 8: 240,
        # Vegetables (9-17)
        9: 504, 10: 168, 11: 504, 12: 336, 13: 336, 14: 240, 15: 240, 16: 120, 17: 72,
        # Grains (18-24)
        18: 8760, 19: 8760, 20: 8760, 21: 8760, 22: 4320, 23: 4320, 24: 2880,
        # Dairy (25-31)
        25: 72, 26: 504, 27: 2160, 28: 240, 29: 336, 30: 24, 31: 72,
        # Frozen (32-36)
        32: 2160, 33: 2160, 34: 1440, 35: 720, 36: 720
    }
    
    shelf_life = base_shelf_life.get(food_enc, 240)
    
    # Adjust based on temperature
    if temperature > 30:
        shelf_life *= 0.5
    elif temperature > 20:
        shelf_life *= 0.75
    elif temperature < 5:
        shelf_life *= 1.2
    
    # Adjust based on humidity
    if humidity > 80:
        shelf_life *= 0.6
    elif humidity > 65:
        shelf_life *= 0.8
    
    # Account for storage duration
    remaining = max(0, shelf_life - (storage_duration * 24))
    
    return {
        'total_shelf_life_hours': round(shelf_life, 1),
        'remaining_hours': round(remaining, 1),
        'remaining_days': round(remaining / 24, 1),
        'status': 'Fresh' if remaining > shelf_life * 0.7 else 'Degrading' if remaining > shelf_life * 0.3 else 'Critical'
    }


# ─── ADVANCED FEATURE: Spoilage Timeline ──────────────────────────────────────
@functools.lru_cache(maxsize=128)
def generate_spoilage_timeline(food_type: str, temperature: float, humidity: float, storage_duration: float) -> Dict[str, Any]:
    """Generate spoilage stages timeline for visualization."""
    shelf_life_data = predict_shelf_life(food_type, temperature, humidity, storage_duration)
    total_hours = shelf_life_data['total_shelf_life_hours']
    current_hours = storage_duration * 24
    
    stages = [
        {
            'stage': 'Fresh',
            'start': 0,
            'end': total_hours * 0.5,
            'color': '#22c55e',
            'icon': '✓',
            'description': 'Optimal condition for consumption',
            'is_active': current_hours < (total_hours * 0.5)
        },
        {
            'stage': 'Degrading',
            'start': total_hours * 0.5,
            'end': total_hours * 0.8,
            'color': '#eab308',
            'icon': '⚠',
            'description': 'Quality declining, consume soon',
            'is_active': (total_hours * 0.5) <= current_hours < (total_hours * 0.8)
        },
        {
            'stage': 'High Risk',
            'start': total_hours * 0.8,
            'end': total_hours * 0.95,
            'color': '#f59e0b',
            'icon': '!',
            'description': 'Approaching expiration, careful inspection needed',
            'is_active': (total_hours * 0.8) <= current_hours < (total_hours * 0.95)
        },
        {
            'stage': 'Spoiled',
            'start': total_hours * 0.95,
            'end': total_hours,
            'color': '#ef4444',
            'icon': '✗',
            'description': 'Not safe for consumption',
            'is_active': current_hours >= (total_hours * 0.95)
        }
    ]
    
    return {
        'stages': stages,
        'current_stage': next((s['stage'] for s in stages if s['is_active']), 'Unknown'),
        'progress_percent': round((current_hours / total_hours) * 100, 1) if total_hours > 0 else 0,
        'timeline_data': [
            {'label': s['stage'], 'hours': round(s['end'] - s['start'], 1), 'color': s['color']}
            for s in stages
        ]
    }


# ─── ADVANCED FEATURE: Delay Prediction ────────────────────────────────────────
@functools.lru_cache(maxsize=128)
def predict_delay(distance: float, weather_condition: str, transit_time: float, temperature: float, humidity: float) -> Dict[str, Any]:
    """Predict transportation delay probability and time."""
    base_delay = 0.0
    
    # Distance factor (longer routes more risk)
    if distance > 500:
        base_delay += 2.5
    elif distance > 200:
        base_delay += 1.5
    elif distance > 100:
        base_delay += 0.8
    
    # Weather factor
    weather_delay_factor = {
        'Clear': 0,
        'Partly Cloudy': 0.3,
        'Overcast': 0.6,
        'Light Rain': 1.5,
        'Heavy Rain': 3.0
    }
    base_delay += weather_delay_factor.get(weather_condition, 0)
    
    # Traffic/route complexity factor
    traffic_factor = np.random.uniform(0, 2)
    base_delay += traffic_factor
    
    # Temperature impact (extreme temperatures cause delays in logistics)
    if temperature > 38 or temperature < 2:
        base_delay += 1.2
    
    delay_hours = round(base_delay, 1)
    delay_probability = min(100, round((delay_hours / (transit_time or 1)) * 50, 1))
    
    return {
        'estimated_delay_hours': delay_hours,
        'delay_probability_percent': delay_probability,
        'delay_warning': 'High risk of delay' if delay_probability > 60 else 'Moderate risk' if delay_probability > 30 else 'Low risk'
    }


# ─── ADVANCED FEATURE: Enhanced Route Optimization ─────────────────────────────
def optimize_route_advanced(src_lat: float, src_lon: float, dst_lat: float, dst_lon: float, risk_level: str, 
                            transit_time: float, weather: str, distance: float, temperature: float, humidity: float) -> List[Dict[str, Any]]:
    """Advanced route optimization with detailed scoring."""
    weather_risk_scores = {
        'Clear': 0.1,
        'Partly Cloudy': 0.3,
        'Overcast': 0.5,
        'Light Rain': 0.8,
        'Heavy Rain': 1.0
    }
    
    spoilage_risk_map = {'Low': 0.1, 'Moderate': 0.5, 'High': 1.0}
    
    weather_risk = weather_risk_scores.get(weather, 0.5)
    spoilage_risk = spoilage_risk_map[risk_level]
    delay_data = predict_delay(distance, weather, transit_time, temperature, humidity)
    
    routes = []
    route_configs = [
        {'name': 'Optimal (Best)', 'dist_mult': 1.0, 'base': 100},
        {'name': 'Alternate', 'dist_mult': 1.15, 'base': 85},
        {'name': 'Risky', 'dist_mult': 0.9, 'base': 60}
    ]
    
    for i, config in enumerate(route_configs):
        route_distance = round(distance * config['dist_mult'], 1)
        route_time = round(transit_time * config['dist_mult'], 1)
        
        # Advanced scoring formula as per spec
        route_score = (
            0.30 * (100 - (route_distance / 1000))  +  # Distance (lower is better)
            0.25 * (100 - (route_time / 10))  +         # Time (lower is better)
            0.20 * (100 - weather_risk * 100)  +        # Weather risk
            0.15 * (100 - spoilage_risk * 100)  +       # Spoilage risk
            0.10 * (100 - delay_data['delay_probability_percent'])  # Delay probability
        )
        route_score = max(0, min(100, route_score))
        
        routes.append({
            'name': config['name'],
            'color': ['green', 'orange', 'red'][i],
            'distance_km': route_distance,
            'estimated_time_hours': route_time,
            'overall_score': round(route_score, 1),
            'weather_risk': round(weather_risk * 100, 1),
            'spoilage_risk': round(spoilage_risk * 100, 1),
            'delay_risk': delay_data['delay_probability_percent'],
            'is_recommended': i == 0
        })
    
    return routes


# ─── ADVANCED FEATURE: Storage Recommendations ──────────────────────────────────
@functools.lru_cache(maxsize=128)
def get_detailed_storage_recommendations(food_type: str) -> Dict[str, Any]:
    """Detailed storage recommendations by food type."""
    food_recommendations = {
        # Fruits
        'Apple': {'temp_range': '0-4°C', 'humidity': '90-95%', 'method': 'Cold storage', 'transport': 'Refrigerated'},
        'Banana': {'temp_range': '13-18°C', 'humidity': '85-90%', 'method': 'Ventilated crates', 'transport': 'Ventilated truck'},
        'Mango': {'temp_range': '10-13°C', 'humidity': '90-95%', 'method': 'Cold storage', 'transport': 'Refrigerated'},
        'Orange': {'temp_range': '0-4°C', 'humidity': '90%', 'method': 'Cold storage', 'transport': 'Refrigerated'},
        'Grapes': {'temp_range': '-1-0°C', 'humidity': '95%', 'method': 'Cold storage', 'transport': 'Frozen truck'},
        'Watermelon': {'temp_range': '5-10°C', 'humidity': '85%', 'method': 'Cool storage', 'transport': 'Refrigerated'},
        # Vegetables
        'Potato': {'temp_range': '4-10°C', 'humidity': '90-95%', 'method': 'Dark cool storage', 'transport': 'Ventilated'},
        'Tomato': {'temp_range': '12-20°C', 'humidity': '85%', 'method': 'Cool storage', 'transport': 'Ventilated'},
        'Onion': {'temp_range': '0-4°C', 'humidity': '65-70%', 'method': 'Dry cool storage', 'transport': 'Ventilated'},
        'Carrot': {'temp_range': '0-4°C', 'humidity': '95%', 'method': 'Cold storage', 'transport': 'Refrigerated'},
        'Spinach': {'temp_range': '0-2°C', 'humidity': '95-100%', 'method': 'Ice storage', 'transport': 'Refrigerated'},
        # Dairy & Perishables
        'Milk': {'temp_range': '0-4°C', 'humidity': 'N/A', 'method': 'Deep freeze', 'transport': 'Refrigerated tanker'},
        'Fish': {'temp_range': '0-2°C', 'humidity': 'N/A', 'method': 'Ice container', 'transport': 'Refrigerated truck'},
        'Chicken': {'temp_range': '0-4°C', 'humidity': '90%', 'method': 'Cold storage', 'transport': 'Refrigerated truck'},
        'Paneer': {'temp_range': '0-4°C', 'humidity': '80%', 'method': 'Vacuum sealed', 'transport': 'Refrigerated'},
        # Grains
        'Rice': {'temp_range': '10-20°C', 'humidity': '55-65%', 'method': 'Dry storage', 'transport': 'Open truck'},
        'Wheat': {'temp_range': '10-20°C', 'humidity': '50-60%', 'method': 'Dry storage', 'transport': 'Open truck'},
    }
    
    return food_recommendations.get(food_type, {
        'temp_range': '15-20°C',
        'humidity': '70-80%',
        'method': 'Standard storage',
        'transport': 'Standard truck'
    })


# ─── ADVANCED FEATURE: Image Quality Analysis for Food ─────────────────────────



# ─── PERF OPTIMIZATION: Bundle All Advanced Metrics ─────────────────────────────
def compute_all_advanced_metrics(food_type: str, temperature: float, humidity: float, storage_duration: float,
                                distance: float, weather_condition: str, transit_time: float) -> Dict[str, Any]:
    """Compute ALL 4 slow sections at once for /predict caching."""
    return {
        'shelf_life': predict_shelf_life(food_type, temperature, humidity, storage_duration),
        'spoilage_timeline': generate_spoilage_timeline(food_type, temperature, humidity, storage_duration),
        'storage_recommendations': get_detailed_storage_recommendations(food_type),
        'delay_prediction': predict_delay(distance, weather_condition, transit_time, temperature, humidity)
    }


def analyze_food_image(image_path: str) -> Dict[str, Any]:
    """Analyze food image for spoilage indicators."""
    try:
        from PIL import Image, ImageStat
        from typing import Any, cast, List, Tuple
        img = Image.open(image_path).convert('RGB')
        
        # Get image statistics
        stat = ImageStat.Stat(img)
        avg_brightness = sum(stat.mean[:3]) / 3
        brightness_variance = sum(stat.stddev[:3]) / 3
        
        # Extract dominant colors
        pixel_data = cast(Any, img.getdata())
        pixels = cast(List[Tuple[int, int, int]], list(pixel_data))
        
        # Analyze for spoilage indicators
        dark_spots = sum(1 for p in pixels if sum(p) < 100) / len(pixels) * 100  # Dark spots %
        brown_tones = sum(1 for p in pixels if p[0] > 120 and p[1] < 80 and p[2] < 80) / len(pixels) * 100  # Brown
        
        # Determine condition
        spoilage_score = (dark_spots * 0.4 + brown_tones * 0.3 + (100 - avg_brightness) * 0.3) / 100
        
        if spoilage_score > 0.6:
            condition = 'Heavily Spoiled'
            temperature_adjustment = 5
        elif spoilage_score > 0.3:
            condition = 'Slightly Spoiled'
            temperature_adjustment = 2
        else:
            condition = 'Fresh'
            temperature_adjustment = 0
        
        return {
            'condition': condition,
            'spoilage_score': round(spoilage_score * 100, 1),
            'brightness': round(avg_brightness, 1),
            'dark_spots_percent': round(dark_spots, 1),
            'temperature_adjustment': temperature_adjustment,
            'confidence': round(((dark_spots + brown_tones) / 2), 1)
        }
    except Exception as e:
        print(f"[ERROR] Image analysis: {e}")
        return {
            'condition': 'Unknown',
            'spoilage_score': 50,
            'brightness': 128,
            'dark_spots_percent': 0,
            'temperature_adjustment': 0,
            'confidence': 0
        }