# -*- coding: utf-8 -*-
import logging
import os
import sys
import jobCenter
from commLib import Config
from commLib import pushTools


from chatbotLib import chatHandler


class autoSpeakJob(jobCenter.jobCenter):


    def addJob(self):
        self.sched.add_job(self.jobMethod, 'interval', seconds=10, args=[])

    def jobMethod(self):
        for gid in [Config.XINRENQUN]:
            self.auto_speak(gid)

    def auto_speak(self, gid):
        c = chatHandler.chatHandler()
        if c.check_redis_is_selfchat(gid, Config.BOT_QQ):
            return

        msg = c.random_auotoreply_msg(Config.AUTOSPEAK_PCT)
        if msg:
            logging.info(f"触发[{gid}]自动发言！")
            self.sendCq(gid, msg)
            c.Chat2Redis(gid, Config.BOT_QQ, msg)


        
    
        
