# import re
# from bs4 import BeautifulSoup
# str = '<a target="_blank" href="/people/yinjie1218" class="zg-link-gray-normal">78016 赞同</a>'
# re_get_number = re.compile(r'^(\d+).*')
# html = BeautifulSoup(str,'lxml')
# #print ()
# for x in html.findAll('a',class_="zg-link-gray-normal"):
#     print  (re_get_number.match(x.text).group(1))


# member = [
#     int (re_get_number.match(x.text).group(1)) for x in html.findAll('a', class_="zg-link-gray-normal")
# ]
# print (member)

def a ():
    return 1,2,3
print(a())
