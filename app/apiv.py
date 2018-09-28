# -*- coding: utf-8 -*-
import os
import yaml
import json
import random
import logging
import requests
from flask import Response, Flask
from flask import request
from apivLib import apivHandler

with open('./app/apiv.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/auth', methods=['GET'])
def statApi(**kw):
    code = request.args.get('code')
    state = request.args.get('state')
    obj = apivHandler.apivHandler()
    rs = obj.userOauth(code, state)
    if rs > 0:
        ret = '通过授权，绑定interbot成功!后续将开放apiv2功能，敬请期待！'
    else:
        ret = '绑定出错，请联系inter!'
    return ret


if __name__ == '__main__':
    app.run(threaded=True)
    
