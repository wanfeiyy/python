from zhihu.io_db import create_pool,destory_pool
import asyncio
from zhihu.client import ZhihuClient
from member_model import Member
import sys
class followees():
    @asyncio.coroutine
    def insert_db(self,followees_url):
        Cookies_File = 'cookies.json'
        client = ZhihuClient(Cookies_File)
        member = client.author(followees_url)
        like = member.followees
        u = Member()
        if like is not  None:
            yield from create_pool(loop, user='root', password='gth123456.', db='weixin', host='127.0.0.1')
            for v in like:
                member_url = v.url
                print ('获取的url：'+member_url)
                find_log =yield from u.findAll(where="url = '"+member_url+"'",column=['name','id'],limit=1)
                if len(find_log):
                    continue
                else:
                    u = Member(id=None,name=v._name,motto=v._motto,
                                url=v.url,photo_url=v._photo_url,
                                weibo_url=v.weibo_url,business=v.business,
                                education=v.education,gender=v.gender,
                                location=v.location
                               )
                    yield from u.save()
            self.insert_db(member_url)
            yield from destory_pool()

followees = followees()
loop = asyncio.get_event_loop()
loop.run_until_complete(followees.insert_db('https://www.zhihu.com/people/renxingjie/'))
loop.close()





