# -*- coding: utf-8 -*-
import yaml
from api import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


yamlFile = open('service.yaml')
config = yaml.load(yamlFile)


if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(config['server']['listen'])
    IOLoop.instance().start()