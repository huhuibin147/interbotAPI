# -*- coding: utf-8 -*-
import yaml
import redis

config = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0
}

def connect(node=None):
    return interRedis(node).getRds()
    
class interRedis():

    def __init__(self, node):
        conf = getConfig(node)
        self.rds = redis.Redis(conf['host'], conf['port'], conf['db'])

    def getRds(self):
        return self.rds

def getConfig(node):
    if not node:
        return config
    yamlFile = open('./commLib/redis.yaml', encoding='utf8')
    _conf = yaml.load(yamlFile)
    config.update(_conf.get(node, {}))
    return config

# if __name__ == '__main__':
#     r = connect('osu2')
#     r1 = r.setex('tt',1,30)
#     r1 = r.get('tt')
#     print(r1)