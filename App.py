
from flask import Flask, render_template, request
import requests
import math
import time
from datetime import datetime

app = Flask(__name__)

# Adresy i klucze
STATIONS_URL = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"
SENSORS_URL = "https://api.gios.gov.pl/pjp-api/rest/station/sensors/"
DATA_URL = "https://api.gios.gov.pl/pjp-api/rest/data/getData/"
GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

API_KEY = "xxxxx"  # <--  klucz do Google Maps

# Cache
STATIONS_CACHE = {"data": None, "timestamp": 0}
STATIONS_CACHE_TTL = 60 * 10
ALL_VOIV_CACHE = {"data": None, "timestamp": 0}
ALL_VOIV_CACHE_TTL = 60 * 30

def geocode_city(city):
    """
    Zwraca (lat, lon) przy pomocy Google Geocoding API,
    lub (None, None) w przypadku błędu.
    """
    params = {'address': city, 'key': API_KEY}
    try:
        r = requests.get(GEOCODING_URL, params=params)
        if r.status_code == 200:
            js = r.json()
            if js.get('results'):
                loc = js['results'][0]['geometry']['location']
                return loc['lat'], loc['lng']
    except requests.RequestException as e:
        print(f"Błąd geokodowania: {e}")
    return None, None

def get_all_stations():
    """Pobiera listę stacji GIOŚ."""
    try:
        resp = requests.get(STATIONS_URL)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []

def get_all_stations_cached():
    now = time.time()
    if STATIONS_CACHE["data"] and (now - STATIONS_CACHE["timestamp"] < STATIONS_CACHE_TTL):
        return STATIONS_CACHE["data"]
    print("[CACHE] Odświeżam stacje GIOŚ...")
    data = get_all_stations()
    STATIONS_CACHE["data"] = data
    STATIONS_CACHE["timestamp"] = now
    return data

def get_sensors(station_id):
    try:
        r = requests.get(SENSORS_URL + str(station_id))
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def get_all_values(sensor_id):
    vals = []
    try:
        r = requests.get(DATA_URL + str(sensor_id))
        if r.status_code == 200:
            data = r.json()
            for v in data.get('values', []):
                if v['value'] is not None:
                    vals.append(float(v['value']))
    except:
        pass
    return vals
def get_latest_value(sensor_id):
    try:
        r = requests.get(DATA_URL + str(sensor_id))
        if r.status_code == 200:
            data = r.json()
            for v in data.get('values', []):
                if v['value'] is not None:
                    return float(v['value'])
    except:
        pass
    return None

def get_hourly_data(sensor_id):
    """
    Zwraca listę (godzina, wartość) dla pomiarów od 00:00 do ostatniej pełnej godziny.
    """
    try:
        r = requests.get(DATA_URL + str(sensor_id))
        if r.status_code == 200:
            data = r.json()
            vals = data.get('values', [])
            now = datetime.now()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            last_full_hour = now.replace(minute=0, second=0, microsecond=0)

            filtered = []
            for v in vals:
                if v['value'] is None:
                    continue
                dt_str = v['date']
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                if start_of_day <= dt <= last_full_hour:
                    filtered.append((dt, float(v['value'])))
            filtered.sort(key=lambda x: x[0])
            result = []
            for dt_obj, val in filtered:
                hour_label = dt_obj.strftime("%H:%M")
                result.append((hour_label, val))
            return result
    except:
        pass
    return []

def haversine(lat1, lon1, lat2, lon2):
    import math
    R = 6371.0
    lat1r = math.radians(lat1)
    lon1r = math.radians(lon1)
    lat2r = math.radians(lat2)
    lon2r = math.radians(lon2)
    dlat = lat2r - lat1r
    dlon = lon2r - lon1r
    a = (math.sin(dlat/2)**2
         + math.cos(lat1r)*math.cos(lat2r)*math.sin(dlon/2)**2)
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R*c

def find_nearest_stations(lat, lon, stations):
    result = []
    for st in stations:
        st_lat = float(st['gegrLat'])
        st_lon = float(st['gegrLon'])
        dist = haversine(lat, lon, st_lat, st_lon)
        result.append((st, dist))
    return sorted(result, key=lambda x: x[1])

