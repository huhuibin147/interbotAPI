# -*- coding: utf-8 -*-
import logging
from ppyappLib import ppyAPI

class ppyHandler():


    def __init__(self):
        pass
    
    def getRecent(self, uid, mode=0, limit=10):
        kw = {
            'uid': uid,
            'mode': mode,
            'limit': limit
        }
        logging.info(kw)
        return ppyAPI.apiRoute('recent', **kw)
    
    def getOsuUserInfo(self, uid):
        kw = {'uid': uid}
        logging.info(kw)
        return ppyAPI.apiRoute('userinfo', **kw)