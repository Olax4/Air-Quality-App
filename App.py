
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

