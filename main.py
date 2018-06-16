# -*- coding: utf-8 -*-
import sys
import yaml
import logging
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

sys.path.append('./app')

if len(sys.argv) < 2:
    print('usage: {python3 main.py app}')
    exit()

appid = sys.argv[1]

loadInstance = __import__(appid)

# 初始化日志格式
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname).4s][%(asctime)s][%(name)s] %(message)s",
    datefmt='%Y-%d-%m %H:%M:%S'
)

def refLoadYaml(filename):
    yamlFile = open('./app/%s' % filename, encoding='utf8')
    config = yaml.load(yamlFile)
    return config

def main():
    filename = '%s.yaml' % appid
    config = refLoadYaml(filename)
    port = config['app']['listen']
    http_server = HTTPServer(WSGIContainer(loadInstance.app))
    http_server.listen(port)
    logging.info('[%s] start, listen [%s]' % (appid,port))
    IOLoop.instance().start()


if __name__ == '__main__':
    main()