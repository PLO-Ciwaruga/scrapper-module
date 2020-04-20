from Scrapper import ScrapperDetik

sc = ScrapperDetik(chromeExecPath='/home/fauh45/Code/chrome-driver/chromedriver', showBrowser=True, timeout=5)
print(sc.execute(10))
print(sc.toLabel("http://localhost:8200/api"))
del sc
