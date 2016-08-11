import redis

r = redis.StrictRedis()
r.set('name', 'jjzhu')
# r.shutdown()
