"""
    PLO-Ciwaruga

    Scrapper Implementation
    20/04/2020
"""

import json
import re
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scrapper:
    timeout: int
    url: str
    driver: webdriver.Chrome
    results: list(dict)

    def __init__(self, url: str, chromeExecPath: str = "", showBrowser: bool = False, timeout: int = 5) -> None:
        # Setting up the Scrapper Driver
        driver_options = Options()
        # Show browser based on params
        if not showBrowser:
            driver_options.add_argument("headless")
        driver_options.add_argument("incognito")
        driver_options.add_argument("no-default-browser-check")
        driver_options.add_argument("no-first-run")
        driver_options.add_argument("no-sandbox")
        driver_options.add_argument("disable-extensions")

        # If the params for path not empty, use the path
        if len(chromeExecPath) != 0:
            self.driver = webdriver.Chrome(
                executable_path=chromeExecPath, options=driver_options)
        else:
            self.driver = webdriver.Chrome(options=driver_options)

        # Class data init
        self.url = url
        self.results = []
        self.timeout = timeout

    # Convert results class data (list of dict) to raw JSON in string form 
    def toJson(self) -> str:
        return json.dumps(self.results, indent=4)

    # Abstract Class that do the scrapping, depends on each website
    def execute(self) -> str:
        pass


class ScrapperDetik(Scrapper):

    def __init__(self, url: str = "http://news.detik.com/", chromeExecPath: str = '', showBrowser: str = False, timeout: int = 5) -> None:
        super().__init__(url, chromeExecPath=chromeExecPath, showBrowser=showBrowser, timeout=timeout)

    def getArticle(self, page_source) -> dict:
        item: dict
        bs = BS(page_source, 'html.parser')

        for article in bs.findAll('article'):
            judul_wrapper = article.find('a', attrs={'class': 'media__link'})
            
            item['judul'] = judul_wrapper.text
            item['link'] = judul_wrapper['href']

            time_wrapper = article.find('a', attrs={'class': 'media__date'}).find('span')

            item['unix_time'] = time_wrapper['d-time']
            item['normal_time'] = time_wrapper['title']

            image_wrapper = article.find('img')

            item['image_url'] = image_wrapper['src']

            yield item

    def execute(self) -> str:
        # Start with opening up the web
        self.driver.get(self.url)

        try:
            # Wait for All article to load up, with the set timeout
            WebDriverWait(self.driver, self.timeout).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'article')))

            # Search for all articles and process them accordingly
            for article in self.getArticle(self.driver.page_source):
                print(article)

            # TODO : Continue with all the processing
            
        except TimeoutException as TE:
            print(TE)

        except NoSuchElementException as NSE:
            print(NSE)