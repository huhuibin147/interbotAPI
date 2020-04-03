# -*- coding: utf-8 -*-
import os
import sys
import json
import logging

sys.path.insert(0, '/root/code/dataAPI')
import real_time_api


path = os.path.dirname(os.path.abspath(__file__))


class QuantHandler():


    def __init__(self):
        pass

    def check_token(self, token):
        if not token:
            return False

        with open(f'{path}/quantTk.json', 'r') as f:
            d = json.load(f)
        if not d:
            return False
    
        if d['token'] == token:
            return True
        return False
        

    def get_real_time_api_info(self, outtype=1):
        api = real_time_api.RealTimeApi()
        r = api.main(outtype=outtype)
        return r

    def out_html(self, data):
        r = f'<pre>{data}</pre>'
        return r
    