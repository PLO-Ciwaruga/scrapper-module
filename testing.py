from Scrapper import ScrapperDetik
from Scrapper import ScrapperKompas
from Scrapper import ScrapperRepublika

scd = ScrapperDetik(chromeExecPath='/home/fauh45/Code/chrome-driver/chromedriver', showBrowser=True, timeout=5)
print(scd.execute(10))
print(scd.toLabel("http://localhost:8200/api"))
del scd

sck = ScrapperKompas(chromeExecPath='', showBrowser=True, timeout=5)
print(sck.execute(30))
print(sck.toLabel("http://localhost:8200/api"))
del sck

scr = ScrapperRepublika(chromeExecPath='', showBrowser=True, timeout=5)
print(scr.execute(50))
print(scr.toLabel("http://localhost:8200/api"))
del scr
