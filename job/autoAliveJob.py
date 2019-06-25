# -*- coding: utf-8 -*-
import os
import time
import logging
import jobCenter


class autoAliveJob(jobCenter.jobCenter):


    def addJob(self):
        self.sched.add_job(self.jobMethod, 'interval', seconds=600, args=[])

    def jobMethod(self):
        for ser in self.getServers():
            os.system("sh loopUtil2.sh %s" % ser)

    def getServers(self):
        sers = ["autoRefreshTokenJob", "autoUpdateOsuerPp"]
        return sers
