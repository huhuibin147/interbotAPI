# -*- coding: utf-8 -*-
import os
import sys
import time
import jobCenter
import interMysql
import logging


from ppyappLib import ppyAPI
from botappLib import botHandler


class autoUpdateOsuerPp(jobCenter.jobCenter):


    def addJob(self):
        self.sched.add_job(self.jobMethod, 'interval', hours=3, args=[])

    def jobMethod(self):
        self.time_insert()
    
    def time_insert(self):
        """自动抓取
        条件 -- 数据库是否存在今天的记录
        存在记录时 -- 做捡漏处理
        """
        ins = botHandler.botHandler()
        if not ins.is_insert_today():
            logging.info('今天未插入，开始执行插入...')
            ins.insert_forday()
        else:
            logging.info('今天插入已完成')

