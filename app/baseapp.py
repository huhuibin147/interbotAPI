# -*- coding: utf-8 -*-
import yaml
import json
import logging
from flask import Flask
from flask import request
from baseappLib import baseHandler
from commLib import cmdRouter
from commLib import appTools

with open('./app/baseapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/uinfo', methods=['POST'])
@appTools.deco()
def userInfoApi(**kw):
    ins = baseHandler.baseHandler()
    rts = ins.getUserBindInfo({"qq":kw['qqid'], "groupid": kw['groupid']})
    return json.dumps(rts)


@app.route('/setid', methods=['POST'])
@appTools.deco()
def bindUserInfo(**kw):
    ins = baseHandler.baseHandler()
    if kw.get('iargs'):
        osuid = kw['iargs'][0]
    else:
        osuid = kw.get('osuid', '')
    return osuid


@app.route('/args', methods=['POST'])
@appTools.deco()
def argsApi(**kw):
    return json.dumps(kw['iargs'])


if __name__ == '__main__':
    app.run()
    
