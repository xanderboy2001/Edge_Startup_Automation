"""
ServiceNow Task Retrieval Module.

This module provides functionality for automating task retrieval from ServiceNow.
It utilizes Selenium WebDriver to launch the browser, navigate to ServiceNow,
log in, retrieve tasks and return them as a list of Task objects.

Usage:
    Tasks can be retrieved by calling get_service_now_tasks(url)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List
import keyring
from selenium import webdriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Global Variables
TIMEOUT = 10


@dataclass
class Task:
    """Represents a ServiceNow Task"""

    number: str
    assigned_to: str
    state: str
    description: str
    opened: datetime
    link: str


def setup_webdriver() -> EdgeWebDriver:
    """
    Sets up and configures the Edge WebDriver.

    Returns:
        web_driver (EdgeWebDriver): The configured Edge Webdriver instance.
    """
    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--headless")
    edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver_path = EdgeChromiumDriverManager().install()
    service = Service(driver_path)
    return webdriver.Edge(service=service, options=edge_options)


def login(driver: EdgeWebDriver, url: str) -> None:
    """
    Logs into the ServiceNow application.

    Args:
        web_driver (EdgeWebDriver): The Edge WebDriver instance.

    Returns:
        None
    """
    driver.get(url)
    username = "achristi@nysif.com"
    textbox_username = driver.find_element(By.ID, "userNameInput")
    textbox_password = driver.find_element(By.ID, "passwordInput")
    textbox_username.send_keys(username)
    textbox_password.send_keys(
        keyring.get_password(service_name="ServiceNow", username=username)
    )
    textbox_password.submit()


def page_loaded(driver: EdgeWebDriver, url: str) -> bool:
    """
    Waits for the specified URL and document to be fully loaded.

    Args:
        web_driver (EdgeWebDriver): The Edge WebDriver instance.
        expected_url (str): The expected URL to wait for.

    Returns:
        bool: True if page is loaded successfully, False otherwise."""
    try:
        WebDriverWait(driver, TIMEOUT).until(EC.url_to_be(url))
        WebDriverWait(driver, TIMEOUT).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
    except TimeoutException as e:
        print(f"Timed out while waiting for the page to load. Error: {e}")
        return False
    else:
        return True


def get_tasks(driver: EdgeWebDriver) -> List[Task]:
    """
    Parses the table on the page and returns a list of Task objects.

    Args:
        web_driver (EdgeWebDriver): The EdgeWebDriver instance.

    Returns:
        List[Task]: A list of Task objects
    """
    find_macroponent_and_switch_to_iframe(driver)
    table = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
    )
    rows = table.find_elements(By.CSS_SELECTOR, "table tbody tr")
    tasks = []
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, "td.vt")
        task_number = cells[0].text.strip()
        assigned_to = cells[1].text.strip()
        state = cells[2].text.strip()
        description = cells[3].text.strip()

        opened_str = cells[4].text.strip()
        opened = datetime.strptime(opened_str, "%m/%d/%Y %I:%M:%S %p")
        link = cells[0].find_element(By.TAG_NAME, "a").get_attribute("href")
        list_object = Task(
            task_number,
            assigned_to,
            state,
            description,
            opened,
            link,
        )
        tasks.append(list_object)
    return tasks


def find_macroponent_and_switch_to_iframe(driver: EdgeWebDriver) -> None:
    """
    Finds the macroponent by its tag name, retrieves the iframe within it,
    and switches the WebDriver to the ifram context.

    Args:
        driver (EdgeWebDriver): The EdgeWebDriver instance used for browser automation.

    Returns:
        None
    """
    shadow_host1 = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "macroponent-f51912f4c700201072b211d4d8c26010")
        )
    )
    # Find the iframe and switch to it
    iframe = WebDriverWait(shadow_host1.shadow_root, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
    )
    # Find the table and parse it
    driver.switch_to.frame(iframe)


def get_service_now_tasks(url: str) -> List[Task]:
    """
    Launches the browser, navigates to ServiceNOW, logs in, gets tasks and returns them.

    Args:
        url (str): The URL of the ServiceNow page.

    Returns:
        List[Task]: A list of Task objects.
    """
    driver = setup_webdriver()
    login(driver, url)
    WebDriverWait(driver, TIMEOUT).until(lambda driver: page_loaded(driver, url))
    tasks = get_tasks(driver)
    driver.quit()
    return tasks
