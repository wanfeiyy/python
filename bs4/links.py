from urllib.request import urlopen
from urllib.error import HTTPError,URLError
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import datetime
import random
import threading
import os
pages = set()
random.seed(datetime.datetime.now())
allExtLinks = set()
allIntLinks = set()
def getInternalLinks(bsObj,includUrl):
    includUrl = urlparse(includUrl).scheme+"://"+urlparse(includUrl).netloc
    internalLinks = []
    dom = bsObj.findAll("a",href = re.compile("^(/|.*"+includUrl+")"))
    for link in dom:
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in internalLinks:
                if(link.attrs['href'].startswith('/')):
                    internalLinks.append(includUrl+link.attrs['href'])
                else:
                    internalLinks.append(link.attrs['href'])
    return internalLinks

def getExteralLinks(bsObj,excludeUrl):
    exteralLinks = []

    dom = bsObj.findAll("a",href = re.compile("^(http|www)((?!"+excludeUrl+").)*$"))
    for link in dom:
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in exteralLinks:
                exteralLinks.append(link.attrs['href'])
    return exteralLinks

def getRandomExternalLink(startingPage):
    html = urlopen(startingPage)
    bsObj = BeautifulSoup(html.read(),"html.parser")
    externalLinks = getExteralLinks(bsObj,urlparse(startingPage).netloc)
    if len(externalLinks) == 0:
        print ('No External Links')
        domain = urlparse(startingPage).scheme+"://"+urlparse(startingPage).netloc
        internalLinks = getInternalLinks(bsObj,domain)
        return getRandomExternalLink(internalLinks[random.randint(0,len(internalLinks)-1)])
    else:
        return externalLinks[random.randint(0,len(externalLinks)-1)]
def followExternalOnly(domain):
    externaLink = getRandomExternalLink(domain)
    print ("From "+threading.current_thread().name+" Random external link is :"+externaLink)
    followExternalOnly(domain)

def splitAddress(address):
    addressParts = address.replace("http://","").split('/')
    return addressParts
def getAllExternalLinks(domain):
    try:
        html = urlopen(domain)
    except(HTTPError,URLError) as e:
        print ('url error')
        os._exit(0)
    except  ValueError as e:
        print ('url error')
        os._exit(0)
    bsObj = BeautifulSoup(html.read(), "html.parser")
    externalLinks = getExteralLinks(bsObj,splitAddress(domain)[0])
    internalLinks = getInternalLinks(bsObj,splitAddress(domain)[0])
    for link in externalLinks:
        if link not in allExtLinks:
            allExtLinks.add(link)
            print (link)
    for link in internalLinks:
        if link not in allIntLinks:
            print("WILL URL:"+link)
            allIntLinks.add(link)
            getAllExternalLinks(link)
getAllExternalLinks('http://www.bilibili.com')
