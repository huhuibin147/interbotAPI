# -*- coding: utf-8 -*-
import sys
import json
import logging
import websocket

sys.path.append('./commLib')

import pushTools
from apscheduler.schedulers.blocking import BlockingScheduler



class jobCenter():


    def __init__(self):
        self.sched = BlockingScheduler()
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s][%(levelname)s]%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

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