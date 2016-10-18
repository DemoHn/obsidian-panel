__author__ = "Nigshoxiz"

import redis
import time

#r = redis.StrictRedis(host='localhost', port=6379, db=0)
r = redis.Redis()
p = r.pubsub()
p.subscribe('socketio')

#while True:
for message in p.listen():
    if message:
        print(r.publish("socketio","hehe"))
        print("Subscriber: %s" % message['data'])

