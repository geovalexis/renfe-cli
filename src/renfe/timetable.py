import os
import re
from datetime import datetime, date, timedelta
from typing import List, Union
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome

os.environ['WDM_LOG_LEVEL'] = '0'


def get_timetable(
        origin: str,
        destination: str,
        days_from_today: int = 0,
        browser_name: str = "firefox",
        search_timeout: int = 3) -> List[dict]:
    soup = get_soup(browser_name, origin, destination, days_from_today, search_timeout)
    types = get_types(soup)
    durations = get_durations(soup)
    departures = get_departures(soup)
    arrivals = get_arrivals(soup)
    prices = get_prices(soup)

    return [
        {"type": t, "departure": de, "arrival": a, "duration": du, "price": p}
        for t, de, a, du, p in zip(types, departures, arrivals, durations, prices)
    ]


def get_browser(type: str) -> Union[Firefox, Chrome]:
    global browser
    try:
        if type == "firefox":
            from selenium.webdriver.firefox.options import Options
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            browser = webdriver.Firefox(options=firefox_options)
        else:  # chrome
            from selenium.webdriver.chrome.options import Options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            browser = webdriver.Chrome(options=chrome_options)

        browser.implicitly_wait(10)  # wait up to 10 seconds while trying to locate elements

    except ValueError as ex:
        raise ex

    return browser


def get_soup(browser_name: str, origin: str, destination: str, days_from_today: int, search_timeout: int) -> BeautifulSoup:
    browser = get_browser(browser_name)
    browser.get("https://www.renfe.com/es/es")

    sleep(3)

    origin_input = browser.find_element(By.CSS_SELECTOR, "rf-awesomplete.rf-input-autocomplete:nth-child(1) \
> div:nth-child(1) > div:nth-child(2) > input:nth-child(1)")
    origin_input.send_keys(origin)

    sleep(0.05)

    origin_option = browser.find_element(By.CSS_SELECTOR, "#awesomplete_list_1_item_0")
    origin_option.click()

    destination_input = browser.find_element(By.CSS_SELECTOR, "rf-awesomplete.rf-input-autocomplete:nth-child(2) \
> div:nth-child(1) > div:nth-child(2) > input:nth-child(1)")
    destination_input.send_keys(destination)

    sleep(0.05)

    destination_option = browser.find_element(By.CSS_SELECTOR, "#awesomplete_list_2_item_0")
    destination_option.click()

    time = browser.find_element(By.CSS_SELECTOR, "div.rf-daterange__container-ipt:nth-child(2) > div:nth-child(2) \
> button:nth-child(2) > i:nth-child(1)")

    while days_from_today > 0:
        days_from_today = days_from_today - 1
        time.click()
    
    search_button = browser.find_element(By.CSS_SELECTOR, "#contentPage > div > div > div:nth-child(1) > div \
    > div > div > div > div > div > rf-header > rf-header-top > div > div.rf-header__wrap-search.grid.sc-rf-header-top \
    > rf-search > div > div.rf-search__filters.rf-search__filters--open > div.rf-search__wrapper-button > \
    div.rf-search__button > form > rf-button > div > div > button > div.mdc-button__touch.sc-rf-button")
    search_button.click()

    sleep(search_timeout)

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    browser.quit()

    return soup


def get_departures(soup) -> List[str]:
    result = []
    attrs_departure = {
            'class': 'booking-list-element-big-font salida displace-text-xs',
        }
    departures = soup.find_all('div', attrs=attrs_departure)
    for departure in departures:
        result.append(departure.text.strip())
    return result


def get_arrivals(soup) -> List[str]:
    result = []
    attrs_arrival = {
            'class': 'booking-list-element-big-font llegada',
        }
    arrivals = soup.find_all('div', attrs=attrs_arrival)
    for arrival in arrivals:
        result.append(arrival.text.strip())
    return result


def get_durations(soup) -> List[str]:
    result = []
    attrs_duration = {
        'class': 'purple-font displace-text duracion hidden-xs',
        'aria-label': 'Duración'
    }
    durations = soup.find_all('div', attrs=attrs_duration)
    for duration in durations:
        result.append(duration.text.strip())
    return result


def get_types(soup) -> List[str]:
    result = []
    attrs_duration = {
            'class': 'purple-font displace-text duracion hidden-xs',
            'aria-label': 'Duración'
        }
    durations = soup.find_all('div', attrs=attrs_duration)
    attrs_duration_hidden = {
            'class': 'purple-font displace-text visible-xs text-nowrap',
        }
    durations_hidden = soup.find_all('div', attrs=attrs_duration_hidden)
    attrs_duration_and_type = {
            'class': 'displace-text',
        }
    durations_and_types = soup.find_all('div', attrs=attrs_duration_and_type)
    types = [item for item in durations_and_types if item not in durations_hidden + durations]
    for t in types:
        result.append(t.text.strip())
    return result


def get_date(days_from_today: int) -> str:
    day = datetime.today() + timedelta(days=days_from_today)
    return f"{day.year}-{day.month}-{day.day}"


def get_days(date_iso: str) -> int:
    date_obj = date.fromisoformat(date_iso)
    return (date_obj - date.today()).days


def get_prices(soup) -> List[List[str]]:
    prices = []
    attrs_trip = {"class": re.compile("trayectoRow\w*")}
    trips = soup.find_all("tr", attrs=attrs_trip)
    for trip in trips:
        attrs_price = {"class":"precio booking-list-element-big-font"}
        price = trip.find_all("div", attrs=attrs_price)
        if len(price)>0:
            price = [p.get_text() for p in price]
        else:
            attrs_train_status = {"class": re.compile("booking-list-element-price\w*")}
            price = [trip.find_all("td", attrs=attrs_train_status)[0].get_text().strip("\n").strip()]
        prices.append(price)
    return prices