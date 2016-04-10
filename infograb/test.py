__author__ = 'Administrator'
from ghost import Ghost

g = Ghost()
with g.start() as session:
    page, extra_resources = session.open("http://www.baidu.com")
    print(page)

