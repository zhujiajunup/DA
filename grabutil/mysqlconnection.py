__author__ = 'jjzhu'

import pymysql


class MysqlConnection:
    def __init__(self, db, host=u'localhost', port=3306, user=u'root', passwd=u'', charset=u'utf8'):
        self.connection = pymysql.connect(db=db, host=host, port=port, user=user, passwd=passwd, charset=charset)
        self.cur = self.connection.cursor()

    def execute_single(self, sql, args=None):
        self.cur.execute(sql, args)
        self.connection.commit()

    def execute_many(self, sql, args):
        self.cur.executemany(sql, args)
        self.connection.commit()

    def exist(self, sql):
        return self.cur.execute(sql)

    def close(self):
        self.cur.close()
        self.connection.close()
