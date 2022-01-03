# -*- coding: utf-8 -*-
import os
import sys
import time
import logging
import jobCenter


from botappLib import botHandler


class autoCheckMpBotJob(jobCenter.jobCenter):


    def addJob(self):
        self.sched.add_job(self.jobMethod, 'interval', seconds=60, args=[])

    def jobMethod(self):
        
        b = botHandler.botHandler()
        if not b.check_mp_idle():
            rs = b.make_mp_idle()
            logging.info("auto make mp idle rs:%s", rs)
        else:
            logging.info("mp idle alive")
            if not b.check_mp_network():
                b.mp_idle_kill()
        
    
        
