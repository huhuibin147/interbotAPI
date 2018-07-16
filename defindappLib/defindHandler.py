# -*- coding: utf-8 -*-
import re
import json
import logging
import requests
import threading
import redis
from commLib import interMysql

class defindHandler():

    def __init__(self, context):
        self.context = context
        self.job = [self.recordRecommendMap]

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
        return ''

