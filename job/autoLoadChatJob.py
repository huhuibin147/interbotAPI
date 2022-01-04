# -*- coding: utf-8 -*-
import os
import sys
import jobCenter


from chatbotLib import chatHandler


class autoLoadChatJob(jobCenter.jobCenter):


    def addJob(self):
        self.sched.add_job(self.jobMethod, 'interval', seconds=60, args=[])

    def jobMethod(self):
        b = chatHandler.chatHandler()
        b.collect_chat2redis()

        
    
        
