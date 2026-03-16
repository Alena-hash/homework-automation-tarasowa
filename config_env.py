import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

AUTH_TOKEN: str = os.getenv("API_TOKEN", "")
BASE_URL_API: str = "https://explore-api.aviasales.com/api/v1/calendar/filters.json"
BASE_URL_UI: str = "https://www.aviasales.ru"

SEARCH_DATA: Dict[str, str] = {
    "destination": "MOW", 
    "origin": "VOG",
    "locale": "ru_RU"
}

UI_TEST_DATA: Dict[str, str] = {
    "origin": "Волгоград",
    "destination": "Москва"
}

HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json"
}
