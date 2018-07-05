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
    # todo 加入未绑定传id情况
    b = botHandler.botHandler()
    osuinfo = b.getOsuInfo({"qqid":kw['qqid'], "groupid": kw['groupid']})
    logging.info(osuinfo)
    if osuinfo[0]:
        osuid = osuinfo[0]['osuid']
        recinfo = b.getRecInfo({"osuid": osuid, "limit": "1"})
        if not recinfo:
            recinfo = "please play game!"
        else:
            recinfo = json.dumps(recinfo)
    else:
        recinfo = "u don't bind!"
    return recinfo

@app.route('/rec', methods=['POST'])
@appTools.deco()
def recent(**kw):
    uid = kw['iargs'][0]
    url = "http://interbot.top/osuppy/recent"
    res = requests.post(url, data={"osuid": uid, "limit": "1"})
    return res.text


if __name__ == '__main__':
    app.run()
    
