# -*- coding: utf-8 -*-
import re
import time
import json
import traceback
import logging
import requests

from commLib import interMysql



class sysHandler():


    def __init__(self):
        pass

    def getFuncDistinctNodes(self):
        """取命令列表用到的节点
        """
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT distinct(location) location 
            FROM cmdRef where location != '' and location is not null
        '''
        rs = db.query(sql)
        return rs

    def getFuncNodes(self):
        """取命令列表功能的节点
        """
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT location, url 
            FROM cmdRef where location != '' and location is not null
        '''
        rs = db.query(sql)
        return rs

    def nodeAliveTest(self):
        """节点存活测试-范围命令列表
        """
        s1 = time.time()
        ret = "interbot's node test\n"
        nodeDict = {}
        p = re.compile('//(.*?)\\.')
        for r in self.getFuncDistinctNodes():
            nodeName = p.findall(r["location"])[0]
            rs = self.urlCurlTest(r["location"]+'/')
            if nodeName not in nodeDict:
                nodeDict[nodeName] = [rs]
            else:
                nodeDict[nodeName].append(rs)
        for k,v in nodeDict.items():
            nums = len(v)
            alive = v.count(True)
            die = nums - alive
            ret += "[%s] total:%s, alive:%s, die:%s \n" % (k, nums, alive, die)
        ret += 'times: %sms' % round(((time.time()-s1)*1000), 2)
        return ret

    def urlCurlTest(self, url):
        """链路测试,502异常,404存活
        """
        try:
            r = requests.get(url)
            logging.info('NodeTest [%s] %s', url, r.status_code)
            if r.status_code == 502:
                return False
            return True
        except:
            return False

    def funcAliveTest(self):
        """功能级别存活测试-范围命令列表
        """
        s1 = time.time()
        ret = "interbot's func test\n"
        nodeDict = {}
        p = re.compile('//(.*?)\\.')
        for r in self.getFuncNodes():
            nodeName = p.findall(r["location"])[0]
            rs = self.urlCurlTest(r["location"]+r["url"])
            if nodeName not in nodeDict:
                nodeDict[nodeName] = [rs]
            else:
                nodeDict[nodeName].append(rs)
        for k,v in nodeDict.items():
            nums = len(v)
            alive = v.count(True)
            die = nums - alive
            ret += "[%s] total:%s, alive:%s, die:%s \n" % (k, nums, alive, die)
        ret += 'times: %sms' % round(((time.time()-s1)*1000), 2)
        return ret

