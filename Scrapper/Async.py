"""
    PLO-Ciwaruga

    Scrapper Async (Thread) Wrapper
    22/05/2020
"""
from threading import Thread
from Scrapper import Scrapper


class ScrapperWrapper(Thread):
    scrapper: Scrapper
    name: str
    n: int
    labelURL: str

    def __init__(self, scrap: Scrapper, name: str, n: int, labelURL: str):
        Thread.__init__(self)
        self.scrapper = scrap
        self.name = name
        self.n = n
        self.labelURL = labelURL

    def run(self):
        print('[INFO] Starting new thread for %s' % (self.name))
        self.scrapper.get(self.n)
        self.scrapper.toLabel(self.labelURL)

        print('[INFO] Thread %s done' % (self.name))

        del self.scrapper
