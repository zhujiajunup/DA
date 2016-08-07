__author__ = 'jjzhu'

import pymysql
import time
import numpy as np


class MysqlConnection:
    def __init__(self, db, host=u'localhost', port=3306, user=u'root', passwd=u'123456', charset=u'utf8'):
        self.connection = pymysql.connect(db=db, host=host, port=port, user=user, passwd=passwd, charset=charset)
        self.cur = self.connection.cursor()

    def execute_single(self, sql, args=None):
        self.cur.execute(sql, args)
        self.connection.commit()

    def execute_many(self, sql, args):
        self.cur.executemany(sql, args)
        self.connection.commit()

    def select_query(self, sql):
        result = []
        self.cur.execute(sql)
        for item in self.cur:
            result.append(item)
        return result

    def exist(self, sql):
        return self.cur.execute(sql)

    def close(self):
        self.cur.close()
        self.connection.close()


def main():
    conn = MysqlConnection(db='weibo')
    user_id = '2210643391'
    select_sql = 'select * from weibo.blog where blog_user_id="2447680824"'
    select_sql = 'select count(*) from weibo.blog where blog_user_id='+user_id+' and blog_created_at > "2015"' \
                                                                               ' and blog_created_at < "2016"'
    select_sql = 'select blog_created_at from weibo.blog where blog_user_id='+user_id\
                 + ' order by blog_created_at asc limit 1'
    result = conn.select_query(select_sql)
    first_blog_time_str = result[0][0]
    first_blog_time = time.strptime(first_blog_time_str, '%Y-%m-%d %H:%M:%S')
    year_diff = time.localtime().tm_year - first_blog_time.tm_year
    x_label = [first_blog_time.tm_year + i for i in range(year_diff+1)]
    y_label = []
    for x in x_label:
        select_sql = 'select count(*) from weibo.blog where blog_user_id='+user_id+' and blog_created_at >= '+\
                     str(x) + ' and blog_created_at < '+str(x+1)
        result = conn.select_query(select_sql)
        y_label.append(result[0][0])

    print(np.sum(y_label))
    print(y_label)

if __name__ == '__main__':
    main()