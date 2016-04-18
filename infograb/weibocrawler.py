__author__ = 'Administrator'

import http.cookiejar
import urllib.request
import urllib.parse
import json
from grabutil.mysqlconnection import MysqlConnection
import redis
import os


class WeiboCrawler:
    def __init__(self, user, password, db='weibo'):
        self.user = user
        self.password = password
        self.opener = self.make_my_opener()
        self.index = 0
        self.login_url = 'https://passport.weibo.cn/sso/login'
        self.mysqlconn = MysqlConnection(db=db)
        self.proxies = [{"HTTP": "58.248.137.228:80"}, {"HTTP": "58.251.132.181:8888"}, {"HTTP": "60.160.34.4:3128"},
                        {"HTTP": "60.191.153.12:3128"}, {"HTTP": "60.191.164.22:3128"}, {"HTTP": "80.242.219.50:3128"},
                        {"HTTP": "86.100.118.44:80"}, {"HTTP": "88.214.207.89:3128"}, {"HTTP": "91.183.124.41:80"},
                        {"HTTP": "93.51.247.104:80"}]
        self.user_insert_query = 'insert into weibo.user(user_id, description, fans_num, screen_name,' \
                                 ' statuses_count, follow_num, profile_image_url, profile_url) value ' \
                                 '(%s, %s, %s, %s, %s, %s, %s, %s)'
        self.blog_insert_query = 'insert into weibo.blog(blog_id, blog_text, blog_source, blog_created_at, ' \
                                 'blog_created_timestamp, blog_like_count, blog_comment_count, ' \
                                 'blog_forward_count, blog_pic_ids, blog_retweet_id, blog_user_id) value (%s, %s, %s, %s, %s, ' \
                                 '%s, %s, %s, %s, %s, %s)'
        self.comment_insert_query = 'insert into weibo.comment(comment_id, comment_text, created_at,' \
                                    ' like_counts, comment_user_id) value(%s, %s, %s, %s, %s)'
        self.pic_insert_query = 'insert into weibo.picture(pic_id, pic_url) value (%s, %s)'
        self.head = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Host': 'm.weibo.cn',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        # self.seed = 'http://m.weibo.cn/login?ns=1&backURL=http%3A%2F%2Fm.weibo.cn%2F&backTitle=%CE%A2%B2%A9&vt=4&'

    def change_proxy(self):
        proxy_handler = urllib.request.ProxyHandler(self.proxies[self.index % self.proxies.__len__()])
        print("换代理了..."+str(self.proxies[self.index % self.proxies.__len__()]))
        self.index += 1
        if self.index >= 1000:
            self.index = 0
        # proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()

        self.opener.add_handler(proxy_handler)

    def login(self):
        args = {
            'username': '767543579@qq.com',
            'password': 'QWErty',
            'savestate': 1,
            'ec': 0,
            'pagerefer': 'https://passport.weibo.cn/signin/'
                         'welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F&wm=3349&vt=4',
            'entry': 'mweibo',
            'wentry': '',
            'loginfrom': '',
            'client_id': '',
            'code': '',
            'qq': '',
            'hff': '',
            'hfp': ''
        }

        post_data = urllib.parse.urlencode(args).encode()
        try:
            self.opener.open(self.login_url, post_data)
            print("login successful")
        except Exception:
            print("login failed")

    def make_my_opener(self):
        """
        模拟浏览器发送请求
        :return:
        """
        head = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'Content-Length': '254',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'passport.weibo.cn',
            'Origin': 'https://passport.weibo.cn',
            'Referer': 'https://passport.weibo.cn/signin/login?'
                       'entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML,'
                          ' like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        header = []
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        opener.addheaders = header
        return opener

    def change_header(self):
        head = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Host': 'm.weibo.cn',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        header = []
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        self.opener.addheaders = header

    def insert_blog_info(self, blog_info):
        print('insert blog info '+str(blog_info))
        if blog_info.__contains__('deleted'):
            return
        blog_id = blog_info['idstr']

        blog_text = blog_info['text']
        blog_source = blog_info['source']
        blog_create_at = blog_info['created_at']
        blog_created_timestamp = blog_info['created_timestamp']
        blog_like_count = blog_info['like_count']
        blog_comment_count = blog_info['comments_count']
        blog_forward_conut = blog_info['attitudes_count']  # TODO
        blog_pic_ids = ''
        if blog_info.__contains__('pics'):
            blog_pictures = blog_info['pics']

            for pic in blog_pictures:
                self.insert_pic_info(pic)
                blog_pic_ids += pic['pid']+','
        blog_retweet_id = ''
        if blog_info.__contains__('retweeted_status'):
            self.insert_blog_info(blog_info['retweeted_status'])
            blog_retweet_id += blog_info['retweeted_status']['idstr']
        if self.insert_user_info(blog_info['user']):
            self.mysqlconn.execute_single(self.blog_insert_query, (blog_id, blog_text, blog_source, blog_create_at,
                                                                   blog_created_timestamp, blog_like_count,
                                                                   blog_comment_count, blog_forward_conut, blog_pic_ids,
                                                                   blog_retweet_id, blog_info['user']['id']))
        pass

    def insert_pic_info(self, pic_info):
        pic_id = pic_info['pid']
        pic_url = pic_info['url']
        self.mysqlconn.execute_single(self.pic_insert_query, (pic_id, pic_url))
        pass

    def insert_user_info(self, user_info):
        print("user info "+str(user_info))
        user_id = user_info['id']
        if user_id is None:
            return False
        description = user_info['description']
        fans_num = str(user_info['fansNum'])
        screen_name = user_info['screen_name']
        statuses_count = str(user_info['statuses_count'])
        follow_num = '0'  # user_info['follow_num']
        profile_image_url = user_info['profile_image_url']
        profile_url = user_info['profile_url']
        if self.mysqlconn.exist("select * from weibo.user where user_id="+str(user_id)):
            update_query = 'update weibo.user set description="'+description+'",fans_num="'+fans_num +\
                           '",screen_name="'+screen_name+'",statuses_count="'+statuses_count+'",follow_num="'\
                           + follow_num + '",profile_image_url="'+profile_image_url+'",profile_url="'\
                           + profile_url+'" where user_id='+str(user_id)
            print(update_query)
            self.mysqlconn.execute_single(update_query)
        else:
            self.mysqlconn.execute_single(self.user_insert_query, (user_id, description, fans_num, screen_name,
                                                                   statuses_count, follow_num, profile_image_url,
                                                                   profile_url))
        return True

    def insert_comment_info(self, comment_info):
        pass

    def grab_user_blogs(self):
        end = False
        page = 1
        while not end:
            url = 'http://m.weibo.cn/page/json?containerid=1005052210643391_-_WEIBO_SECOND_PROFILE_WEIBO&page='+str(page)
            page += 1
            if page % 5 == 0:  # 换代理
                self.change_proxy()
            print("正在打开："+url)
            rsp = self.opener.open(url)
            return_json = json.loads(rsp.read().decode())
            print('返回数据：'+str(return_json))
            cards = return_json['cards']
            for card in cards:
                if card.__contains__('msg'):
                    end = True
                    break
                card_group = card['card_group']

                for blog_info in card_group:
                    if blog_info['card_type'] != 9:
                        continue
                    # print(blog_info['mblog'])
                    self.insert_blog_info(blog_info['mblog'])

    def start(self):
        self.login()
        self.change_header()
        self.grab_user_blogs()
        # self.grab_weibo()
        # self.save_pic()

    def save_pic(self):
        url = 'http://ww2.sinaimg.cn/large/c0788b86jw1f2xfstebzaj20dc0hst9r.jpg'
        rsp = self.opener.open(url)
        pic_data = rsp.read()
        try:
            file = open("d:\\weibo_pic\\1.jpg", 'wb')
            file.write(pic_data)
            file.close()
        except FileNotFoundError:
            os.mkdir("d:\\weibo_pic")
        except FileExistsError:
            pass

    def get_comment_by_page(self, blog_id, page_num):
        url = 'http://m.weibo.cn/single/rcList?format=cards&id='
        req_url = url + str(blog_id) + '&type=comment&hot=0&page='+str(page_num)
        print('浏览器正在打开url：'+req_url)
        rsp = self.opener.open(req_url)
        return_json = json.loads(rsp.read().decode())
        print('请求返回数据:\t'+str(return_json))
        if page_num == 1:
            comment_json = return_json[1]
        else:
            comment_json = return_json[0]
        return comment_json

    def grab_comment(self, blog_id):
        page = 1
        comment_json = self.get_comment_by_page(blog_id, page)
        print('评论——json\t' + str(comment_json))
        if 'maxPage' not in comment_json:
            return
        max_page = comment_json['maxPage']
        page += 1
        if 'card_group' in comment_json:
            comment_card_group = comment_json['card_group']
            for comment_group in comment_card_group:
                self.print_comment(comment_group)
        print("总页面数：max_page：\t"+str(max_page))
        while page <= max_page:
            print("curr_page:\t"+str(page)+"\t    max_page\t:"+str(max_page))
            comment_json = self.get_comment_by_page(blog_id, page)
            if 'card_group' in comment_json:
                comment_card_group = comment_json['card_group']
                for comment_group in comment_card_group:
                    self.print_comment(comment_group)
            page += 1

    def grab_weibo(self):
        open_url = 'http://m.weibo.cn/index/feed?format=cards'
        print('浏览器正在打开url：' + open_url)
        rsp = self.opener.open(open_url)
        return_json = json.loads(rsp.read().decode())
        card_group = return_json[0]['card_group']
        next_cursor = return_json[0]['next_cursor']
        previous_cursor = return_json[0]['previous_cursor']
        page = return_json[0]['page']
        max_page = return_json[0]['maxPage']
        page = 1

        c = '3963770537235924&type=comment&hot=0&page=2'
        for group in card_group:
            self.print_info(group)
            mblog = group['mblog']
            curr_blog_id = mblog['id']
            user = mblog['user']
            user_id = user['id']
            self.grab_comment(curr_blog_id)
            # page += 1

        n = 20
        while n > 0:
            n -= 1
            open_url = 'http://m.weibo.cn/index/feed?format=cards&next_cursor='+str(next_cursor) + '&page='+str(page)
            print('浏览器正在打开url：' + open_url)
            rsp = self.opener.open(open_url)
            return_json = json.loads(rsp.read().decode())
            card_group = return_json[0]['card_group']
            next_cursor = return_json[0]['next_cursor']
            previous_cursor = return_json[0]['previous_cursor']
            for group in card_group:
                self.print_info(group)
                mblog = group['mblog']
                curr_blog_id = mblog['id']
                user = mblog['user']
                user_id = user['id']
                self.grab_comment(curr_blog_id)
        return

    def print_info(self, group):
        mblog = group['mblog']
        text = mblog['text']
        user = mblog['user']
        created_at = mblog['created_at']
        comments_count = mblog['comments_count']
        like_count = mblog['like_count']
        reposts_count = mblog['reposts_count']
        screen_name = user['screen_name']
        fansNum = user['fansNum']
        statuses_count = user['statuses_count']

        print("用户名："+screen_name, "发布时间："+created_at, "转发数："+str(reposts_count),
              "评论数："+str(comments_count), "点赞数："+str(like_count),
              "粉丝个数："+str(fansNum), "关注："+str(statuses_count), "微博内容："+text)

    def print_comment(self, group):
        created_at = group['created_at']  # 评论的时间
        comment_id = group['id']  # 该条评论的id
        comment_content = group['text']  # 评论内容
        comment_source = group['source']  # 评论来源，什么客户端
        like_counts = group['like_counts']  # 被点赞数
        comment_user = group['user']  # 评论用户
        screen_name = comment_user['screen_name']  # 评论用户
        comment_user_id = comment_user['id']  # 评论用户id
        print("\t用户id为"+str(comment_user_id)+",\t昵称为"+screen_name+",\t在"
              + created_at+"\t发了：<"+comment_content+"> 评论，\t获得了<"+str(like_counts)+">个赞")


def main():
    my = WeiboCrawler("", "")
    my.start()

if __name__ == '__main__':
    main()
