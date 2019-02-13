# -*- coding: utf-8 -*-
import yaml
import json
import logging
import requests
from flask import Flask
from flask import request
from botappLib import botHandler
from commLib import appTools
from commLib import Config
from commLib import interRedis
from ppyappLib import ppyHandler
from baseappLib import baseHandler

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

@app.route('/rctpps', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid,osuname')
def rctpps(**kw):
    b = botHandler.botHandler()
    osuid = kw['autoOusInfoKey']['osuid']
    osuname = kw['autoOusInfoKey']['osuname']
    recinfo = b.getRecInfo(osuid, "5")
    logging.info(recinfo)
    if not recinfo:
        res = "没有最近游戏记录,绑定用户为%s" % osuname
    else:
        res = b.getRctppBatchRes(recinfo)
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
    b = botHandler.botHandler()
    osuname = kw['autoOusInfoKey']['osuname']
    res = b.getSkillInfo(osuname)
    return res

@app.route('/vssk', methods=['POST'])
@appTools.deco()
def vssk(**kw):
    b = botHandler.botHandler()
    groupid = kw['groupid']
    # 先判断自己绑定信息
    osuinfo = b.getOsuInfo(kw['qqid'], groupid)
    if not osuinfo:
        return "你倒是绑定啊.jpg"
    osuname = osuinfo[0]['osuname']
    # 判断输入信息和艾特信息
    if kw.get('atqq'):
        vsosuinfo = b.getOsuInfo(kw['atqq'], groupid)
        if not vsosuinfo:
            return "他没有绑定，赶紧叫他绑定啊!"
        vsosuname = vsosuinfo[0]['osuname']
    else:
        if not kw['iargs']:
            return "你倒是输入vs谁啊" 
        else:
            vsosuname = ' '.join(kw['iargs'])
    res = b.getSkillvsInfo(osuname, vsosuname)
    return res

@app.route('/todaybp', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuname')
def todaybp(**kw):
    b = botHandler.botHandler()
    osuname = kw['autoOusInfoKey']['osuname']
    res = b.todaybp(osuname)
    return res

@app.route('/mu', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid')
def mu(**kw):
    b = botHandler.botHandler()
    osuid = kw['autoOusInfoKey']['osuid']
    res = 'https://osu.ppy.sh/u/%s' % osuid
    return res

@app.route('/myinfo', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid,osuname,money,bagnum')
def myinfo(**kw):
    b = botHandler.botHandler()
    osuid = kw['autoOusInfoKey']['osuid']
    osuname = kw['autoOusInfoKey']['osuname']
    money = kw['autoOusInfoKey']['money']
    bagnum = kw['autoOusInfoKey']['bagnum']
    home_url = 'https://osu.ppy.sh/u/%s' % osuname
    res = "osu:%s\nosuid:%s\nmoney:%s\nbagnum:%s\n%s" % (osuname, osuid, money, bagnum, home_url)
    return res

@app.route('/help', methods=['POST'])
@appTools.deco()
def help(**kw):
    b = botHandler.botHandler()
    rs = b.helpFormatOut()
    return rs

@app.route('/thanks', methods=['POST'])
@appTools.deco()
def thanks(**kw):
    b = botHandler.botHandler()
    rs = b.thanksFormatOut()
    return rs

@app.route('/friends', methods=['POST'])
@appTools.deco()
def friends(**kw):
    b = ppyHandler.ppyHandler()
    rs = b.getFriends(kw['qqid'], kw['groupid'])
    return rs

@app.route('/tt', methods=['POST'])
@appTools.deco()
def tt(**kw):
    rs = '%s->%s' % (kw['qqid'], kw['atqq'])
    return rs

@app.route('/stat', methods=['POST'])
@appTools.deco()
def stat(**kw):
    b = ppyHandler.ppyHandler()
    atqq = kw['atqq']
    if atqq:
        base = baseHandler.baseHandler()
        rs = base.checkTokenPermission(atqq, kw['groupid'])
        if rs.isdigit():
            rs = b.osuV2stat(atqq, kw['groupid'])
    else:
        rs = b.osuV2stat(kw['qqid'], kw['groupid'])
    return rs

@app.route('/v2me', methods=['POST'])
@appTools.deco()
def v2me(**kw):
    b = ppyHandler.ppyHandler()
    rs = b.getV2MyInfo(kw['qqid'], kw['groupid'])
    return rs


@app.route('/nbp', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid,osuname', rawinput=1)
def nbp(**kw):
    b = botHandler.botHandler()
    osuid = kw['autoOusInfoKey']['osuid']
    osuname = kw['autoOusInfoKey'].get('osuname')
    bid = kw['iargs'][0]

    recinfo = b.getRecBp(osuid, "100")
    if not recinfo:
        return "没有Bp,下一个!!"
    res = b.getBpNumBybid(recinfo, osuname, bid)
    return res

@app.route('/createroom', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuname', rawinput=1)
def createroom(**kw):
    b = botHandler.botHandler()
    osuname = kw['autoOusInfoKey']['osuname']
    if len(kw['iargs']) != 2:
        return '参数错误 usage: ¡createroom roomname password'
    roomname = kw['iargs'][0]
    roompwd = kw['iargs'][1]

    res = b.createMpRoom(osuname, kw['qqid'], kw['groupid'], roomname, roompwd)
    return res

@app.route('/getroom', methods=['POST'])
@appTools.deco()
def getroom(**kw):
    b = botHandler.botHandler()

    res = b.getMpRoom(kw['qqid'], kw['groupid'])
    return res

@app.route('/joinroom', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid,osuname', rawinput=1)
def joinroom(**kw):
    b = botHandler.botHandler()

    res = b.joinMpRoom()
    return res

@app.route('/privatetest', methods=['POST'])
@appTools.deco()
def privatetest(**kw):
    return 'interbot偷偷cue了你一下！'


@app.route('/sttest', methods=['POST'])
@appTools.deco()
def sttest(**kw):
    end = sttest_start('sttest', kw['qqid'], kw['groupid'], kw['step'])
    if end:
        return '交互次数达到3，sttest结束退出'
    return '[%s] %s' % ('sttest1', str(kw))

@app.route('/sttest2', methods=['POST'])
@appTools.deco()
def sttest2(**kw):
    end = sttest_start('sttest2', kw['qqid'], kw['groupid'], kw['step'])
    if end:
        return '交互次数达到3，sttest2结束退出'
    return '[%s] %s' % ('sttest2', str(kw))

def sttest_start(func, qqid, groupid, step):
    rds = interRedis.connect('inter1')
    key = Config.CMDSTEP_KEY.format(qq=qqid, groupid=groupid, func=func)
    rs = rds.incr(key)
    rds.expire(key, Config.CMDSTEP_KEY_EXPIRE_TIME)
    end = 0
    if rs >= 3:
        rds.delete(key)
        key2 = Config.FUNC_ACTIVE_KEY.format(qq=qqid, groupid=groupid)
        rds.srem(key2, func)
        end = 1
    return end


if __name__ == '__main__':
    app.run(threaded=True)
    
