# -*- coding: utf-8 -*-
import sys
import yaml
import os
import re
import logging
from logging.handlers import TimedRotatingFileHandler
# from tornado.wsgi import WSGIContainer
# from tornado.httpserver import HTTPServer
# from tornado.ioloop import IOLoop

sys.path.append('./app')
appid = sys.argv[1]
port = None
loadInstance = None

if len(sys.argv) < 2:
    print('usage: {python3 main.py app}')
    exit()

def addTimedRotatingFileHandler(filename, **kwargs):
    """给logger添加一个时间切换文件的handler
    默认时间是0点，3个备份
    """
    dname = os.path.dirname(filename)
    if dname and not os.path.isdir(dname):
        os.makedirs(dname, '0755')
    conf = {
        'when': 'midnight',
        'backupCount': 3,
        'format': '[%(asctime)s][tid:%(thread)d][%(filename)s:%(lineno)d] %(levelname)s: %(message)s',
        'logger': logging.getLogger(),
    }
    conf.update(kwargs)
    if 'logLevel' in conf:
        if isinstance(conf['logLevel'], str):
            conf['logLevel'] = getattr(logging, conf['logLevel'])
        conf['logger'].setLevel(conf['logLevel'])
    handler = logging.handlers.TimedRotatingFileHandler(
        filename = filename,
        when = conf['when'],
        backupCount = conf['backupCount'],
    )
    handler.setFormatter(
        logging.Formatter(conf['format'])
    )
    conf['logger'].addHandler(handler)

# 日志轮转初始化
addTimedRotatingFileHandler('./var/log/itb.%s.log' % appid, logLevel = logging.INFO)


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
    loadInstance.app.run(
        port = port,
        threaded = True
    )
    # http_server = HTTPServer(WSGIContainer(loadInstance.app))
    # http_server.listen(port)
    logging.info('[%s] start, listen [%s]' % (appid, port))
    # IOLoop.instance().start()



if __name__ == '__main__':
    main()
    