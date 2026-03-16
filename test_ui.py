import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import BASE_URL_UI


@pytest.fixture(scope="session")
def driver():
    with allure.step("Открыть и настроить браузер"):
        timeout = 20

        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.page_load_strategy = "eager"
        prefs = {"profile.default_content_setting_values.geolocation": 2}
        options.add_experimental_option("prefs", prefs)

        browser = webdriver.Chrome(options=options)
        browser.implicitly_wait(timeout)
        browser.maximize_window()
        yield browser

    with allure.step("Закрыть браузер"):
        browser.quit()


@pytest.mark.ui
@allure.feature("Поиск авиабилетов")
@allure.title("Введение кода IATA прилёта")
@allure.story("Успешный кода IATA прилёта")
@allure.severity(allure.severity_level.CRITICAL)
def test_search_where(driver):
    """Тест ввода кода IATA вместо города прилёта"""
    with allure.step("1. Открыть главную страницу Aviasales"):
        driver.get(BASE_URL_UI)

    with allure.step("2. Нажать на дату"):
        date_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, "//*[@data-test-id='departure-calendar-icon']")))
        date_field.click()

    with allure.step("2. Нажать на конкретное чило: 28"):
        date_28 = driver.find_element(
            By.XPATH, "//button[@aria-label='суббота, 28 марта 2026 г.']")
        date_28.click()

    with allure.step("2. Нажать на кнопку билет в одну сторону"):
        ticket_button = driver.find_element(
            By.CSS_SELECTOR, "[class*='CCkfHTmJ7jcd90Jd rdp-day_button']")
        ticket_button.click()

    with allure.step("2. Вписать в поле 'Куда' код IATA 'ARH'"):
        where_input = driver.find_element(
            By.ID, "avia_form_destination-input")
        where_input.click()
        where_input.send_keys(Keys.ARROW_DOWN)
        where_input.send_keys(Keys.ENTER)

    with allure.step("2. Нажать на кнопку Найти билеты"):
        search_button = driver.find_element(
            By.CSS_SELECTOR, "[data-test-id='form-submit']")
        search_button.click()

    with allure.step("2. Блок со странами есть на странице"):
        assert driver.find_element(By.CSS_SELECTOR, "[data-test-element='country-list']").is_displayed()

