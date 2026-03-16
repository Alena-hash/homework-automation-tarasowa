import pytest
import requests
import allure
from typing import Any, List, Dict
import config

@allure.epic("API Тестирование Aviasales")
@allure.feature("Поиск и фильтры")
class TestAviasalesApi:

    @allure.title("Кейс №1: Поиск по названию на кириллице")
    @pytest.mark.api
    def test_search_cyrillic(self) -> None:
        params: Dict[str, str] = {"destination": "МОС", "origin": "ВОЛ", "locale": "ru_RU"}
        with allure.step("Отправка запроса к фильтрам календаря"):
            response = requests.get(config.BASE_URL_API, params=params, headers=config.HEADERS)
        assert response.status_code == 200

    @allure.title("Кейс №2: Поиск по названию на латинице")
    @pytest.mark.api
    def test_search_latin(self) -> None:
        params: Dict[str, str] = {"destination": "MOW", "origin": "VJG", "locale": "ru_RU"}
        with allure.step("Отправка запроса на латинице"):
            response = requests.get(config.BASE_URL_API, params=params, headers=config.HEADERS)
        assert response.status_code == 200

    @allure.title("Кейс №3: Поиск по названию с цифрами")
    @pytest.mark.api
    def test_search_with_numbers(self) -> None:
        params: Dict[str, str] = {"destination": "12345", "origin": "VOG", "locale": "ru_RU"}
        with allure.step("Отправка запроса с цифрами"):
            response = requests.get(config.BASE_URL_API, params=params, headers=config.HEADERS)
        assert response.status_code == 200

    @allure.title("Кейс №4: Поиск по произвольному названию (абракадабра)")
    @pytest.mark.api
    def test_search_random_text(self) -> None:
        params: Dict[str, str] = {"destination": "qwsderftg", "origin": "VOG", "locale": "ru_RU"}
        with allure.step("Отправка произвольного текста"):
            response = requests.get(config.BASE_URL_API, params=params, headers=config.HEADERS)
        assert response.status_code == 200

    @allure.title("Кейс №5: Пустой поиск")
    @pytest.mark.api
    def test_search_empty(self) -> None:
        params: Dict[str, str] = {"destination": "", "origin": "VOG", "locale": "ru_RU"}
        with allure.step("Отправка пустого запроса"):
            response = requests.get(config.BASE_URL_API, params=params, headers=config.HEADERS)
        assert response.status_code == 400

    @allure.title("Кейс №6: Поиск без токена")
    @pytest.mark.api
    def test_search_no_token(self) -> None:
        with allure.step("Запрос без заголовка Authorization"):
            response = requests.get(config.BASE_URL_API, params={"destination": "MOW",  "origin": "VOG", "locale": "ru_RU"})
        assert response.status_code == 200

    @allure.title("Кейс №7: Поиск с методом PUT вместо GET")
    @pytest.mark.api
    def test_search_wrong_method(self) -> None:
        with allure.step("Отправка PUT запроса вместо GET"):
            response = requests.put(config.BASE_URL_API, params={"destination": "MOW", "origin": "VOG", "locale": "ru_RU"})
        assert response.status_code in [200, 404, 405]

    @allure.title("Кейс №8: Поиск с неактуальным токеном")
    @pytest.mark.api
    def test_search_invalid_token(self) -> None:
        headers = {"Authorization": "Bearer expired_token_123"}
        with allure.step("Запрос с просроченным токеном"):
            response = requests.get(config.BASE_URL_API, params={"destination": "MOW", "origin": "VOG", "locale": "ru_RU"}, headers=headers)
        assert response.status_code in [200, 401, 403, 404]
