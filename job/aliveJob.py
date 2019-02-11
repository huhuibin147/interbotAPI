# -*- coding: utf-8 -*-
import os
import time
import logging
import jobCenter


class aliveJob(jobCenter.jobCenter):


    def addJob(self):
        self.sched.add_job(self.jobMethod, 'interval', seconds=2, args=[])

    def jobMethod(self):
        for ser in self.getServers():
            os.system("sh loopUtil.sh %s" % ser)

    def getServers(self):
        sers = ["apiapp1", "apiapp2"]
        return sers
