# Instalacja pytest - w terminalu wpisz: pip install pytest
import pytest
from unittest.mock import patch, MagicMock
from App import (  # Zmienione z app na App, ponieważ plik to App.py
    geocode_city,
    get_all_stations_cached,
    get_color_class,
    haversine,
    find_nearest_stations,
    calculate_voivodeship_averages,
    get_latest_value,
)

# Test dla geocode_city
@patch("App.requests.get")  # Poprawione z app.requests.get na App.requests.get
def test_geocode_city(mock_get):
    """
    Test sprawdza poprawność funkcji `geocode_city`.
    Mockujemy odpowiedź API, która zwraca współrzędne miasta.
    """
    # Przygotowanie symulowanej odpowiedzi API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {"geometry": {"location": {"lat": 52.2297, "lng": 21.0122}}}
        ]
    }
    mock_get.return_value = mock_response

    # Wywołanie testowanej funkcji
    lat, lon = geocode_city("Warsaw")

    # Sprawdzenie poprawności odpowiedzi
    assert lat == 52.2297  # Spodziewana szerokość geograficzna
    assert lon == 21.0122  # Spodziewana długość geograficzna


# Test dla funkcji get_all_stations_cached
@patch("App.get_all_stations")  # Poprawione z app.get_all_stations na App.get_all_stations
def test_get_all_stations_cached(mock_get_all_stations):
    """
    Test sprawdza działanie cache w funkcji `get_all_stations_cached`.
    Symulujemy brak danych w cache i odświeżenie stacji.
    """
    # Przygotowanie symulowanej odpowiedzi funkcji get_all_stations
    mock_get_all_stations.return_value = [{"id": 1, "name": "Station 1"}]

    # Wywołanie testowanej funkcji
    stations = get_all_stations_cached()

    # Sprawdzenie poprawności odpowiedzi
    assert len(stations) == 1  # Spodziewana liczba stacji
    assert stations[0]["name"] == "Station 1"  # Sprawdzenie nazwy stacji

# Test dla get_color_class
def test_get_color_class():
    """
    Test sprawdza przypisywanie klas kolorów w zależności od wartości
    i rodzaju parametru zanieczyszczenia.
    """
    # Testy dla PM10
    assert get_color_class("PM10", 10) == "level-very-good"  # Bardzo dobry poziom
    assert get_color_class("PM10", 55) == "level-fair"  # Umiarkowany poziom

    # Testy dla NO2
    assert get_color_class("NO2", 120) == "level-fair"  # Umiarkowany poziom

    # Testy dla O3
    assert get_color_class("O3", 200) == "level-poor"  # Zły poziom


# Test dla haversine
def test_haversine():
    """
    Test sprawdza poprawność obliczeń odległości między dwoma punktami
    geograficznymi za pomocą funkcji `haversine`.
    """
    # Warszawa (52.2297, 21.0122) i Kraków (50.0647, 19.9450)
    distance = haversine(52.2297, 21.0122, 50.0647, 19.9450)

    # Sprawdzenie poprawności obliczeń
    assert round(distance, 1) == 252.0  # Oczekiwana odległość: 252 km


# Test dla find_nearest_stations
def test_find_nearest_stations():
    """
    Test sprawdza działanie funkcji `find_nearest_stations`,
    która sortuje stacje według odległości od zadanego punktu.
    """
    # Przygotowanie przykładowych stacji
    stations = [
        {"gegrLat": "52.2297", "gegrLon": "21.0122", "id": 1},  # Warszawa
        {"gegrLat": "50.0647", "gegrLon": "19.9450", "id": 2},  # Kraków
    ]

    # Punkt odniesienia (51.0, 20.0) - bliżej Krakowa
    nearest = find_nearest_stations(51.0, 20.0, stations)
    print(nearest)  # Debugowanie wyniku

    # Sprawdzenie, czy najbliższą stacją jest Kraków
    assert nearest[0][0]["id"] == 2, f"Expected station 2, got {nearest[0][0]['id']}"


# Test dla calculate_voivodeship_averages
@patch("App.get_sensors") #mockujemy funkcję get_sensors
@patch("App.get_all_values")  #Mockujemy funkcję get_all_values
@patch("App.get_all_stations_cached")  #Mockujemy funkcję get_all_stations_cached
def test_calculate_voivodeship_averages(mock_stations, mock_values, mock_sensors):
    """
    Test sprawdza poprawność obliczania średnich zanieczyszczeń dla województwa.
    Mockujemy odpowiedzi funkcji pobierających dane o stacjach i czujnikach.
    """
    # Przygotowanie danych o stacjach w województwie
    mock_stations.return_value = [
        {"id": 1, "addressVoivodeship": "mazowieckie"},  # Stacja w Mazowieckim
        {"id": 2, "addressVoivodeship": "śląskie"},  # Stacja w Śląskim (pomijana)
    ]
    # Przygotowanie danych o czujnikach
    mock_sensors.return_value = [
        {"id": 101, "param": {"paramName": "PM10"}},  # Czujnik PM10
    ]
    # Przygotowanie danych pomiarowych
    mock_values.return_value = [10, 20, 30]  # Wartości PM10

    # Wywołanie funkcji obliczającej średnie
    averages = calculate_voivodeship_averages("mazowieckie")

    # Sprawdzenie poprawności obliczeń
    assert "PM10" in averages  # Sprawdzenie, czy PM10 jest w wynikach
    assert averages["PM10"]["value_str"] == "20.00 µg/m³"  # Średnia PM10

# Test dla get_latest_value
@patch("App.requests.get")  # Mockujemy requests.get dla symulacji odpowiedzi API
def test_get_latest_value(mock_get):
    """
    Test sprawdza poprawność działania funkcji `get_latest_value`,
    która pobiera ostatnią dostępną wartość z API dla czujnika.
    """
    # Przygotowanie symulowanej odpowiedzi API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "values": [
            {"date": "2025-01-10 12:00:00", "value": 15.5},  # Ostatnia wartość
            {"date": "2025-01-10 13:00:00", "value": None},  # Nowsza wartość, ale brak danych
        ]
    }
    mock_get.return_value = mock_response

    # Wywołanie funkcji
    latest_value = get_latest_value(101)

    # Sprawdzenie poprawności wyniku
    assert latest_value == 15.5  # Spodziewana wartość to 15.5
