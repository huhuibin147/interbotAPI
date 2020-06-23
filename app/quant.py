# -*- coding: utf-8 -*-
import os
import yaml
import json
import random
import logging
import requests
from flask import Response, Flask
from flask import request
from quantLib import quantHandler


with open('./app/quant.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)



@app.route('/info', methods=['GET'])
def getRealTimeInfo(**kw):
    tk = request.args.get('tk')
    args = request.args.get('o', '0')
    logging.info('args:%s', args)
    obj = quantHandler.QuantHandler()
    if not obj.check_token(tk):
        return ''
    r = obj.get_real_time_api_info(args)
    rs = obj.out_html(r)
    return rs


if __name__ == '__main__':
    app.run(threaded=True)
    
