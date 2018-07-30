# -*- coding: utf-8 -*-
import sys
import json
import logging
import websocket

from apscheduler.schedulers.blocking import BlockingScheduler



class jobCenter():


    def __init__(self):
        self.ws = 'ws://interbot.cn:12345/'
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
        ws = websocket.create_connection(self.ws)
        ws.send(json.dumps({
                "groupid": groupid,
                "msg": msg
            }))
        logging.info('send to[%s],msg[%s]', groupid, msg)
        ws.close()


def main(modelname):
    _model = __import__(modelname)
    _class = getattr(_model, modelname)
    _instance = _class()
    _instance.start()


if __name__ == '__main__':
    main(sys.argv[1])