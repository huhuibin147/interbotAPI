# -*- coding: utf-8 -*-
import yaml
import logging
from api import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


yamlFile = open('service.yaml')
config = yaml.load(yamlFile)

# 初始化日志格式
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname).4s][%(asctime)s][%(name)s] %(message)s",
    datefmt='%Y-%d-%m %H:%M:%S'
)

if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(config['server']['listen'])
    IOLoop.instance().start()