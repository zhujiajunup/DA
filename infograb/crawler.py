__author__ = 'jjzhu'
# -*- coding:utf-8 -*-
import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import json
import re
import pymysql
import datetime

from grabutil import mysqlconnection as mysqlconn
position_default_url = "http://www.lagou.com/jobs/"

conn = mysqlconn.Connection('position_info')
to_add_infos = []  # 待添加的职位信息，用于数据的批量插入
max_count = 10  # 批量数
query = "insert into position_info.position(city, companyId, companyLabelList, companyName,  companyShortName, " \
        "companySize, education, financeStage, industryField, jobNature, leaderName, positionAdvantage," \
        "positionFirstType, positionId, positionName, positionType, pvScore, workYear, salary_min, salary_max," \
        "homepage, positionDescibe)" \
        " values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"


def make_my_opener():
    """
    模拟浏览器发送请求
    :return:
    """
    head = {
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener


def grab_city():
    """
    获取所有的城市
    :return:
    """
    seed_url = 'http://www.lagou.com/zhaopin/'
    my_opener = make_my_opener()
    op = my_opener.open(seed_url)
    my_soup = BeautifulSoup(op.read().decode(), 'html.parser')
    all_positions_html = my_soup.find(class_='more more-positions')
    all_positions_hrefs = all_positions_html.find_all('a')
    all_cities = []
    for a_tag in all_positions_hrefs:
        all_cities.append(a_tag.contents[0])
    return all_cities


def grab_position():
    """
    获取所有招聘职位
    :return:
    """
    lagou_url = "http://www.lagou.com/"
    html = urllib.request.urlopen(lagou_url)
    soup = BeautifulSoup(html, "html.parser")
    side_bar = soup.find(id="sidebar")
    mainNavs = side_bar.find(class_="mainNavs")
    menu_boxes = mainNavs.find_all(class_="menu_box")
    all_positions = []
    for menu_box in menu_boxes:
        menu_sub = menu_box.find(class_="menu_sub")  # 所有职位
        all_a_tags = menu_sub.find_all("a")  #  找出所有职位的a标签
        for a_tag in all_a_tags:
            all_positions.append(a_tag.contents[0])
    return all_positions


def grab_detail(url):
    html_detail = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_detail, "html.parser")
    return soup


def connect_to_mysql(db, host=u'localhost', port=3306, user=u'root', passwd=u'', charset=u'utf8'):
    return pymysql.connect(db=db, host=host, port=port, user=user, passwd=passwd, charset=charset)


def change_salary(salary):
    salaries = re.findall("\d+", salary)
    if salaries.__len__() == 0:
        return 0, 0
    elif salaries.__len__() == 1:
        return int(salaries[0])*1000, int(salaries[0])*1000
    else:
        return int(salaries[0])*1000, int(salaries[1])*1000


def position_detail(position_id):
    my_opener = make_my_opener()
    position_url = position_default_url + str(position_id)+".html"
    print(position_url)

    op = my_opener.open(position_url, timeout=1000)
    detail_soup = BeautifulSoup(op.read().decode(), 'html.parser')
    job_company = detail_soup.find(class_='job_company')
    job_detail = detail_soup.find(id='job_detail')
    job_req = job_detail.find(class_='job_bt')
    c_feature = job_company.find(class_='c_feature')
    homePage = c_feature.find('a')
    homeUrl = homePage.get('href')
    return job_req, homeUrl


def insert_into_database(result):
    city = result['city']
    companyId = result['companyId']
    companyLabelList = result['companyLabelList']
    companyLabel = ''
    for lable in companyLabelList:
        companyLabel += lable+" "
    companyName = result['companyName']
    companyShortName = result['companyShortName']
    companySize = result['companySize']
    education = result['education']
    financeStage = result['financeStage']
    industryField = result['industryField']
    jobNature = result['jobNature']
    leaderName = result['leaderName']
    positionAdvantage = result['positionAdvantage']
    positionFirstType = result['positionFirstType']
    positionId = result['positionId']
    job_req, homeUrl = position_detail(positionId)  # 获取信息
    positionName = result['positionName']
    positionType = result['positionType']
    pvScore = result['pvScore']
    salary = result['salary']
    salaryMin, salaryMax = change_salary(salary)
    workYear = result['workYear']
    '''
    print(city, companyId, companyLabel, companyName,  companyShortName, companySize,
          education, financeStage, industryField, jobNature, leaderName, positionAdvantage,
          positionFirstType, positionId, positionName, positionType, pvScore, salary, workYear)
    '''
    to_add_infos.append((city, str(companyId), companyLabel, companyName,  companyShortName, companySize,
                         education, financeStage, industryField, jobNature, leaderName, positionAdvantage,
                         positionFirstType, positionId, positionName, positionType, pvScore, workYear, salaryMin,
                         salaryMax, homeUrl, str(job_req)))
    if to_add_infos.__len__() >= max_count:
        conn.execute_many(sql=query, args=to_add_infos)
        to_add_infos.clear()


def grab_category(city, kd):
    url = "http://www.lagou.com/jobs/positionAjax.json?city="+urllib.parse.quote(city)
    url.encode(encoding='utf-8')
    my_opener = make_my_opener()
    pn = 1
    postdata = urllib.parse.urlencode({'first': 'true', 'pn': pn, 'kd': kd}).encode()
    pn += 1
    op = my_opener.open(url, postdata)
    return_json = json.loads(op.read().decode())
    content_json = return_json['content']
    total_page = content_json['totalPageCount']

    result_list = content_json['result']
    for result in result_list:
        insert_into_database(result)
    while pn < total_page:
        start = datetime.datetime.now()
        print("--------职位："+kd+"--------"+"城市："+city+"---------")
        print("当前页："+str(pn))
        postdata = urllib.parse.urlencode({'first': 'false', 'pn': pn, 'kd': kd}).encode()
        pn += 1
        op = my_opener.open(url, postdata)
        return_json = json.loads(op.read().decode())
        content_json = return_json['content']

        result_list = content_json['result']
        for result in result_list:
            insert_into_database(result)
        end = datetime.datetime.now()
        print('当前页耗时：'+str((end-start).seconds))
    print('successful')


def main():
    all_cities = grab_city()
    all_positions = grab_position()
    grabed_cities_file = open("d:\\grabed_cities.txt", 'a')
    for i in range(1, 2):
        start_time = datetime.datetime.now()
        for j in range(0, int(all_positions.__len__()/2)):
            grab_category(city=all_cities[i], kd=all_positions[j])
        end_time = datetime.datetime.now()
        print((end_time-start_time).seconds)
        grabed_cities_file.write(all_cities[i]+"----耗时："+str((end_time-start_time).seconds)+"s\n")
    conn.close()
    print("----------finish--------------")
    '''
    start_time = datetime.datetime.now()
    all_cities = grab_city()
    all_positions = grab_position()
    for position in all_positions:

        for city in all_cities:
            if city == '全国':
                continue
            print(city+"--------职位："+position+"--------"+"城市："+city+"---------")
            grab_category(city=city, kd=position)
    end_time = datetime.datetime.now()
    print((end_time-start_time).seconds)
    '''
if __name__ == '__main__':
    main()
