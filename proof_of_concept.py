"""
Module to perform web searches using DuckDuckGo and Selenium.

This module provides a function `search_duckduckgo` that allows for searching the internet
using the DuckDuckGo search engine. It leverages Selenium WebDriver to automate the browser
interaction, enabling efficient and controlled web scraping.
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


def search_duckduckgo(query: str) -> None:
    """
    Searches for the given query on DuckDuckGo using Selenium

    Args:
        quert (str): The term to search for on DuckDuckGo.

    Returns:
        None
    """
    driver = webdriver.Edge()
    try:
        driver.get("https://duckduckgo.com")
        search_box = driver.find_element(
            By.XPATH,
            '//*[@id="searchbox_input"]',
        )
        search_box.send_keys(query)
        search_box.submit()
        time.sleep(10)
    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    search_duckduckgo("Selenium")
