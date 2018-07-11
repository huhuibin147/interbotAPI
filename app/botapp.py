# -*- coding: utf-8 -*-
import yaml
import json
import logging
import requests
from flask import Flask
from flask import request
from botappLib import botHandler
from commLib import appTools

with open('./app/botapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/rctpp', methods=['POST'])
@appTools.deco()
def rctpp(**kw):
    b = botHandler.botHandler()
    osuinfo = b.getOsuInfo({"qqid":kw['qqid'], "groupid": kw['groupid']})
    logging.info(osuinfo)
    if osuinfo:
        osuid = osuinfo[0]['osuid']
        recinfo = b.getRecInfo({"osuid": osuid, "limit": "1"})
        logging.info(recinfo)
        if not recinfo:
            res = "别复读好马!"
        else:
            res = b.getRctppRes(recinfo[0])
    else:
        res = "你倒是绑定啊.jpg"
    return res

@app.route('/mybp', methods=['POST'])
@appTools.deco()
def mybp(**kw):
    limit = "1" if not kw['iargs'] else kw['iargs'][0]
    if int(limit) < 0 or int(limit) > 100:
        limit = "1"
    b = botHandler.botHandler()
    osuinfo = b.getOsuInfo({"qqid":kw['qqid'], "groupid": kw['groupid']})
    logging.info(osuinfo)
    if osuinfo:
        osuid = osuinfo[0]['osuid']
        recinfo = b.getRecBp({"osuid": osuid, "limit": limit})
        logging.info(recinfo)
        if not recinfo:
            res = "别复读好马!"
        else:
            res = b.getRctppRes(recinfo[-1])
    else:
        res = "你倒是绑定啊.jpg"
    return res


if __name__ == '__main__':
    app.run()
    
