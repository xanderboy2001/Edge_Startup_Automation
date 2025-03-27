from dataclasses import dataclass
from typing import List
import keyring
from selenium import webdriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchShadowRootException, TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

TIMEOUT = 10


@dataclass
class Task:
    number: str
    assigned_to: str
    state: str
    short_desctiption: str
    opened: str


def setup_webdriver() -> None:
    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--headless")
    edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver_path = EdgeChromiumDriverManager().install()
    service = Service(driver_path)
    return webdriver.Edge(service=service, options=edge_options)


def login(web_driver: EdgeWebDriver) -> None:
    username = "achristi@nysif.com"
    textbox_username = web_driver.find_element(By.ID, "userNameInput")
    textbox_password = web_driver.find_element(By.ID, "passwordInput")
    textbox_username.send_keys(username)
    textbox_password.send_keys(
        keyring.get_password(service_name="ServiceNow", username=username)
    )
    textbox_password.submit()


def page_loaded(web_driver: EdgeWebDriver, expected_url: str) -> bool:
    try:
        WebDriverWait(web_driver, TIMEOUT).until(EC.url_to_be(expected_url))
        WebDriverWait(web_driver, TIMEOUT).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
    except TimeoutException as e:
        print(f"Timed out while waiting for the page to load. Error: {e}")
        return False
    else:
        return True


def parse_table(web_driver: EdgeWebDriver) -> List[Task]:
    task_list = list()
    task_elements = web_driver.find_elements(By.CSS_SELECTOR, ".list_row")
    for task_element in task_elements:
        td_elements = task_element.find_elements(By.CSS_SELECTOR, "td.vt")
        task_list.append(
            Task(
                number=td_elements[0].text,
                assigned_to=td_elements[1].text,
                state=td_elements[2].text,
                short_desctiption=td_elements[3].text,
                opened=td_elements[4].text,
            )
        )
    return task_list


if __name__ == "__main__":
    url = "https://nysifprod.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_nostack%3Dtrue%26sysparm_query%3Dactive%253Dtrue%255Eassignment_group%253D2d636adcdb4957006a2c9837db96193e%255Estate!%253D6%255EnumberNOT%2520LIKERITM%26sysparm_first_row%3D1%26sysparm_view%3D"
    # Initialize Edge
    driver = setup_webdriver()
    # Navigate to SNOW
    driver.get(url)
    # Login
    login(driver)
    # Wait until page is loaded before trying to work with it
    WebDriverWait(driver, TIMEOUT).until(lambda driver: page_loaded(driver, url))
    # Find the macroponent
    try:
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
        table = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        print(parse_table(driver))

    except TimeoutException as e:
        print(f"Timed out while waiting for element: {e}")
    except NoSuchShadowRootException as e:
        print(f"Cannot find shadow root: {e}")
    except Exception as e:
        print(type(e))
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
