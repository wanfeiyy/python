from urllib.request import urlopen
from urllib.error import HTTPError,URLError
from bs4 import BeautifulSoup
import re
import datetime
import random
random.seed(datetime.datetime.now())
def getLinks(articleUrl):
    html = urlopen("https://en.wikipedia.org"+articleUrl)
    bsObj = BeautifulSoup(html.read(),"html.parser")
    links = bsObj.find("div",{"id":"bodyContent"}).findAll("a",href=re.compile("^(/wiki/)((?!:).)*$"))
    return links
links = getLinks("/wiki/Kevin_Bacon")
while len(links) > 0:
    nameArticle = links[random.randint(0,len(links)-1)].attrs['href']
    print (nameArticle)
    links = getLinks(nameArticle)

