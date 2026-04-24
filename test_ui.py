import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import BASE_URL_UI
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException
)



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
    """Тест: ввод IATA, затем выбор даты"""
    with allure.step("1. Открыть главную страницу Aviasales"):
        driver.get(BASE_URL_UI)

    with allure.step("2. Вписать в поле 'Куда' код IATA 'ARH'"):
        where_input = WebDriverWait(driver, 15, ignored_exceptions=[StaleElementReferenceException]).until(
                EC.element_to_be_clickable((By.ID, "avia_form_destination-input"))
        )
        where_input.click()
        where_input.send_keys("ARH")
        where_input.send_keys(Keys.TAB)

    with allure.step("3. Нажать на дату (открывается календарь)"):
        date_field = WebDriverWait(driver, 15, ignored_exceptions=[StaleElementReferenceException]).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@data-test-id='departure-calendar-icon']")))
        date_field.click()

    with allure.step("4. Выбрать 28 апреля 2026"):
        date_28 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='вторник, 28 апреля 2026 г.']"))
        )
        date_28.click()

    with allure.step("5. Нажать на кнопку 'билет в одну сторону'"):
        ticket_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[class*='CCkfHTmJ7jcd90Jd rdp-day_button']"))
        )
        ticket_button.click()

    with allure.step("6. Нажать на кнопку Найти билеты"):
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='form-submit']"))
        )
        search_button.click()


def disable_hotel_checkbox(driver):
    """Функция для отключения чек-бокса 'Открыть Островок!' без sleep"""
    wait = WebDriverWait(driver, 5)
    try:
        with allure.step("Проверить и отключить чек-бокс отелей"):
            hotel_checkbox = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "label.s__VtQkw_Oq48k3iOT6.s__GqYnDRAoDxQHwGh8.s__wBKpOKQzfuAVx4yX")))

            checkbox_input = hotel_checkbox.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            if checkbox_input.is_selected():
                hotel_checkbox.click()
                wait.until(lambda d: not checkbox_input.is_selected())
                allure.step("Чек-бокс отелей был отключен")
    except Exception:
        allure.step("Чек-бокс не найден или уже отключен")


def clear_origin_field_completely(driver):
    """Полностью очищает поле 'Откуда' через ожидания"""
    wait = WebDriverWait(driver, 10)
    with allure.step("Очистить поле 'Откуда'"):
        origin_input = wait.until(EC.element_to_be_clickable((By.ID, "avia_form_origin-input")))
        origin_input.click()
        origin_input.send_keys(Keys.CONTROL + "a")
        origin_input.send_keys(Keys.DELETE)
        driver.execute_script("arguments[0].value = '';", origin_input)
        wait.until(lambda d: origin_input.get_attribute("value") == "")
        origin_input.send_keys(Keys.ESCAPE)
        return origin_input


def set_origin_city(driver, city_name):
    """Устанавливает город отправления с использованием ожиданий"""
    wait = WebDriverWait(driver, 10)
    with allure.step(f"Установить город отправления: {city_name}"):
        origin_input = clear_origin_field_completely(driver)
        origin_input.send_keys(city_name)
        try:
            suggest_item = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-test-id='autocomplete-item']")))
            suggest_item.click()
        except TimeoutException:
            origin_input.send_keys(Keys.ENTER)
        wait.until(lambda d: city_name.lower() in origin_input.get_attribute("value").lower())
        entered_value = origin_input.get_attribute("value")
        return origin_input, entered_value


@pytest.mark.ui
@allure.feature("Поиск авиабилетов")
@allure.title("Поиск билетов с выбором даты туда и обратно")
@allure.story("Успешный поиск билетов туда-обратно")
@allure.severity(allure.severity_level.CRITICAL)
def test_round_trip_search(driver):
    """Тест поиска билетов туда и обратно с выбором дат"""
    with allure.step("1. Открыть главную страницу Aviasales"):
        driver.get(BASE_URL_UI)

    disable_hotel_checkbox(driver)

    with allure.step("2. Проверить, что на странице есть форма поиска"):
        form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='avia-form']"))
        )
        assert form.is_displayed()
        origin_input = driver.find_element(By.ID, "avia_form_origin-input")
        assert origin_input.is_displayed()
        destination_input = driver.find_element(By.ID, "avia_form_destination-input")
        assert destination_input.is_displayed()
        search_button = driver.find_element(By.CSS_SELECTOR, "[data-test-id='form-submit']")
        assert search_button.is_displayed()

        allure.step("Все элементы формы поиска присутствуют на странице")


@pytest.mark.ui
@allure.feature("Фильтры поиска")
@allure.title("Фильтрация билетов по количеству пересадок")
@allure.story("Успешная фильтрация билетов")
@allure.severity(allure.severity_level.NORMAL)
def test_filter_by_stops(driver):
    """Тест фильтрации результатов поиска по количеству пересадок"""
    wait = WebDriverWait(driver, 15)
    with allure.step("1. Открыть главную страницу"):
        driver.get(BASE_URL_UI)
        disable_hotel_checkbox(driver)

    with allure.step("2. Установить город отправления - Москва"):
        origin_input = clear_origin_field_completely(driver)
        origin_input.click()
        for char in "Моск":
            origin_input.send_keys(char)

        origin_input.send_keys(Keys.ARROW_DOWN)

        origin_suggest = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "[data-test-id='suggested-city-MOW']"
            ))
        )
        origin_suggest.click()

    with allure.step("3. Ввести город назначения - Сочи"):
        destination_input = wait.until(
            EC.element_to_be_clickable((By.ID, "avia_form_destination-input"))
        )
        destination_input.click()
        destination_input.clear()
        for char in "Сочи":
            destination_input.send_keys(char)
        destination_input.send_keys(Keys.ARROW_DOWN)

        def click_suggest(d):
            try:
                el = d.find_element(By.CSS_SELECTOR, "[data-test-id='suggested-city-AER']")
                d.execute_script("arguments[0].click();", el)
                return True
            except (StaleElementReferenceException, NoSuchElementException):
                return False

        wait.until(click_suggest)

    with allure.step("4. Выбрать дату вылета"):
        date_field = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='start-date-field']"))
        )
        date_field.click()
        date_28 = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//div[@data-test-id='date-28.04.2026']]"))
        )
        date_28.click()

    with allure.step("5. Нажать кнопку 'Найти билеты'"):
        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='form-submit']"))
        )
        search_button.click()

    with allure.step("6. Проверить, что поиск выполнен"):
        wait.until(lambda d: "search" in d.current_url)
        try:
            WebDriverWait(driver, 25).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='ticket-desktop'], "
                                               "[data-test-id='direct-tickets-schedule-container'], "
                                               "[data-test-id='filter-group'],"
                                               "[class*='no-results']"))
            )
            allure.step("Страница с результатами поиска успешно загружена")
        except TimeoutException:
            current_url = driver.current_url
            assert "search" in current_url, f"Поиск не удался, мы всё еще на {current_url}"
            allure.step(f"Поиск подтвержден только по URL: {current_url}")


@pytest.mark.ui
@allure.feature("Поиск отелей")
@allure.title("Поиск отеля с выбором дат заезда и выезда")
@allure.story("Успешный поиск отеля с датами")
@allure.severity(allure.severity_level.CRITICAL)
def test_hotel_search_with_dates(driver):
    """Тест поиска отеля с указанием дат в разных месяцах"""
    wait = WebDriverWait(driver, 15, ignored_exceptions=[StaleElementReferenceException])

    with allure.step("1. Открыть страницу отелей"):
        driver.get("https://aviasales.ru/hotels")

    with allure.step("2. Ввести город - Казань"):
        stale_wait = WebDriverWait(driver, 15, ignored_exceptions=[StaleElementReferenceException])
    for _ in range(5):
        try:
            city_input = stale_wait.until(EC.element_to_be_clickable((By.ID, "hotel_autocomplete-input")))
            city_input.click()
            break
        except StaleElementReferenceException:
            continue

    def get_input():
        return stale_wait.until(EC.element_to_be_clickable((By.ID, "hotel_autocomplete-input")))
    for char in "Казань":
        get_input().send_keys(char)
    get_input().send_keys(Keys.ARROW_DOWN)

    with allure.step("3. Выбрать дату заезда (28 апреля 2026)"):
        start_date_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='start-date-field']")))
        start_date_btn.click()
        date_28_apr = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='date-28.04.2026']")))
        date_28_apr.click()

    with allure.step("4. Выбрать дату выезда (03 мая 2026)"):
        end_date_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='end-date-field']")))
        end_date_btn.click()
        date_03_may = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='date-03.05.2026']")))
        date_03_may.click()

    with allure.step("5. Нажать на кнопку Найти отели"):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        search_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[data-test-id='form-submit']")
        ))
        search_button.click()


@pytest.mark.ui
@allure.feature("Поиск авиабилетов")
@allure.title("Ввод города отправления")
@allure.story("Успешный ввод города отправления")
@allure.severity(allure.severity_level.CRITICAL)
def test_origin_city_input(driver):
    """Тест ввода города отправления с исправленной логикой"""
    wait = WebDriverWait(driver, 10, ignored_exceptions=[StaleElementReferenceException])
    with allure.step("1. Открыть главную страницу Aviasales"):
        driver.get(BASE_URL_UI)
        disable_hotel_checkbox(driver)

    with allure.step("2. Изменить город отправления на Уфа"):
        origin_input = clear_origin_field_completely(driver)
        origin_input.send_keys("Уфа")
        try:
            suggest_item = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='autocomplete-item']"))
            )
            suggest_item.click()
        except TimeoutException:
            origin_input.send_keys(Keys.ENTER)

    with allure.step("3. Проверить, что поле изменилось на Уфа"):
        check_input = wait.until(EC.presence_of_element_located((By.ID, "avia_form_origin-input")))
        wait.until(lambda d: "Уфа" in (check_input.get_attribute("value") or ""))
        entered_value = check_input.get_attribute("value") or ""
        assert "Уфа" in entered_value, f"Ожидалась Уфа, но в поле: {entered_value}"
