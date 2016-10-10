from urllib.request import urlopen
from urllib.error import HTTPError,URLError
from bs4 import BeautifulSoup
import re
from lxml import etree
html = urlopen('http://www.bilibili.com')
dom = etree.HTML(html.read())
#print (bsObj)
childrenList = dom.xpath('//span')
print(len(childrenList))
for child in childrenList:
    print (child)
