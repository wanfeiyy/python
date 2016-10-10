# import asyncio
# import logging
# import aiomysql
# @asyncio.coroutine
# def create_pool(loop,**kw):
#     logging.info('create database connection pool...')
#     global __pool
#     __pool = yield from aiomysql.create_pool(
#         host=kw.get('host', 'localhost'),  # 默认定义host名字为localhost
#         port=kw.get('port', 3306),  # 默认定义mysql的默认端口是3306
#         user=kw['user'],  # user是通过关键字参数传进来的
#         password=kw['password'],  # 密码也是通过关键字参数传进来的
#         db=kw['db'],  # 数据库的名字
#         charset=kw.get('charset', 'utf8'),  # 默认数据库字符集是utf8
#         autocommit=kw.get('autocommit', True),  # 默认自动提交事务
#         maxsize=kw.get('maxsize', 10),  # 连接池最多同时处理10个请求
#         minsize=kw.get('minsize', 1),  # 连接池最少1个请求
#         loop=loop  # 传递消息循环对象loop用于异步执行
#     )
#
# @asyncio.coroutine
# def select(sql,args,size=None):
#     log(sql.args)
#     global __pool
#     with (yield from __pool) as conn:
#         cur = yield from conn.cursor(aiomysql.DictCursor)
#         yield from cur.execute(sql.replace('?','%s'),args or ())
#         if size:
#             rs = yield from cur.fetchmany(size)
#         else:
#             rs = yield from cur.fetchall()
#         yield from cur.close()
#         logging.info('rows returned: %s' % len(rs))
#         return rs
#
#
# @asyncio.coroutine
# def execute(sql,args):
#     #log(sql)
#     with(yield from __pool) as conn:
#         try:
#             cur = yield from conn.cursor()
#             yield from cur.execute(sql.replace('?','%s'),args)
#             affected = cur.rowcount
#             yield from cur.close()
#         except BaseException as e:
#             raise
#         return affected
#
# @asyncio.coroutine
# def destory_pool():
#     global __pool
#     if __pool is not None:
#         __pool.close()
#         yield from __pool.wait_closed()
#
# def create_args_string(num):
#     L = []
#     for n in range(num):
#         L.append('?')
#     return ', '.join(L)
#
# class Field(object):
#
#     def __init__(self, name, column_type, primary_key, default):
#         self.name = name
#         self.column_type = column_type
#         self.primary_key = primary_key
#         self.default = default
#
#     def __str__(self):
#         return '<%s, %s, %s>' %(self.__class__.__name__,self.column_type, self.name)
#
# class StringField(Field):
#
#     def __init__(self, name=None, column_type = 'varchar(100)', primary_key = False, default = None):
#         super(StringField, self).__init__(name, column_type, primary_key, default)
#
# class IntegerField(Field):
#
#     def __init__(self, name=None, column_type = 'bigint', primary_key = False, default = None):
#         super(IntegerField, self).__init__(name, column_type, primary_key, default)
#
#
# class ModelMetaclass(type):
#
#     def __new__(cls, name, bases, attrs):
#         print (name,bases,attrs)
#         if name == 'Model':
#             return type.__new__(cls, name, bases, attrs)
#         tableName = attrs.get('__table__', None) or name
#         print('found model: %s(table:%s)' % (name, tableName))
#         #获取所有Field和主键名
#         mappings = dict()
#         fields = []
#         primaryKey = None
#         for k,v in attrs.items():
#             if isinstance(v,Field):
#                 print('founding mapping:%s ==> %s'%(k,v))
#                 mappings[k] = v
#                 if v.primary_key:
#                     #找到主键
#                     if primaryKey:
#                         #主键不能重复
#                         raise RuntimeError('Duplicate primary key for field:%s' %k)
#                     primaryKey = k
#                 else:
#                     fields.append(k)
#         if not primaryKey:
#             raise RuntimeError('primaryKey not found')
#         for k in mappings.keys():
#             attrs.pop(k)
#         escaped_fields = list(map(lambda f:'%s' %f, fields))
#         attrs['__mappings__'] = mappings
#         attrs['__table__'] = tableName
#         attrs['__primary_key__'] = primaryKey #主属性名
#         attrs['__fields__'] = fields #除主键外的属性名
#         attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
#         attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
#         attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
#         attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
#         return type.__new__(cls, name, bases, attrs)
#
# class Model(dict, metaclass = ModelMetaclass):
#     # 继承dict是为了使用方便，例如对象实例user['id']即可轻松通过UserModel去数据库获取到id
#     # 元类自然是为了封装我们之前写的具体的SQL处理函数，从数据库获取数据
#     def __init__(self, **kw):
#         # 调用dict的父类__init__方法用于创建Model,super(类名，类对象)
#         super(Model, self).__init__(**kw)
#
#     def __getattr__(self, key):
#         try:
#             return self[key]
#         except KeyError:
#             raise AttributeError(r"'Model' object has no attribute '%s'" % key)
#
#     def __setattr__(self, key, value):
#         self[key] = value
#
#     def getValue(self, key):
#         return getattr(self, key, None)
#
#     def getValueOrDefault(self, key):
#         value = getattr(self, key, None)
#         if value is None:
#             field = self.__mappings__[key]
#             if field.default is not None:
#                 value = field.default() if callable(field.default) else field.default
#                 logging.debug('using default value for %s:%s'%(key, str(value)))
#                 setattr(self, key, value)
#         return value
#
#     @asyncio.coroutine
#     def find(cls, pk):
#         'find object by primaryKey'
#         rs = yield from select('%s where %s = ?' % (cls.__select__, cls.__primary_key__), [pk], 1)
#         if len(rs) == 0:
#             return None
#         return cls(**rs[0])
#
#     @asyncio.coroutine
#     def save(self):
#         args = list(map(self.getValueOrDefault, self.__fields__))
#         args.append(self.getValueOrDefault(self.__primary_key__))
#         rows = yield from execute(self.__insert__, args)
#         print(rows)
#         if rows != 1:
#             logging.warn('failed to insert record:affected rows:%s' % rows)
#
#
# class User():
#     __table__ = 'members'
#     id = IntegerField(primary_key = True)
#     open_id = StringField()
#
#
#
# @asyncio.coroutine
# def test():
#     yield from create_pool(loop,user = 'root',password = 'gth123456.',db = 'weixin',host = '127.0.0.1')
#     u = User(id = None, open_id = 'obkNVs4hZ06IR4dJWMsj1IhagjvE')
#     yield from u.save()
#     yield from destory_pool()
#
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(test())
# loop.close()



import aiomysql
import asyncio
import sys
@asyncio.coroutine
def create_pool(loop, **kw):
    #logging.info('create database connection pool...')
    print('create database connection pool...')
    global __pool
    __pool = yield from aiomysql.create_pool(
    host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

@asyncio.coroutine
def select(sql, args, size=None):
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        # print (sql.replace('?','%s'))
        # sys.exit(0)
        yield from cur.execute(sql.replace('?','%s'), args or ())
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()
        #logging.info('rows returned: %s' % len(rs))
        return rs

@asyncio.coroutine
def execute(sql, args):
    #log(sql)
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected

def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)

class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s, %s>' %(self.__class__.__name__,self.column_type, self.name)

class StringField(Field):

    def __init__(self, name=None, column_type = 'varchar(255)', primary_key = False, default = None):
        super(StringField, self).__init__(name, column_type, primary_key, default)

class IntegerField(Field):

    def __init__(self, name=None, column_type = 'bigint', primary_key = False, default = None):
        super(IntegerField, self).__init__(name, column_type, primary_key, default)

class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name
        print('found model: %s(table:%s)' % (name, tableName))
        #获取所有Field和主键名
        mappings = dict()
        fields = []
        primaryKey = None
        for k,v in attrs.items():
            if isinstance(v,Field):
                print('founding mapping:%s ==> %s'%(k,v))
                mappings[k] = v
                if v.primary_key:
                    #找到主键
                    if primaryKey:
                        #主键不能重复
                        raise RuntimeError('Duplicate primary key for field:%s' %k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('primaryKey not found')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f:'%s' %f, fields))
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey #主属性名
        attrs['__fields__'] = fields #除主键外的属性名
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)

class Model(dict, metaclass = ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s:%s'%(key, str(value)))
                setattr(self, key, value)
        return value

    @asyncio.coroutine
    def find(cls, pk):
        #sys.exit(0)
        'find object by primaryKey'
        rs = yield from select('%s where %s = ?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return rs[0]

    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        print(rows)
        if rows != 1:
            logging.warn('failed to insert record:affected rows:%s'%rows)


    @asyncio.coroutine
    def findAll(cls,where = None,args = None,**kw):
        # 初始化SQL语句和参数列表
        sql = [cls.__select__]
        if args is None:
            args = []
            # WHERE查找条件的关键字
        if where:
            sql.append('where ')
            sql.append(where)
        if kw.get('orderBy') is not None:
            sql.append('order by %s' % (kw['orderBy']))
        limit = kw.get('limit')
        if limit is not None:
            if isinstance(limit,int):
                sql.append('limit')
                args.append(limit)
            elif isinstance(limit,tuple) and len(limit) == 2:
                sql.append('limit ?,?')
                args.append(limit)
            else:
                raise ValueError('Invalid limit value: %s' % limit)
        print (sql,args)
        rs = yield from select(' '.join(sql), args)
        return rs
        #rs = yield from select('%s where %s = ?' % (cls.__select__, cls.__primary_key__))
@asyncio.coroutine
def destory_pool():
    global __pool
    if __pool is not None:
        __pool.close()
        yield from __pool.wait_closed()

class Member(Model):
    __table__ = 'members'
    id = IntegerField(primary_key = True)
    open_id = StringField()

def test():
    yield from create_pool(loop, user='root', password='gth123456.', db='weixin', host='127.0.0.1')
    user = Member()
    rs = yield from user.findAll(limit = 2 )
    print (rs)
    yield from destory_pool()
loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()



