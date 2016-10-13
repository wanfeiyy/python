import aiomysql
import asyncio
import sys
import logging
import importlib
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
            print (sql.replace('?', '%s'), args)
            try:
                yield from cur.execute(sql.replace('?', '%s'), args)
            except TypeError:
               print ('请检查参数！')
               destory_pool()
               sys.exit(0)
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
    def __new__(cls, name, bases, attrs,**kw):
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
        fillable = attrs.get('fillable')
        hanleFillable = []
        if fillable is not None and isinstance(fillable,list):
            for x in fillable:
                 if x in fields:
                     hanleFillable.append(x)
        escaped_fields = list(map(lambda f:'%s' %f, hanleFillable if len(hanleFillable) else fields))
        attrs['__auto__'] = attrs.get('auto')
        attrs['__fillable__'] = hanleFillable
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey #主属性名
        attrs['__fields__'] = fields #除主键外的属性名
        attrs['__select__'] = 'select `%s`, %s  from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        #print(','.join(map(lambda f:f.replace(f,f+'=?'),fields)))
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        # print (attrs)
        # sys.exit(0)
        return type.__new__(cls, name, bases, attrs)

class Model(dict, metaclass = ModelMetaclass):
    def __init__(self, **kw):
        print (1)
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
                #logging.debug('using default value for %s:%s'%(key, str(value)))
                setattr(self, key, value)
        return value

    def autoComplete(cls):
        auto = cls.__auto__
        auto_data = {}
        if len(auto) == 0:
            return auto_data
        for item in auto:
            if len(item) == 2:
                auto_data[item[0]] = item[1]
            elif len(item) == 3:
                me_def = ''.join(item[-1:])
                if me_def == 'callback':
                    func = item[1]
                    auto_data[item[0]] = getattr(cls,func,'default')()
                elif me_def == 'def':
                    try:
                        handle_def = item[1]
                        module = handle_def.split('.')[0]
                        use_def = handle_def.split('.')[1]
                        me_import = importlib.import_module(module)
                    except ImportError:  # 如果导入失败，即配置文件不存在，系统推出
                        logging.info("导入"+module+"失败")
                        destory_pool()
                        sys.exit()
                    auto_data[item[0]] = getattr(me_import,use_def)()
        return auto_data

    @asyncio.coroutine
    def find(cls, pk):
        #sys.exit(0)
        'find object by primaryKey'
        rs = yield from select('%s where %s = ?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return rs[0]

    @asyncio.coroutine
    def save(cls):
        cls.autoComplete()
        args = list(map(cls.getValueOrDefault, cls.__fillable__ if len(cls.__fillable__)  else cls.__fields__))
        args.append(cls.getValueOrDefault(cls.__primary_key__))
        rows = yield from execute(cls.__insert__, args)
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
    test = StringField()
    password = StringField()
   #fillable = ['open_id','password','test']
    auto = [['password','encrypt','callback'],['created_at','time.time','def'],['status',0]]
    def encrypt(self):
        return 'encrypt'
def test():
    yield from create_pool(loop, user='root', password='gth123456.', db='weixin', host='127.0.0.1')
    user = Member(password ='123456',open_id='3333',test='ssdd')
    rs = yield from user.save()
    #print (rs)
    yield from destory_pool()
loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()



