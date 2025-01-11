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
