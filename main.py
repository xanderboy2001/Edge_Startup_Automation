import logging
import sys
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

log_file_path = "C:\\Temp\\edge_output.log"


def init_logging():
    logger = logging.getLogger("selenium")
    file_handler = logging.FileHandler(log_file_path, mode="w")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


def setup_webdriver():
    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_argument("--no-sandbox")
    edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    edge_options.add_experimental_option("detach", True)

    driver_path = EdgeChromiumDriverManager().install()
    service = Service(driver_path)
    return webdriver.Edge(service=service, options=edge_options)


if __name__ == "__main__":
    init_logging()
    driver = setup_webdriver()
    driver.get(
        "https://nysifprod.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Eassignment_group%253D2d636adcdb4957006a2c9837db96193e%255Estate!%253D6%255EnumberNOT%2520LIKERITM%26sysparm_first_row%3D1%26sysparm_view%3D"
    )
    input("Press enter to continue...")
    sys.exit()
