import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()
API_TOKEN: str = os.getenv("API_TOKEN", "")
COOKIE_LIST: List[Dict[str, Any]] = json.loads(os.getenv("COOKIE_JSON", "[]"))
BASE_URL_API: str = "https://explore-api.aviasales.com/api/v1/calendar/filters.json"
BASE_URL_UI: str = "https://www.aviasales.ru"


SEARCH_DATA: Dict[str, str] = {
    "destination": "MOW", 
    "origin": "VOG",
    "locale": "ru_RU"
}

HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json"
}
