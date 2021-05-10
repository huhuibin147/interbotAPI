# -*- coding: utf-8 -*-
import yaml
import json
import time
import random
import logging
import requests
from flask import Flask
from flask import request
from botappLib import botHandler
from commLib import appTools
from commLib import Config
from commLib import interRedis
from commLib import pushTools
from ppyappLib import ppyHandler
from baseappLib import baseHandler
from draws import drawRank
from draws import rank_tab
from draws import draw_data

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
    smoke_res = None
    if not recinfo:
        res = "没有最近游戏记录,绑定用户为%s" % osuname
    else:
        res, kv  = b.getRctppRes(recinfo[0])
        # 执行管理逻辑
        smoke_res = b.rctppSmoke(kw["groupid"], kw["qqid"], kv, iswarn=1)
        if smoke_res:
            res += f'\n>>{smoke_res}<<'
    rank_tab.upload_rec(osuid, kw["groupid"])
    if smoke_res:
        return f'由于触发本群限制，请私聊查询，触犯法律:{smoke_res}'
    return res

@app.route('/rctppnew', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid,osuname')
def rctppnew(**kw):
    b = botHandler.botHandler()
    osuid = kw['autoOusInfoKey']['osuid']
    osuname = kw['autoOusInfoKey']['osuname']
    recinfo = b.getRecInfo(osuid, "1")
    logging.info(recinfo)
    if not recinfo:
        res = "没有最近游戏记录,绑定用户为%s" % osuname
    else:
        res, kv = b.getRctppResNew(recinfo[0])
        # 执行管理逻辑
        b.rctppSmoke(kw["groupid"], kw["qqid"], kv)
    rank_tab.upload_rec(osuid, kw["groupid"])
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
    qqid = kw['qqid'] if not kw['atqq'] else kw['atqq']
    if not kw['iargs']:
        x = 1  
    else:
        input0 = kw['iargs'][0]
        args0 = input0.replace(f'[CQ:at,qq={qqid}]', '')
        x = int(args0) if args0.isdigit() else 1

    if x < 0 or x > 100:
        x = 1
    b = botHandler.botHandler()
    osuinfo = b.getOsuInfo2(qqid)
    logging.info(osuinfo)
    smoke_res = None
    if osuinfo:
        osuid = osuinfo['osuid']

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
            res, kv = b.getRctppRes(recinfo[x-1])
            # 执行管理逻辑
            smoke_res = b.rctppSmoke(kw["groupid"], kw["qqid"], kv, iswarn=1)
            if smoke_res:
                res += f'\n>>{smoke_res}<<'
    else:
        res = "你倒是绑定啊.jpg"
    if smoke_res:
        return f'由于触发本群限制，请私聊查询，触犯法律:{smoke_res}'
    return res


@app.route('/boom', methods=['POST'])
@appTools.deco()
def boom_check(**kw):
    qqid = kw['qqid']
    atqq = kw['atqq']
    groupid = kw['groupid']
    # 群限定
    if int(groupid) != Config.GROUPID["XINRENQUN"]:
        return ''
    rds = interRedis.connect('osu2')
    key = f'SMOKE_TS_{groupid}|{atqq}'
    rs = rds.get(key)
    if not rs:
        return ''
    # 越狱概率
    if random.random() >= 0.5:
        rds.delete(key)
        return f'在{qqid}的帮助下{atqq}越狱成功!'
    
    v = json.loads(rs)
    nowts = time.time()
    ts = v['ts']
    endts = v['endts']
    # 已经释放出狱
    if nowts >= endts:
        return
    
    # 重新计算入狱时间
    leftts = endts - nowts
    ts = leftts + leftts*0.5
    endts += leftts*0.5
    v = json.dumps({'nowts': nowts, 'endts': endts, 'ts': ts})
    rds.setex(key, v, int(ts))
    rds.expire(key, int(ts))

    # 帮凶承担一半时间
    ts2 = ts * 0.5
    endts2 = nowts + ts2
    key2 =  f'SMOKE_TS_{groupid}|{qqid}'
    v2 = json.dumps({'nowts': nowts, 'endts': endts2, 'ts': ts2})
    rds.setex(key2, v2, int(ts2))
    rds.expire(key2, int(ts2))

    time.sleep(0.5)
    pushTools.pushSmokeCmd(groupid, atqq, ts)
    pushTools.pushSmokeCmd(groupid, qqid, ts2)

    s = f'检测到越狱行为，{qqid}尝试解救{atqq}失败，双双入狱'
    return s


@app.route('/bestmaprec', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid,osuname', rawinput=1)
def bestmaprec(**kw):
    if not kw['iargs']:
        return "请输入bid！"
    bid = kw['iargs'][0]
    osuid = kw['autoOusInfoKey']['osuid']
    b = botHandler.botHandler()
    res = b.get_best_map_rec_from_db(osuid, bid)
    if not res:
        return "你连成绩都没有，快去打一个上传！"
    recinfo = json.loads(res["recjson"])
    res, kv = b.getRctppRes(recinfo)
    return res


@app.route('/bbp', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid,osuname')
def bbp(**kw):
    qqid = kw['qqid'] if not kw['atqq'] else kw['atqq']
    if not kw['iargs']:
        x = 1  
    else:
        input0 = kw['iargs'][0]
        args0 = input0.replace(f'[CQ:at,qq={qqid}]', '')
        x = int(args0) if args0.isdigit() else 1

    if x < 1 or x > 100:
        x = 1

    b = botHandler.botHandler()
    osuinfo = b.getOsuInfo2(qqid)
    if osuinfo:
        osuid = osuinfo['osuid']
        osuname = osuinfo['osuname']
    else:
        return "你倒是绑定啊.jpg"

    recinfo = b.getRecBp(osuid, "100")
    if not recinfo:
        return "没有Bp,下一个!!"
    res = b.bbpOutFormat(recinfo[x-1:x+4], osuname, x)
    return res
    
@app.route('/bbp2', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid,osuname')
def bbp2(**kw):
    qqid = kw['qqid'] if not kw['atqq'] else kw['atqq']
    if not kw['iargs']:
        x = 1  
    else:
        input0 = kw['iargs'][0]
        args0 = input0.replace(f'[CQ:at,qq={qqid}]', '')
        x = int(args0) if args0.isdigit() else 1

    if x < 1 or x > 100:
        x = 1

    b = botHandler.botHandler()
    osuinfo = b.getOsuInfo2(qqid)
    if osuinfo:
        osuid = osuinfo['osuid']
        osuname = osuinfo['osuname']
    else:
        return "你倒是绑定啊.jpg"

    recinfo = b.getRecBp(osuid, "100")
    if not recinfo:
        return "没有Bp,下一个!!"
    res = b.bbpOutFormat2(recinfo[x-1:x+2], osuname, x)
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

@app.route('/sleep', methods=['POST'])
@appTools.deco()
def sleep(**kw):
    ts = 3600*8
    pushTools.pushSmokeCmd(kw["groupid"], kw["qqid"], ts)
    return ""

@app.route('/kill', methods=['POST'])
@appTools.deco()
def kill(**kw):
    pushTools.pushKickCmd(kw["groupid"], kw["atqq"])
    return "%s已经狗带了" % kw["atqq"]

@app.route('/playerscheck', methods=['POST'])
@appTools.deco()
def playerscheck(**kw):
    b = botHandler.botHandler()
    ret = b.groupPlayerCheck(kw["groupid"])
    return ret

@app.route('/scancallback', methods=['POST'])
@appTools.deco()
def scancallback(**kw):
    logging.info('scancallback....')
    ret = kw["ret"]
    users = json.loads(ret)
    groupid = kw["callbackargs"]
    b = botHandler.botHandler()
    ret = b.scanPlayers(groupid, users)
    return ret

@app.route('/ppcheck', methods=['POST'])
@appTools.deco()
def ppcheck(**kw):
    b = botHandler.botHandler()
    ret = b.groupPpCheck(kw["groupid"])
    return ret

@app.route('/ppcheckcallback', methods=['POST'])
@appTools.deco()
def ppcheckcallback(**kw):
    logging.info('ppcheckcallback....')
    ret = kw["ret"]
    users = json.loads(ret)
    groupid = kw["callbackargs"]
    b = botHandler.botHandler()
    ret = b.scanPlayers2(groupid, users)
    return ret

@app.route('/days', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuname', rawinput=1)
def days(**kw):
    x = 0 if not kw['iargs'] else int(kw['iargs'][0])
    if int(x) < 0:
        x = 0
    osuname = kw['autoOusInfoKey']['osuname']
    b = botHandler.botHandler()
    ret = b.osu_stats(osuname, x)
    return ret

@app.route('/rank', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid', rawinput=1)
def rank(**kw):
    try:
        if not kw['iargs']:
            return "请输入bid!"
        bid = kw['iargs'][0]
        osuid = kw['autoOusInfoKey']['osuid']
        p = drawRank.start(bid, kw["groupid"], hid=1, mods=-1, uid=osuid)
        return "[CQ:image,cache=0,file=http://interbot.cn/itbimage/%s]" % p
    except:
        logging.exception("rank error")
        return "fail..."

@app.route('/uploadrec', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid', rawinput=1)
def up(**kw):
    osuid = kw['autoOusInfoKey']['osuid']
    return rank_tab.upload_rec(osuid, kw["groupid"])

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

@app.route('/upimg', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid', rawinput=1)
def upimg(**kw):
    osuid = kw['autoOusInfoKey']['osuid']
    draw_data.down_images_from_ppy([osuid])
    return '刷新成功(可能吧?'

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

@app.route('/setcontent', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuname', rawinput=1, autouseatqq=False)
def setcontent(**kw):
    b = botHandler.botHandler()
    osuname = kw['autoOusInfoKey']['osuname']
    if kw['iargs']:
        content = kw['iargs'][0]
    else:
        return '请输入内容，¡xx xxxx'
    if content[:2] == '\r\n':
        content = content[2:]
    cmd = b.set_id_content_cmd(osuname, content)
    res = '设置成功，生成指令为[%s]' % cmd
    return res

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



@app.route('/randmap', methods=['POST'])
@appTools.deco()
def randmap(**kw):
    s1, s2, s3 = None, None, None
    if len(kw['iargs']) >= 1:
        s1 = float(kw['iargs'][0])
        if len(kw['iargs']) > 1:
            s2 = float(kw['iargs'][1])
        if len(kw['iargs']) > 2:
            s3 = float(kw['iargs'][2])
            if s3 > 50:
                s3 = 5

    if not s1:
        s1 = 4
    if not s2:
        s2 = 5.6
    if not s3:
        s3 = 5

    b = botHandler.botHandler()
    res = b.random_maps(s1, s2, s3)
    return res

if __name__ == '__main__':
    app.run(threaded=True)
    
