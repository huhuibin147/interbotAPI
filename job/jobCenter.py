# -*- coding: utf-8 -*-
import os
import sys
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import websocket

sys.path.append('./')
sys.path.append('./commLib')

import pushTools
from apscheduler.schedulers.blocking import BlockingScheduler

appid = sys.argv[1]

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
addTimedRotatingFileHandler('./var/log/sitb.%s.log' % appid, logLevel = logging.INFO)

class jobCenter():


    def __init__(self):
        self.sched = BlockingScheduler()
        # logging.basicConfig(
        #     level=logging.INFO,
        #     format='[%(asctime)s][%(levelname)s]%(message)s',
        #     datefmt='%Y-%m-%d %H:%M:%S'
        # )

    def start(self):
        self.addJob()
        self.sched.start()

    def addJob(self):
        self.sched.add_job(self.jobMethod, 'cron', second='*/30', args=[])

    def jobMethod(self):
        logging.info('default job!')

    def sendCq(self, groupid, msg):
        pushTools.pushMsgOne(groupid, msg)


def main(modelname):
    _model = __import__(modelname)
    _class = getattr(_model, modelname)
    _instance = _class()
    _instance.start()


if __name__ == '__main__':
    main(sys.argv[1])