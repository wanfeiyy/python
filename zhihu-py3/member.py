from zhihu.io_db import create_pool,destory_pool
from member_model import Member
import asyncio
from zhihu.client import ZhihuClient
class followees():
    @asyncio.coroutine
    def insert_db(self,followees_url):
        Cookies_File = 'cookies.json'
        client = ZhihuClient(Cookies_File)
        member = client.author(followees_url)
        like = member.followees
        if like is not  None:
            followees_count = len(like)
            yield from create_pool(loop, user='root', password='gth123456.', db='weixin', host='127.0.0.1')
            for v in like:
                u = Member(id=None,name=v._name,motto=v._motto,
                            url=v.url,photo_url=v._photo_url,
                            weibo_url=v.weibo_url,business=v.business,
                            education=v.education,gender=v.gender,
                            location=v.location
                           )
                yield from u.save()
            yield from destory_pool()

followees = followees()
loop = asyncio.get_event_loop()
loop.run_until_complete(followees.test())
loop.close()





