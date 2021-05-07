# -*- coding: utf-8 -*-
import os
import time
import logging
import jobCenter


class aliveJob(jobCenter.jobCenter):


    def addJob(self):
        self.sched.add_job(self.jobMethod, 'interval', seconds=60, args=[])

    def jobMethod(self):
        for ser in self.getServers():
            os.system("sh loopUtil.sh %s" % ser)

    def getServers(self):
        sers = ["apiapp1", "apiv", "ppyapp1", "sysapp1", "defindapp1", "msgCenter1", "quant", "botapp1", "baseapp1", "extendapp1"]
        return sers
