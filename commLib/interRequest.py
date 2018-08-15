# -*- coding: utf-8 -*-
import requests
import json
import logging

class interReq():


    def __init__(self, timeout=5, headers={}):
        if not headers:
            self.headers = {
                'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-encoding' : 'gzip, deflate, br',
                'accept-language' : 'zh-CN,zh;q=0.9',
                'cookie' : '__cfduid=dcd84cc446800e949d5088570b4fa54c21490246214; _ga=GA1.2.2055967706.1490246215; cf_clearance=a233723e29ddfea8d91182fce773a828db7cc04e-1512707357-31536000; __utmz=226001156.1518163818.69.5.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _encid=%7B%22name%22%3A%22interbot%22%2C%22email%22%3A%22%22%2C%22_source%22%3A%22a%22%7D; phpbb3_2cjk5_u=11788070; phpbb3_2cjk5_u=11788070; phpbb3_2cjk5_k=5e74a60e99ec406f; phpbb3_2cjk5_k=5e74a60e99ec406f; phpbb3_2cjk5_sid=fbca0496b3d5366edf1e0b929c75c363; phpbb3_2cjk5_sid=fbca0496b3d5366edf1e0b929c75c363; phpbb3_2cjk5_sid_check=d3165160830ec9259e84adc94a9660fbca629157; phpbb3_2cjk5_sid_check=d3165160830ec9259e84adc94a9660fbca629157; __utma=226001156.2055967706.1490246215.1519746481.1520072282.81',
                'upgrade-insecure-requests' :  '1',
                'user-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
            }
        else:
            self.headers = headers
        self.timeout = timeout


    def post(self, url, params=None):
        res = requests.post(url=url, data=params, timeout=self.timeout, headers=self.headers)
        return ret

    def get(self, url):
        res = requests.get(url=url, timeout=self.timeout, headers=self.headers) 
        return ret


    def down_image(self, iname, url, path=None):
        # 此方法暂留  未修改
        if not url:
            return 0
        ir = requests.get(url=url)
        path = path+iname+'.jpg' if path else 'image/%s.png' % iname
        if ir.status_code == 200:
            with open(path, 'wb') as f:
                f.write(ir.content)
            return 1
        else:
            return 0


