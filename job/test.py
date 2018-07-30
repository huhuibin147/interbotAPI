# -*- coding: utf-8 -*-
import time
import logging
import jobCenter

class test(jobCenter.jobCenter):


    def addJob(self):
        self.sched.add_job(self.jobMethod, 'interval', minutes=1, args=[])

    def jobMethod(self):
        groupid = 641236878
        msg = '定时推送任务测试,%s' % str(time.time())
        self.sendCq(groupid, msg)

