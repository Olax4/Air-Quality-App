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

def get_color_class(param_name, value):
    """
    Zwraca klasę CSS (level-very-good, level-good, etc.) zależnie od parametru i wartości.
    """
    name_map = {
        "PM10": "PM10",
        "PYŁ ZAWIESZONY PM10": "PM10",
        "PM2.5": "PM2.5",
        "PYŁ ZAWIESZONY PM2.5": "PM2.5",
        "DWUTLENEK AZOTU": "NO2",
        "NO2": "NO2",
        "DWUTLENEK SIARKI": "SO2",
        "SO2": "SO2",
        "OZON": "O3",
        "O3": "O3"
    }
    def between(x, a, b):
        return (x>a and x<=b)

    short = name_map.get(param_name.upper(), param_name.upper())
    if short == "PM10":
        if 0 <= value <= 20: return "level-very-good"
        elif between(value,20,50): return "level-good"
        elif between(value,50,80): return "level-fair"
        elif between(value,80,110):return "level-moderate"
        elif between(value,110,150):return "level-poor"
        else:                      return "level-very-poor"
    elif short == "PM2.5":
        if 0 <= value <= 13:     return "level-very-good"
        elif between(value,13,35):   return "level-good"
        elif between(value,35,55):   return "level-fair"
        elif between(value,55,75):   return "level-moderate"
        elif between(value,75,110):  return "level-poor"
        else:                       return "level-very-poor"
    elif short == "NO2":
        if 0 <= value <= 40:     return "level-very-good"
        elif between(value,40,100):  return "level-good"
        elif between(value,100,150): return "level-fair"
        elif between(value,150,200): return "level-moderate"
        elif between(value,200,300): return "level-poor"
        else:                       return "level-very-poor"
    elif short == "O3":
        if 0 <= value <= 70:     return "level-very-good"
        elif between(value,70,120):  return "level-good"
        elif between(value,120,150): return "level-fair"
        elif between(value,150,180): return "level-moderate"
        elif between(value,180,240): return "level-poor"
        else:                       return "level-very-poor"
    elif short == "SO2":
        if 0 <= value <= 50:     return "level-very-good"
        elif between(value,50,100):  return "level-good"
        elif between(value,100,200): return "level-fair"
        elif between(value,200,350): return "level-moderate"
        elif between(value,350,500): return "level-poor"
        else:                       return "level-very-poor"
    return "level-unknown"

def calculate_voivodeship_averages(voiv):
    """Średnie w danym województwie."""
    stations = get_all_stations_cached()
    voiv_stations = []
    for st in stations:
        v1 = (st.get('addressVoivodeship') or "").lower()
        v2 = ""
        if ('city' in st and 'commune' in st['city']
            and 'provinceName' in st['city']['commune']):
            v2 = (st['city']['commune']['provinceName'] or "").lower()
        if (v1 == voiv.lower() or v2 == voiv.lower()):
            voiv_stations.append(st)

    param_sums = {}
    for st in voiv_stations:
        sensors = get_sensors(st['id'])
        for sens in sensors:
            p = sens['param']['paramName']
            vals = get_all_values(sens['id'])
            if vals:
                if p not in param_sums:
                    param_sums[p] = {"sum": 0.0, "count": 0}
                param_sums[p]["sum"] += sum(vals)
                param_sums[p]["count"] += len(vals)

    result = {}
    for p, sc in param_sums.items():
        avg_val = sc["sum"]/sc["count"]
        cclass = get_color_class(p, avg_val)
        result[p] = {
            "value_str": f"{avg_val:.2f} µg/m³",
            "color_class": cclass
        }
    return result
def calculate_all_voivodeships_averages():
    """
    Województwa w wierszach, parametry w kolumnach.
    """
    stations = get_all_stations_cached()
    voiv_dict = {}
    for st in stations:
        v1 = (st.get('addressVoivodeship') or "").strip().lower()
        v2 = ""
        if ('city' in st and 'commune' in st['city']
            and 'provinceName' in st['city']['commune']):
            v2 = (st['city']['commune']['provinceName'] or "").strip().lower()
        final_voiv = v1 if v1 else v2
        if not final_voiv:
            continue
        voiv_dict.setdefault(final_voiv, []).append(st)

    all_result = {}
    for voiv, st_list in voiv_dict.items():
        param_sums = {}
        for st in st_list:
            sensors = get_sensors(st['id'])
            for sens in sensors:
                p = sens['param']['paramName']
                vals = get_all_values(sens['id'])
                if vals:
                    if p not in param_sums:
                        param_sums[p] = {"sum":0.0, "count":0}
                    param_sums[p]["sum"] += sum(vals)
                    param_sums[p]["count"] += len(vals)
        voiv_result = {}
        for p, sc in param_sums.items():
            avg_val = sc["sum"]/sc["count"]
            cclass = get_color_class(p, avg_val)
            voiv_result[p] = {
                "value_str": f"{avg_val:.2f} µg/m³",
                "color_class": cclass
            }
        all_result[voiv] = voiv_result
    return all_result
def calculate_all_voivodeships_averages_cached():
    now = time.time()
    if ALL_VOIV_CACHE["data"] and (now - ALL_VOIV_CACHE["timestamp"] < ALL_VOIV_CACHE_TTL):
        return ALL_VOIV_CACHE["data"]
    data = calculate_all_voivodeships_averages()
    ALL_VOIV_CACHE["data"] = data
    ALL_VOIV_CACHE["timestamp"] = now
    return data
@app.route('/', methods=['GET','POST'])
def index():
    pollutant_data = {}
    hourly_plot_data = {}
    voivodeship_averages = {}
    chosen_voiv = ""
    all_voiv_averages = {}

    city_coords = None
    nearest_station = None
    distance = None

    if request.method == 'POST':
        city = request.form['city']
        lat, lon = geocode_city(city)
        if not lat or not lon:
            return render_template(
                'index.html',
                error="Nie udało się znaleźć współrzędnych miasta.",
                pollutant_data=pollutant_data,
                voivodeship_averages=voivodeship_averages,
                all_voiv_averages=all_voiv_averages
            )

        city_coords = (lat, lon)
        stations = get_all_stations_cached()
        st_sorted = find_nearest_stations(lat, lon, stations)
        for st, dist in st_sorted:
            if dist <= 20:
                nearest_station = st
                distance = dist
                break

        if not nearest_station:
            return render_template(
                'index.html',
                error="Nie znaleziono stacji w promieniu 20 km.",
                pollutant_data=pollutant_data,
                city_coords=city_coords,
                voivodeship_averages=voivodeship_averages,
                all_voiv_averages=all_voiv_averages
            )

        # Bieżące dane
        sensors = get_sensors(nearest_station['id'])
        for sens in sensors:
            param_name = sens['param']['paramName']
            val = get_latest_value(sens['id'])
            if val is not None:
                cclass = get_color_class(param_name, val)
                pollutant_data[param_name] = {
                    "value_str": f"{val:.1f} µg/m³",
                    "color_class": cclass
                }
            else:
                pollutant_data[param_name] = {
                    "value_str": "Brak danych",
                    "color_class": "level-unknown"
                }

            # Wykresy godzinowe
            data_points = get_hourly_data(sens['id'])
            if data_points:
                hourly_plot_data[param_name] = data_points

        # Województwo
        if 'addressVoivodeship' in nearest_station and nearest_station['addressVoivodeship']:
            chosen_voiv = nearest_station['addressVoivodeship']
        if ('city' in nearest_station and 'commune' in nearest_station['city']
            and 'provinceName' in nearest_station['city']['commune']):
            if not chosen_voiv:
                chosen_voiv = nearest_station['city']['commune']['provinceName']

        if chosen_voiv:
            voivodeship_averages = calculate_voivodeship_averages(chosen_voiv)

        all_voiv_averages = calculate_all_voivodeships_averages_cached()

        return render_template(
            'index.html',
            city=city,
            nearest_station=nearest_station,
            distance=distance,
            pollutant_data=pollutant_data,
            city_coords=city_coords,
            hourly_plot_data=hourly_plot_data,
            voivodeship_averages=voivodeship_averages,
            chosen_voiv=chosen_voiv,
            all_voiv_averages=all_voiv_averages
        )

    # GET
    return render_template(
        'index.html',
        pollutant_data=pollutant_data,
        city_coords=city_coords,
        hourly_plot_data=hourly_plot_data,
        voivodeship_averages=voivodeship_averages,
        all_voiv_averages=all_voiv_averages
    )

if __name__ == '__main__':
    app.run(debug=True)  # Uruchamia aplikację Flask w trybie debugowania
