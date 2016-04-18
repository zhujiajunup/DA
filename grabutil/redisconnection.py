__author__ = 'jjzhu'
__doc__ = 'redis 数据库'
import redis

r = redis.StrictRedis()
r.set('name', 'jjzhu')
# r.shutdown()
