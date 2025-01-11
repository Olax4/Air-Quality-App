# Air Quality App

## Opis projektu
Air Quality App to aplikacja webowa umożliwiająca monitorowanie jakości powietrza w wybranej lokalizacji. Użytkownik może wprowadzić nazwę miasta, a aplikacja wyświetli dane dotyczące jakości powietrza z najbliższej stacji pomiarowej. Dodatkowo aplikacja oblicza średnie pomiary dla województw i prezentuje dane w sposób graficzny.

## Funkcje
- **Wyszukiwanie stacji:** Użytkownik podaje miasto, a aplikacja lokalizuje najbliższą stację pomiarową w promieniu 20 km.
- **Dane bieżące:** Pobieranie i wyświetlanie aktualnych pomiarów jakości powietrza.
- **Wykresy godzinowe:** Wizualizacja danych godzinowych od 00:00 do ostatniej pełnej godziny.
- **Średnie wojewódzkie:** Obliczanie średnich wartości dla wybranego województwa oraz porównanie wszystkich województw w Polsce.
- **Responsywność:** Obsługa zarówno na komputerach, jak i urządzeniach mobilnych.

## Technologie
### Backend
- **Python**: Język programowania użyty do implementacji logiki aplikacji.
- **Flask**: Mikroframework webowy do obsługi żądań HTTP.
- **Biblioteki:**
  - `requests`: Pobieranie danych z API.
  - `math`, `time`, `datetime`: Obsługa obliczeń i operacji czasowych.
  - `Jinja2`: Silnik szablonów do dynamicznego generowania HTML.

### Frontend
- **HTML**: Struktura aplikacji.
- **CSS**: Stylizacja interfejsu użytkownika.
- **Leaflet**: Wizualizacja map.
- **Chart.js**: Generowanie wykresów.

### API
- **API GIOŚ:** Pobieranie danych o stacjach pomiarowych i wynikach pomiarów.
- **Google Geocoding API:** Geokodowanie lokalizacji na podstawie nazwy miasta.

### Narzędzia dodatkowe
- **Ngrok:** Umożliwia tymczasowe udostępnienie aplikacji lokalnej w internecie. Przydatne do testowania i prezentacji aplikacji.

### Struktura 

/Air-Quality-App/
├── static/
│   └── styles.css
├── templates/
│   └── index.html
├── docs/
│   └── Dokumentacja_Air_Quality_App.pdf
├── App.py
├── requirements.txt
├── README.md




## Jak uruchomić projekt
### Wymagania
- Python 3.x
- Klucz API do Google Geocoding API
- Zainstalowany Ngrok (opcjonalne, do udostępniania aplikacji publicznie)
- Połączenie internetowe

### Instrukcje
1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/<your-username>/air-quality-app.git
   cd air-quality-app
   ```
2. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```
3. Skonfiguruj plik `config.py` (jeśli wymagany) i wprowadź swój klucz API Google Geocoding.
4. Uruchom aplikację:
   ```bash
   python app.py
   ```
5. (Opcjonalnie) Udostępnij aplikację za pomocą Ngrok:
   - Uruchom Ngrok:
     ```bash
     ngrok http 5000
     ```
   - Skopiuj wygenerowany publiczny URL i wklej go w przeglądarce.

   ```
## Przykłady działania
1. **Wprowadzenie miasta**: Wpisz nazwę miasta w formularzu i kliknij "Sprawdź".
2. **Wynik**: Wyświetli się najbliższa stacja pomiarowa, dane bieżące, wykresy oraz średnie wojewódzkie.
3. **Mapa**: Zobacz lokalizację stacji i miasta na mapie.

## Licencja
Projekt objęty licencją **Apache License 2.0**.

## Autorzy
- Kornelia Lis
- Aleksandra Przybyło
