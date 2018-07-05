# -*- coding: utf-8 -*-
import json
import logging
from commLib import cmdRouter

class botHandler():


    def __init__(self):
        pass
    
    def getOsuInfo(self, args):
        """取osu用户绑定信息
        Args:
            qq/groupid
        """
        ret = cmdRouter.invoke('!uinfo', args)
        return json.loads(ret)

    def getRecInfo(self, args):
        """取osu用户rec信息
        Args:
            osuid
        """
        ret = cmdRouter.invoke('!rec', args)
        return json.loads(ret)


    def getOppaiInfo(self, bid, extend=''):
        """取oppai结果,后续可以缓存在本地,定期清理
        Args:
            bid
            extend 附加条件  参考git
        """
        ret = cmdRouter.invoke('!oppai', {"bid": bid, "extend": extend})
        return json.loads(ret)


