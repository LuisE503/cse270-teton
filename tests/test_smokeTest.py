from urllib.parse import urljoin

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "http://127.0.0.1:5500/teton/1.6/"


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


def wait_for(driver, condition):
    return WebDriverWait(driver, 10).until(condition)


def page(driver, filename):
    driver.get(urljoin(BASE_URL, filename))


def test_logo_header_and_title(driver):
    page(driver, "index.html")

    logo = wait_for(driver, EC.visibility_of_element_located(
        (By.CSS_SELECTOR, ".header-logo img")
    ))
    assert logo.get_attribute("alt") == "Teton Chamber of Commerce Logo"
    assert wait_for(driver, EC.visibility_of_element_located(
        (By.XPATH, "//footer//h3[normalize-space()='Teton Idaho Chamber of Commerce']")
    ))
    assert driver.title == "Teton Idaho CoC"


def test_home_spotlights_and_join_feature(driver):
    page(driver, "index.html")

    wait_for(driver, lambda browser: len(
        browser.find_elements(By.CSS_SELECTOR, ".main-spotlight > div")
    ) >= 2)
    join_link = wait_for(driver, EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".main-hero a[href='join.html']")
    ))
    assert join_link.text == "Join Us"
    join_link.click()
    wait_for(driver, EC.url_contains("join.html"))
    assert driver.current_url.endswith("/join.html")


def test_directory_grid_and_list_feature(driver):
    page(driver, "directory.html")

    wait_for(driver, EC.visibility_of_element_located(
        (By.XPATH, "//*[normalize-space()='Teton Turf and Tree']")
    ))
    grid = driver.find_element(By.ID, "directory-grid")
    list_button = driver.find_element(By.ID, "directory-list")

    grid.click()
    assert "active" in grid.get_attribute("class")
    assert "Teton Turf and Tree" in driver.find_element(
        By.ID, "directory-data"
    ).text

    list_button.click()
    wait_for(driver, lambda browser: "directory-list" in browser.find_element(
        By.ID, "directory-data"
    ).get_attribute("class"))
    assert "Teton Turf and Tree" in driver.find_element(
        By.ID, "directory-data"
    ).text


def test_join_page_data_entry(driver):
    page(driver, "join.html")

    first_name = wait_for(driver, EC.visibility_of_element_located(
        (By.NAME, "fname")
    ))
    first_name.send_keys("Ada")
    driver.find_element(By.NAME, "lname").send_keys("Lovelace")
    driver.find_element(By.NAME, "bizname").send_keys("Analytical Engines")
    driver.find_element(By.NAME, "biztitle").send_keys("Founder")
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    wait_for(driver, EC.url_contains("join-step2.html"))
    assert wait_for(driver, EC.visibility_of_element_located(
        (By.NAME, "email")
    ))


def test_admin_page_invalid_username_and_password(driver):
    page(driver, "admin.html")

    wait_for(driver, EC.visibility_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys("not-a-user")
    driver.find_element(By.ID, "password").send_keys("not-a-password")
    driver.find_element(By.CSS_SELECTOR, "input[value='Login']").click()

    error = wait_for(driver, EC.visibility_of_element_located(
        (By.CSS_SELECTOR, ".errorMessage")
    ))
    assert error.text == "Invalid username and password."
