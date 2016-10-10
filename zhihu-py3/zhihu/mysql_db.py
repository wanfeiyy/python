import pymysql
class db():

    def __init__(self,host='127.0.0.1',username=None,passwd=None,dbname=None,type='mysql',charset='utf8',db=None):
        self.host = host
        self.username = username
        self.passwd = passwd
        self.dbname = dbname
        self.type = type
        self.charset = charset
        self.db = self._connect()
    def _connect(self):
        conn = pymysql.connect(self.host,self.username,self.passwd,self.db,self.charset)
        return conn.cursor()

    def insert_data(self,data):
        pass

    def _destory(self):
        self.db.close()



