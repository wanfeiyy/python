from zhihu.io_db import *
class Member(Model):
    __table__ = 'zhihu'
    id = IntegerField(primary_key = True)
    name = StringField()
    motto = StringField()
    url = StringField()
    photo_url = StringField()
    weibo_url = StringField()
    business = StringField()
    location = StringField()
    education = StringField()
    gender = StringField(column_type='varchar(8)')