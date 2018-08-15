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
@appTools.deco(autoOusInfoKey='osuid,osuname')
def rctpp(**kw):
    b = botHandler.botHandler()
    osuid = kw['autoOusInfoKey']['osuid']
    osuname = kw['autoOusInfoKey']['osuname']
    recinfo = b.getRecInfo(osuid, "1")
    logging.info(recinfo)
    if not recinfo:
        res = "没有最近游戏记录,绑定用户为%s" % osuname
    else:
        res = b.getRctppRes(recinfo[0])
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
@appTools.deco(autoOusInfoKey='osuid,osuname')
def bbp(**kw):
    # 带输入用户类型
    b = botHandler.botHandler()
    osuid = kw['autoOusInfoKey']['osuid']
    osuname = kw['autoOusInfoKey'].get('osuname')

    recinfo = b.getRecBp(osuid, "5")
    if not recinfo:
        return "没有Bp,下一个!!"
    res = b.bbpOutFormat(recinfo, osuname)
    return res

@app.route('/test', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid')
def test(**kw):
    # 带输入用户类型
    b = botHandler.botHandler()
    osuid = kw['autoOusInfoKey']['osuid']
    uinfo = b.getOsuInfoFromAPI(osuid)
    if not uinfo:
        return "不存在或者网络异常!"
    recinfo = b.getRecBp(osuid, "5")
    res = b.testFormatOut(uinfo[0], recinfo)
    return res

@app.route('/skill', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuname')
def skill(**kw):
    # 带输入用户类型
    b = botHandler.botHandler()
    osuname = kw['autoOusInfoKey']['osuname']
    res = b.getSkillInfo(osuname)
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
    
