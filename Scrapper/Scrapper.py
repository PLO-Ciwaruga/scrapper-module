"""
    PLO-Ciwaruga

    Scrapper Implementation
    20/04/2020
"""

import Connector.Sender as Conn

import json
import re
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scrapper:
    timeout: int
    url: str
    driver: webdriver.Chrome
    results: list
    source: str

    def __init__(self, url: str, chromeExecPath: str = "", chromeBinPath: str = "", showBrowser: bool = False, timeout: int = 5) -> None:
        # Setting up the Scrapper Driver
        driver_options = Options()
        # Show browser based on params
        if not showBrowser:
            driver_options.add_argument("headless")
        driver_options.add_argument("incognito")
        driver_options.add_argument("no-default-browser-check")
        driver_options.add_argument("no-first-run")
        driver_options.add_argument("no-sandbox")
        driver_options.add_argument('disable-gpu')
        driver_options.add_argument("disable-extensions")

        if len(chromeBinPath) != 0:
            # Set binary location if path not empty
            driver_options.binary_location = chromeBinPath

        print('[INFO] Creating new instance of Chrome webdriver')
        # If the params for path not empty, use the path
        if len(chromeExecPath) != 0:
            self.driver = webdriver.Chrome(
                executable_path=chromeExecPath, options=driver_options)
        else:
            print('[INFO] Got no parameter path, using env path instead')
            self.driver = webdriver.Chrome(options=driver_options)

        # Class data init
        self.url = url
        self.results = []
        self.timeout = timeout

    # Convert results class data (list of dict) to raw JSON in string form
    def toLabel(self, url: str) -> str:
        print("[INFO] Sending scrapping data to %s" % (url))
        return Conn.sendToLabelStudio(self.results, url).status_code

    # Class Destructor
    def __del__(self):
        print('[INFO] Closing webdriver instance')
        self.driver.quit()

    # Abstract Class that do the scrapping, depends on each website
    def get(self, n: int) -> list:
        pass


class ScrapperDetik(Scrapper):

    def __init__(self, url: str = "http://news.detik.com/indeks", chromeExecPath: str = '', chromeBinPath: str = "", showBrowser: str = False, timeout: int = 5) -> None:
        super().__init__(url, chromeExecPath=chromeExecPath, chromeBinPath=chromeBinPath,
                         showBrowser=showBrowser, timeout=timeout)

    def getBody(self, url: str) -> dict:
        self.driver.implicitly_wait(self.timeout)
        # Create new window to open up the article
        self.driver.execute_script('window.open('');')
        # Switch to the new tab
        self.driver.switch_to.window(self.driver.window_handles[1])

        data = {}

        try:
            # Get the url
            self.driver.get(url)
            # Wait for body
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'detail__body-text')))
            self.driver.implicitly_wait(self.timeout)

            # Create new instace of Beautiful Soup
            bs = BS(self.driver.page_source, 'html.parser')

            body_wrapper = bs.find('div', attrs={'class': 'detail__body-text'})
            # Deleting ANNOYING link in middle of the body
            for ads in body_wrapper.findAll('table', attrs={'class': 'linksisip'}):
                ads.decompose()

            for script in body_wrapper.findAll('script'):
                script.decompose()

            for noscript in body_wrapper.findAll('noscript'):
                noscript.decompose()

            for style in body_wrapper.findAll('style'):
                style.decompose()

            body = body_wrapper.text
            body = re.sub(r'\n+', '\n', body)
            tanggal = bs.find('div', attrs={'class': 'detail__date'}).text

            data = {
                'body': body,
                'tanggal': tanggal
            }

            self.driver.close()

        except TimeoutException as TE:
            self.driver.close()
            print("[ERROR] Detik Scrapper Getting Detail error (timeout), ", TE)

        except NoSuchElementException as NSE:
            self.driver.close()
            print(
                "[ERROR] Detik Scrapper Getting Detail error (Elements not found), ", NSE)

        except NoSuchWindowException as NSW:
            print(
                "[ERROR] Detik Scrapper Getting Detail error (Window already closed), ", NSW)

        finally:
            self.driver.switch_to_window(self.driver.window_handles[0])

            return data

    def getArticle(self, page_source) -> dict:
        bs = BS(page_source, 'html.parser')
        articles = bs.findAll('article')
        print('[INFO] Got %d number of detik article links' % (len(articles)))

        for article in articles:
            item = {}
            judul_wrapper = article.find(
                'h3', attrs={'class': 'media__title'})

            if judul_wrapper == None:
                continue
            else:
                judul_wrapper = judul_wrapper.find('a')

            image_wrapper = article.find('img')

            if image_wrapper == None:
                continue

            item = {
                'judul': str(judul_wrapper.text),
                'link': str(judul_wrapper['href']),
                'image_url': str(image_wrapper['src'])
            }

            yield item

    def scrollDown(self) -> None:
        print('[INFO] Scrolling down to end of site')
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        while True:
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);')

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                print("[INFO] Found the end of the page")
                break

            last_height = new_height

    def nextPage(self) -> None:
        next_button = self.driver.find_element_by_xpath(
            '/html/body/div[5]/div[2]/div[2]/div/div[2]/a[9]')

        try:
            if next_button.is_enabled() and next_button.is_displayed():
                print('[INFO] Going to next page normally')
                next_button.click()

            else:
                print("[INFO] Button is not enabled, trying href method instead")
                print("[INFO] Going to %s for next page" %
                      (next_button.get_attribute('href')))
                self.driver.get(next_button.get_attribute('href'))

        except ElementClickInterceptedException as ECIE:
            print("[ERROR] Next Page error (element blocked) : ", ECIE)
            print("[INFO] Trying href method instead")
            print("[INFO] Going to %s for next page" %
                  (next_button.get_attribute('href')))

            self.driver.get(next_button.get_attribute('href'))

    def get(self, n: int = 100) -> list:
        print('[INFO] Starting scrap for %d detik news' % (n))
        count = 0
        done = False
        # Start with opening up the web
        self.driver.get(self.url)

        while True:
            try:
                # Wait for All article to load up, with the set timeout
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'article')))

                self.scrollDown()

                # Search for all articles and process them accordingly
                for article in self.getArticle(self.driver.page_source):
                    if len(article) == 0:
                        continue

                    article_detailed = self.getBody(article['link'])

                    if(len(article_detailed) == 0):
                        continue

                    temp = {
                        'judul': str(article['judul']).strip(),
                        'tanggal': article_detailed['tanggal'],
                        'isi': article_detailed['body'],
                        'sumber' : "Detik"
                    }

                    self.results.append(temp)
                    count += 1

                    if count >= n:
                        done = True
                        break

                if done:
                    break

                self.nextPage()

            except NoSuchElementException as NSE:
                print(
                    "[ERROR] Detik Scrapper Execute Error (No elemets found), ", NSE)

            except KeyError as KE:
                print("[ERROR] Detik Scrapper Execute Error (Key error), ", KE)

            except TimeoutException as TE:
                print("[ERROR] Detik Scrapper Execute Error (timeout), ", TE)

        print('[INFO] Scrap done')
        return self.results


class ScrapperKompas(Scrapper):

    def __init__(self, url: str = "https://indeks.kompas.com/?site=news", chromeExecPath: str = '', chromeBinPath: str = '', showBrowser: str = False, timeout: int = 5) -> None:
        super().__init__(url, chromeExecPath=chromeExecPath, chromeBinPath=chromeBinPath,
                         showBrowser=showBrowser, timeout=timeout)

    def getBody(self, url: str) -> dict:
        self.driver.implicitly_wait(self.timeout)
        # Create new window to open up the article
        self.driver.execute_script('window.open("");')
        # Switch to the new tab
        self.driver.switch_to.window(self.driver.window_handles[1])

        data = {}

        try:
            # Get the url
            self.driver.get(url)
            # Wait for body
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'read__content')))
            # self.driver.implicitly_wait(self.timeout)

            # Create new instace of Beautiful Soup
            bs = BS(self.driver.page_source, 'html.parser')

            body_wrapper = bs.find('div', attrs={'class': 'read__content'})

            # Deleting ANNOYING link in middle of the body
            for ads in body_wrapper.findAll('a', attrs={'class': 'inner-link-baca-juga'}):
                ads.decompose()

            for script in body_wrapper.findAll('span', attrs={'class': 'ads-on-body'}):
                script.decompose()

            body = body_wrapper.text
            body = re.sub(r'\n+', '\n', body)
            tanggal = bs.find('div', attrs={'class': 'read__time'}).text

            data = {
                'body': body,
                'tanggal': tanggal
            }

            self.driver.close()

        except TimeoutException as TE:
            self.driver.close()
            print("[ERROR] Kompas Scrapper Getting Detail error (timeout), ", TE)

        except NoSuchElementException as NSE:
            self.driver.close()
            print(
                "[ERROR] Kompas Scrapper Getting Detail error (Elements not found), ", NSE)

        except NoSuchWindowException as NSW:
            print(
                "[ERROR] Kompas Scrapper Getting Detail error (Window already closed), ", NSW)

        except Exception as EX:
            self.driver.close()
            print('[ERROR] Kompas Scrapper Exception, ', EX)

        self.driver.switch_to_window(self.driver.window_handles[0])

        return data

    def getArticle(self, page_source) -> dict:
        bs = BS(page_source, 'html.parser')
        articles = bs.findAll('div', attrs={'article__list clearfix'})
        print('[INFO] Got %d number of kompas article links' % (len(articles)))

        for article in articles:
            item = {}
            judul_wrapper = article.find(
                'h3', attrs={'class': 'article__title article__title--medium'})

            if judul_wrapper == None:
                continue
            else:
                judul_wrapper = judul_wrapper.find('a')

            image_wrapper = article.find('img')

            if image_wrapper == None:
                continue

            item = {
                'judul': str(judul_wrapper.text),
                'link': str(judul_wrapper['href']),
                'image_url': str(image_wrapper['src'])
            }

            yield item

    def scrollDown(self) -> None:
        print('[INFO] Scrolling down to end of site')
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        while True:
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);')

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                print("[INFO] Found the end of the page")
                break

            last_height = new_height

    def nextPage(self) -> None:
        next_button = self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/div[1]/div[4]/div/div/div[4]/a")

        try:
            if next_button.is_enabled() and next_button.is_displayed():
                print('[INFO] Going to next page normally')
                next_button.click()

            else:
                print("[INFO] Button is not enabled, trying href method instead")
                print("[INFO] Going to %s for next page" %
                      (next_button.get_attribute('href')))
                self.driver.get(next_button.get_attribute('href'))

        except ElementClickInterceptedException as ECIE:
            print("[ERROR] Next Page error (element blocked) : ", ECIE)
            print("[INFO] Trying href method instead")
            print("[INFO] Going to %s for next page" %
                  (next_button.get_attribute('href')))

            self.driver.get(next_button.get_attribute('href'))

    def get(self, n: int = 30) -> list:
        print('[INFO] Starting scrap for %d kompas news' % (n))
        count = 0
        done = False
        # Start with opening up the web
        self.driver.get(self.url)

        while True:
            try:
                # Wait for All article to load up, with the set timeout
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'article__list')))

                # self.scrollDown()

                # Search for all articles and process them accordingly
                for article in self.getArticle(self.driver.page_source):
                    if len(article) == 0:
                        continue

                    article_detailed = self.getBody(article['link'])

                    if(len(article_detailed) == 0):
                        continue

                    temp = {
                        'judul': str(article['judul']).strip(),
                        'tanggal': article_detailed['tanggal'],
                        'isi': article_detailed['body'],
                        'sumber' : "Kompas"
                    }

                    self.results.append(temp)
                    count += 1

                    if count >= n:
                        done = True
                        break

                if done:
                    break

                self.nextPage()

            except NoSuchElementException as NSE:
                print(
                    "[ERROR] Kompas Scrapper Execute Error (No elemets found), ", NSE)

            except KeyError as KE:
                print("[ERROR] Kompas Scrapper Execute Error (Key error), ", KE)

            except TimeoutException as TE:
                print("[ERROR] Kompas Scrapper Execute Error (timeout), ", TE)

        print('[INFO] Scrap done')
        return self.results


class ScrapperRepublika(Scrapper):

    def __init__(self, url: str = "https://republika.co.id/index/news/", chromeExecPath: str = '', chromeBinPath: str = '', showBrowser: str = False, timeout: int = 5) -> None:
        super().__init__(url, chromeExecPath=chromeExecPath, chromeBinPath=chromeBinPath,
                         showBrowser=showBrowser, timeout=timeout)

    def getBody(self, url: str) -> dict:
        self.driver.implicitly_wait(self.timeout)
        # Create new window to open up the article
        self.driver.execute_script('window.open('');')
        # Switch to the new tab
        self.driver.switch_to.window(self.driver.window_handles[1])

        data = {}

        try:
            # Get the url
            self.driver.get(url)
            # Wait for body
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'artikel')))
            self.driver.implicitly_wait(self.timeout)

            # Create new instace of Beautiful Soup
            bs = BS(self.driver.page_source, 'html.parser')

            body_wrapper = bs.find('div', attrs={'class': 'artikel'})
            # Deleting ANNOYING link in middle of the body
            for text in body_wrapper.findAll('div', attrs={'class': 'taiching'}):
                text.decompose()

            for script in body_wrapper.findAll('script'):
                script.decompose()

            for noscript in body_wrapper.findAll('iframe'):
                noscript.decompose()

            for style in body_wrapper.findAll('style'):
                style.decompose()

            for ads in body_wrapper.findAll('div', attrs={'class': 'baca-juga'}):
                ads.decompose()
                
            for bacajuga in body_wrapper.findAll('div', attrs={'class': 'picked-article'}):
                bacajuga.decompose()

            body = body_wrapper.text
            body = re.sub(r'\n+', '\n', body)
            tanggal = bs.find('div', attrs={'class': 'date_detail'}).text

            data = {
                'body': body,
                'tanggal': tanggal
            }

            self.driver.close()

        except TimeoutException as TE:
            self.driver.close()
            print("[ERROR] Republika Scrapper Getting Detail error (timeout), ", TE)

        except NoSuchElementException as NSE:
            self.driver.close()
            print(
                "[ERROR] Republika Scrapper Getting Detail error (Elements not found), ", NSE)

        except NoSuchWindowException as NSW:
            print(
                "[ERROR] Republika Scrapper Getting Detail error (Window already closed), ", NSW)

        finally:
            self.driver.switch_to_window(self.driver.window_handles[0])

            return data

    def getArticle(self, page_source) -> dict:
        bs = BS(page_source, 'html.parser')
        articles = bs.findAll('div', attrs={'set_subkanal'})
        print('[INFO] Got %d number of republika article links' % (len(articles)))

        for article in articles:
            item = {}
            judul_wrapper = article.find('h2')

            if judul_wrapper == None:
                continue
            else:
                judul_wrapper = judul_wrapper.find('a')

            image_wrapper = article.find('img')

            if image_wrapper == None:
                continue

            item = {
                'judul': str(judul_wrapper.text),
                'link': str(judul_wrapper['href']),
                'image_url': str(image_wrapper['src'])
            }

            yield item

    def scrollDown(self) -> None:
        print('[INFO] Scrolling down to end of site')
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        while True:
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);')

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                print("[INFO] Found the end of the page")
                break

            last_height = new_height

    def nextPage(self) -> None:
        next_button = self.driver.find_element_by_class_name("pagination")

        try:
            if next_button.is_enabled() and next_button.is_displayed():
                print('[INFO] Going to next page normally')
                next_button.click()

            else:
                print("[INFO] Button is not enabled, trying href method instead")
                print("[INFO] Going to %s for next page" %
                      (next_button.get_attribute('href')))
                self.driver.get(next_button.get_attribute('href'))

        except ElementClickInterceptedException as ECIE:
            print("[ERROR] Next Page error (element blocked) : ", ECIE)
            print("[INFO] Trying href method instead")
            print("[INFO] Going to %s for next page" %
                  (next_button.get_attribute('href')))

            self.driver.get(next_button.get_attribute('href'))

    def get(self, n: int = 30) -> list:
        print('[INFO] Starting scrap for %d republika news' % (n))
        count = 0
        done = False
        # Start with opening up the web
        self.driver.get(self.url)

        while True:
            try:
                # Wait for All article to load up, with the set timeout
                # WebDriverWait(self.driver, self.timeout).until(
                #     EC.presence_of_all_elements_located((By.CLASS_NAME, 'article__list clearfix')))

                self.scrollDown()

                # Search for all articles and process them accordingly
                for article in self.getArticle(self.driver.page_source):
                    if len(article) == 0:
                        continue

                    article_detailed = self.getBody(article['link'])

                    if(len(article_detailed) == 0):
                        continue

                    temp = {
                        'judul': str(article['judul']).strip(),
                        'tanggal': article_detailed['tanggal'],
                        'isi': article_detailed['body'],
                        'sumber' : "Republika"
                    }

                    self.results.append(temp)
                    count += 1

                    if count >= n:
                        done = True
                        break

                if done:
                    break

                self.nextPage()

            except NoSuchElementException as NSE:
                print(
                    "[ERROR] Republika Scrapper Execute Error (No elemets found), ", NSE)

            except KeyError as KE:
                print("[ERROR] Republika Scrapper Execute Error (Key error), ", KE)

            except TimeoutException as TE:
                print("[ERROR] Republika Scrapper Execute Error (timeout), ", TE)

        print('[INFO] Scrap done')
        return self.results
