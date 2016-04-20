__author__ = 'jjzhu'
from grabutil.mysqlconnection import MysqlConnection
import time
import numpy as np
import datetime
import calendar
import matplotlib.pyplot as plt
conn = MysqlConnection(db='weibo')


def year_detail(year, user_id='2210643391'):
    x = [i+1 for i in range(12)]
    y = []
    x_tick_label = []
    x_tick_label.append('')
    for i in range(12):
        x_tick_label.append(str(i+1) + '月')
    for i in range(12):

        start_time = str(datetime.date(year, i+1, 1))
        if i+1 is 12:
            end_time = str(datetime.date(year+1, 1, 1))
        else:
            end_time = str(datetime.date(year, i+2, 1))
        select_sql = 'select count(*) from weibo.blog where blog_user_id=\''+user_id+'\' and blog_created_at >= \''+\
                     start_time+'\' and blog_created_at < \''+end_time + '\''
        print(select_sql)
        result = conn.select_query(select_sql)
        y.append(result[0][0])
    plt.xticks([i for i in range(13)])
    for i in range(x.__len__()):
        plt.plot([x[i], x[i]], [0, y[i]], '-.r')
        # plt.plot([0, x[i]], [y[i], y[i]], '-.r')
        plt.annotate(str(y[i]), xy=(x[i], y[i]),
                     xycoords='data', xytext=(+10, +20),  textcoords='offset points', fontsize=12,
                     arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    plt.title(str(year)+'年各月的微博数折线图')
    plt.xlim((0, 13))
    plt.ylim(np.min(y)-10, np.max(y)+10)
    print(x)
    plt.plot(x, y, '-b')
    ax = plt.gca()
    ax.set_xticklabels(x_tick_label)
    plt.savefig('year_'+str(year)+'_detail')
    plt.show()

    # print(x)
    # print(y)

def main():

    user_id = '2210643391'
    select_sql = 'select * from weibo.blog where blog_user_id="2447680824"'
    select_sql = 'select count(*) from weibo.blog where blog_user_id='+user_id+' and blog_created_at > "2015"' \
                                                                               ' and blog_created_at < "2016"'
    select_sql = 'select blog_created_at from weibo.blog where blog_user_id='+user_id+' order by blog_created_at asc limit 1'
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
    # plt.xticks(np.arange(year_diff+1), [str(i) for i in x_label])

    plt.plot(x_label, y_label, '-b')
    plt.ylim(np.min(y_label)-100, np.max(y_label)+100)
    for i in range(x_label.__len__()):
        plt.plot([x_label[i], x_label[i]], [0, y_label[i]], '-.r')
        if i is 0:
            x_off = -20
        else:
            x_off = +10
        plt.annotate(str(y_label[i]), xy=(x_label[i], y_label[i]),
                     xycoords='data', xytext=(x_off, +20),  textcoords='offset points', fontsize=12,
                     arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    ax = plt.gca()
    plt.xlim(2011, 2017)
    ax.set_xticklabels([first_blog_time.tm_year - 1 + i for i in range(year_diff+2)])
    print(x_label)
    print(y_label)
    plt.xlabel('年份')
    plt.ylabel('微博数')
    plt.savefig('weibo')
    plt.show()


if __name__ == '__main__':
    year_detail(2013)
    conn.close()