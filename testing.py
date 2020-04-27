from Scrapper import ScrapperDetik
from Scrapper import ScrapperKompas
from Scrapper import ScrapperRepublika

scd = ScrapperDetik(chromeExecPath='/home/fauh45/Code/chrome-driver/chromedriver', timeout=5)
print(scd.get(20))
print(scd.toLabel("http://plo-label.azurewebsites.net/api"))
del scd

sck = ScrapperKompas(chromeExecPath='/home/fauh45/Code/chrome-driver/chromedriver', timeout=5)
print(sck.get(30))
print(sck.toLabel("http://plo-label.azurewebsites.net/api"))
del sck

scr = ScrapperRepublika(chromeExecPath='/home/fauh45/Code/chrome-driver/chromedriver', timeout=5)
print(scr.get(50))
print(scr.toLabel("http://plo-label.azurewebsites.net/api"))
del scr
