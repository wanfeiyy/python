from urllib.request import urlopen
from urllib.error import HTTPError,URLError
from bs4 import BeautifulSoup
def getTitle(url):
    try:
        html = urlopen(url)
    except(HTTPError,URLError) as e :
        return None
    try:
         bsObj = BeautifulSoup(html.read(),"html.parser")
         title = bsObj.html.head.title
    except AttributeError as e:
         return None
    return title
title = getTitle('http://www.bilibili.com')
if title == None:
    print('Title Not Found')
else:
    print(title)
