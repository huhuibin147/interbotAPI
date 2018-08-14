# -*- coding: utf-8 -*-
import yaml
import json
import logging
import requests
from flask import Flask
from flask import request
from botappLib import botHandler
from commLib import appTools
from commLib import interRedis

with open('./app/botapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/rctpp', methods=['POST'])
@appTools.deco()
def rctpp(**kw):
    b = botHandler.botHandler()
    qqid = kw['qqid'] if not kw.get('atqq') else kw['atqq']
    osuinfo = b.getOsuInfo(qqid, kw['groupid'])
    logging.info(osuinfo)
    if osuinfo:
        osuid = osuinfo[0]['osuid']
        recinfo = b.getRecInfo(osuid, "1")
        logging.info(recinfo)
        if not recinfo:
            res = "没有最近游戏记录,绑定用户为%s" % osuinfo[0]['osuname']
        else:
            res = b.getRctppRes(recinfo[0])
    else:
        res = "你倒是绑定啊.jpg"
    return res

@app.route('/mybp', methods=['POST'])
@appTools.deco()
def mybp(**kw):
    x = "1" if not kw['iargs'] else kw['iargs'][0]
    if int(x) < 0 or int(x) > 100:
        x = "1"
    b = botHandler.botHandler()
    osuinfo = b.getOsuInfo(kw['qqid'], kw['groupid'])
    logging.info(osuinfo)
    if osuinfo:
        osuid = osuinfo[0]['osuid']

        key = 'OSU2_USERBP:%s'
        rds = interRedis.connect('osu2')
        rdsRs = rds.get(key % osuid)
        if not rdsRs:
            recinfo = b.getRecBp(osuid, "100")
            rds.setex(key % osuid, json.dumps(recinfo), 900)
        else:
            recinfo = json.loads(rdsRs)

        if not recinfo:
            res = "别复读好马!"
        else:
            res = b.getRctppRes(recinfo[int(x)-1])
    else:
        res = "你倒是绑定啊.jpg"
    return res

@app.route('/bbp', methods=['POST'])
@appTools.deco()
def bbp(**kw):
    # 带输入用户类型
    b = botHandler.botHandler()
    osuid = "" if not kw['iargs'] else ' '.join(kw['iargs'])
    osuname = osuid
    if not osuid:
        qqid = kw['qqid'] if not kw.get('atqq') else kw['atqq']
        osuinfo = b.getOsuInfo(qqid, kw['groupid'])
        if not osuinfo:
            return "你倒是绑定啊.jpg"
        osuid = osuinfo[0]['osuid']
        osuname = osuinfo[0]['osuname']

    recinfo = b.getRecBp(osuid, "5")
    if not recinfo:
        return "没有Bp,下一个!!"
    res = b.bbpOutFormat(recinfo, osuname)
    return res

@app.route('/help', methods=['POST'])
@appTools.deco()
def help(**kw):
    b = botHandler.botHandler()
    rs = b.helpFormatOut()
    return rs

@app.route('/tt', methods=['POST'])
@appTools.deco()
def tt(**kw):
    b = botHandler.botHandler()
    rs = b.getOsuBeatMapInfo(bid=kw['iargs'][0])
    logging.info(rs)
    return ''


if __name__ == '__main__':
    app.run()
    
