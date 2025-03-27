import time
from selenium import webdriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from typing import List
from dataclasses import dataclass
import keyring

TIMEOUT = 20


@dataclass
class Task:
    number: str
    assigned_to: str
    state: str
    short_desctiption: str
    opened: str


def setup_webdriver():
    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--headless")
    edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # edge_options.add_experimental_option("detach", True)

    driver_path = EdgeChromiumDriverManager().install()
    service = Service(driver_path)
    return webdriver.Edge(service=service, options=edge_options)


def login(web_driver: EdgeWebDriver):
    username = "achristi@nysif.com"
    textbox_username = web_driver.find_element(By.ID, "userNameInput")
    textbox_password = web_driver.find_element(By.ID, "passwordInput")
    textbox_username.send_keys(username)
    textbox_password.send_keys(
        keyring.get_password(service_name="ServiceNow", username=username)
    )
    textbox_password.submit()


def dump_elements(elements: List[WebElement]):
    print("Dumping elements...")
    for element in elements:
        print(f"Tag Name: {element.tag_name}\tText: {element.text}")


def parse_table(web_driver: EdgeWebDriver):
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
    driver = setup_webdriver()
    driver.get(
        "https://nysifprod.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_nostack%3Dtrue%26sysparm_query%3Dactive%253Dtrue%255Eassignment_group%253D2d636adcdb4957006a2c9837db96193e%255Estate!%253D6%255EnumberNOT%2520LIKERITM%26sysparm_first_row%3D1%26sysparm_view%3D"
    )
    login(driver)
    time.sleep(5)
    try:
        shadow_host1 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[starts-with(name(), 'macroponent')]")
            )
        )
        shadow_root1 = shadow_host1.shadow_root
        iframe = WebDriverWait(shadow_root1, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
        )
        # shadow_root1.find_element(By.CSS_SELECTOR, "iframe")
        driver.switch_to.frame(iframe)
        # dump_elements(driver.find_elements(By.CSS_SELECTOR, "#task_table"))
        # print(driver.find_element(By.CSS_SELECTOR, "#task_table"))
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        print(parse_table(driver))

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
