# -*- coding: utf-8 -*-
'''
网络爬虫之用户名密码及验证码登陆：爬取知乎网站
'''
import requests
import configparser
from bs4 import BeautifulSoup

def create_session():
    cf = configparser.ConfigParser()
    cf.read('config.ini')
    cookies = cf.items('cookies')
    cookies = dict(cookies)
    from pprint import pprint
    #pprint(cookies)
    phone_num  = cf.get('info', 'phone_num')
    password = cf.get('info', 'password')

    session = requests.Session()
    login_data = {'phone_num':phone_num , 'password': password}
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36',
        'Host': 'www.zhihu.com',
        'Referer': 'http://www.zhihu.com/'
    }
    r = session.post('http://www.zhihu.com/login/phone_num', data=login_data, headers=header)
    if r.json()['r'] == 1:
        print ('Login Failed, reason is:'),
        for m in r.json()['data']:
            print (r.json()['data'][m])
        print ('So we use cookies to login in...')
        has_cookies = False
        for key in cookies:
            if key != '__name__' and cookies[key] != '':
                has_cookies = True
                break
        if has_cookies is False:
            raise ValueError('请填写config.ini文件中的cookies项.')
        else:
            # r = requests.get('http://www.zhihu.com/login/email', cookies=cookies) # 实现验证码登陆
            r = session.get('http://www.zhihu.com/login/email',headers = header, cookies=cookies) # 实现验证码登陆

    with open('login.html', 'w') as fp:
        fp.write(r.content.decode('utf-8'))

    return session, cookies

def getUserName(cookies):
    content = requests.get('https://www.zhihu.com/', cookies=cookies)
    #bsObj = BeautifulSoup(content,'html.parser')
    #userNameInfo = bsObj.find('div',{'class':'top-nav-profile'})
    #print (content.content)

if __name__ == '__main__':
    requests_session, requests_cookies = create_session()
    #print (requests_session.text)
    #print (requests_session.cookies)
    #getUserName(requests_cookies)
    # url = 'http://www.zhihu.com/login/email'
    url = 'http://www.zhihu.com/topic/19552832'
    # # content = requests_session.get(url).content # 未登陆
    #content = requests.get(url, cookies=requests_cookies).content # 已登陆

    # content = requests_session.get(url, cookies=requests_cookies).content # 已登陆
    # with open('url.html', 'w') as fp:
    #     fp.write(content)
