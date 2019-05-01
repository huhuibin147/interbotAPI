# -*- coding: utf-8 -*-
import os
import sys
import time
import logging
import jobCenter
import interMysql


from ppyappLib import ppyAPI


class autoRefreshTokenJob(jobCenter.jobCenter):


    def addJob(self):
        self.sched.add_job(self.jobMethod, 'interval', hours=6, args=[], max_instances=1)

    def jobMethod(self):
        # get users
        users = self.getUsers()
        # refresh token
        for u in users:
            logging.info('dealing.. %s', u)
            ppyAPI.apiv2RefreshToken(u["refreshtoken"], qq=u["qq"], groupid=u["groupid"])

    def getUsers(self):
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT qq, groupid, acesstoken, refreshtoken 
            FROM user where acesstoken!='' group by qq
        '''
        ret = db.query(sql)
        return ret