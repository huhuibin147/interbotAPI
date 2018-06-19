# -*- coding: utf-8 -*-
import sys
import yaml
import re
import logging
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

sys.path.append('./app')
appid = sys.argv[1]
port = None
loadInstance = None

if len(sys.argv) < 2:
    print('usage: {python3 main.py app}')
    exit()


# 初始化日志格式
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname).4s][%(asctime)s][%(name)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

def refLoadYaml(filename):
    p = re.compile('\d')
    filename = p.sub('', filename)
    with open('./app/%s' % filename, encoding='utf8') as f:
        config = yaml.load(f)
    return config

def loading():
    global port, loadInstance
    filename = '%s.yaml' % appid
    config = refLoadYaml(filename)
    port = config[appid]['listen']
    model = config[appid]['model']
    loadInstance = __import__(model)

def main():
    loading()
    http_server = HTTPServer(WSGIContainer(loadInstance.app))
    http_server.listen(port)
    logging.info('[%s] start, listen [%s]' % (appid, port))
    IOLoop.instance().start()



if __name__ == '__main__':
    main()