# -*- coding: utf-8 -*-
import re
import json
import logging
import requests
import threading
import redis
from commLib import interMysql
from commLib import interRedis
from defindappLib import audio

class defindHandler():

    def __init__(self, context):
        self.context = context
        self.job = [self.oldBotMain]
        # self.job = [self.recordRecommendMap]

    def main(self):
        """任务分配中心
        配置方法：
            self.job添加任务方法
            以多线程方式启动
        return：
            以ws方式推回cq
        """
        for method in self.job:
            t = threading.Thread(target=method)
            t.start()

        return ''

    def recordRecommendMap(self):
        """记录热推荐图任务
        说明：
            通过命令方式启动记录
            key1 记录 通行 incr实现
            key2 写 真实记录 list实现
        """
        qqid = self.context['user_id']
        groupid = self.context['group_id']
        rds = interRedis.connect('inter4')
        tagskey = 'RECORD_MAP:{groupid}:{qqid}'.format(groupid=groupid, qqid=qqid)
        if not rds.exists(tagskey):
            return ''

        logging.info('存在记录key,进行推荐记录')
        bids = self.recommendMapFilter(self.context['message'])
        self.mapList2Redis(bids, groupid, qqid)
        return ''

    def recommendMapFilter(self, content):
        """过滤消息，取Map链接
        """
        p = re.compile('https://osu.ppy.sh/b/(\d+)')
        bids = p.findall(content)
        logging.info('提取bids:%s', bids)
        return bids

    def mapList2Redis(self, bids, groupid, qqid):
        rds = interRedis.connect('inter4')
        key = 'RECORD_MAPLIST:{groupid}:{qqid}'.format(groupid=groupid, qqid=qqid)
        for bid in bids:
            rds.lpush(key, bid)
        return

    def test(self):
        logging.info('defind test job suc')


    def oldBotMain(self):
        """实现旧版本模式
        """
        try:
            audio.entry(self.context)
        except:
            logging.exception("")
            