# -*- coding: utf-8 -*-
import os
import yaml
import json
import logging
from flask import Flask
from flask import request
from commLib import appTools
from ppyappLib import ppyHandler

with open('./app/ppyapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)


app = Flask(__name__)

@app.route('/bp', methods=['POST'])
def bpApi():
    return 'bp test'

@app.route('/recent', methods=['POST'])
@appTools.deco()
def recent(**kw):
    uid = kw.get('osuid')
    mode = kw.get('mode', 0)
    limit = kw.get('limit', 10)
    pyh = ppyHandler.ppyHandler()
    ret = pyh.getRecent(uid, mode, limit)
    return json.dumps(ret)

@app.route('/oppai', methods=['POST'])
@appTools.deco()
def oppai(**kw):
    bid = kw['bid']
    extend = kw.get('extend', '')
    ret = os.popen('curl https://osu.ppy.sh/osu/%s | /root/oppai/./oppai - %s' % (bid, extend))
    return json.dumps(ret.read())



if __name__ == '__main__':
    app.run()
    
