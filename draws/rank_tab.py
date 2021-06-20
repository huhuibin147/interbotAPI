# -*- coding: utf-8 -*-
import traceback
import json
import logging
import copy
from ppyappLib import ppyHandler
from commLib import interRedis
from commLib import Config
from draws import score
from commLib import mods
# from libs import args_func

istest = 0

def filter_rec(uid, rec):
    # 返回入库bids
    rds = interRedis.connect()
    key = 'rec_%s' % uid
    ret = rds.get(key)
    bids = []
    # rec直接缓存
    if ret is None:
        indata = dict((r['beatmap_id'],r['date']) for r in rec)
        rds.setex(key, json.dumps(indata), 60 * 60 * 12)
        bids = [r['beatmap_id'] for r in rec]
    else:
        res = json.loads(ret)
        for r in rec:
            if r['beatmap_id'] in res:
                if r['date'] != res[r['beatmap_id']]:
                    res['beatmap_id'] = r['date']
                    bids.append(r['beatmap_id'])
                else:
                    break
            else:
                res[r['beatmap_id']] = r['date']
                bids.append(r['beatmap_id'])
        rds.setex(key, json.dumps(res), 60 * 60 * 12)
    # 测试
    if istest:
        rds.delete(key)
    return bids


def save_rec_by_rec(uid, groupid, rec, hid=1, limit=1):
    o = ppyHandler.ppyHandler()
    
    bids = [rec[0]["beatmap_id"]]
    # 提取rec
    inRec = score.check_rec(bids, rec, uid)
    if not inRec:
        logging.info('无新成绩！')
        return '你还要再刚一点.JPG'
    # 从库中过滤bids 
    inbids = [r['beatmap_id'] for r in inRec]
    inbids = score.filter_beatmapid(inbids)
    logging.info('查询bids列表:%s'%str(inbids))
    if inbids:
        mapsinfo = [o.getOsuBeatMapInfo(b) for b in inbids]
        map_args = score.args_format('map', mapsinfo)
        score.map2db(map_args)

    rec_args = score.args_format('rec', inRec)
    score.rec2db(rec_args)

    rec1 = copy.deepcopy(inRec)
    rec2 = copy.deepcopy(inRec)
    # 总榜临时处理
    score.map_rank(rec1, groupid, hid=1, rtype=1)

    score.map_rank(rec2, groupid, hid=1, rtype=2)
    return 'upload success!'

def save_rec(uid, groupid, hid=1, limit=1):
    o = ppyHandler.ppyHandler()
    rec = o.getRecent(uid, limit=limit)
    if not rec:
        return '你想意念刚榜???'
    # 过滤bids
    bids = filter_rec(uid, rec)
    if not bids:
        logging.info('bids列表空！')
        return '你倒是打图啊.JPG'
    # 过滤rec
    newRec = autoRec(rec, bids)
    # 最新rec成绩优化
    newRec = score.rec_highscore(newRec)
    # 提取rec
    inRec = score.check_rec(bids, newRec, uid)
    if not inRec:
        logging.info('无新成绩！')
        return '你还要再刚一点.JPG'
    # 从库中过滤bids 
    inbids = [r['beatmap_id'] for r in inRec]
    inbids = score.filter_beatmapid(inbids)
    logging.info('查询bids列表:%s'%str(inbids))
    if inbids:
        mapsinfo = [o.getOsuBeatMapInfo(b) for b in inbids]
        map_args = score.args_format('map', mapsinfo)
        score.map2db(map_args)

    rec_args = score.args_format('rec', inRec)
    score.rec2db(rec_args)

    rec1 = copy.deepcopy(inRec)
    rec2 = copy.deepcopy(inRec)
    # 总榜临时处理
    score.map_rank(rec1, groupid, hid=1, rtype=1)

    score.map_rank(rec2, groupid, hid=1, rtype=2)
    return 'upload success!'

def autoRec(rec, bids):
    # 过滤rec多余的
    newRec = []
    for r in rec:
        if r['beatmap_id'] in bids:
            newRec.append(r)
    return newRec


def upload_rec(uid, groupid, limit=2):
    try:
        ret = save_rec(uid, groupid, hid=1, limit=limit)
        logging.info('up success')
        return ret
    except:
        logging.exception("up error")
        return "error.."

def upload_best_rec(uid, groupid, rec):
    try:
        ret = save_rec_by_rec(uid, groupid, rec)
        logging.info('up success')
        return ret
    except:
        logging.exception("up error")
        return "error.."


def get_rankinfo(uid, groupid, bid, hid=1, mod=-1):
    logging.info('查询用户[%s]'%uid)
    ret = score.hid_ranks(bid, groupid, hid, mod)
    o = osu_user.Osuer()
    if not ret:
        return '榜上一个成绩都没有!!! https://osu.ppy.sh/b/%s' % bid
    ret = ret[0]
    outstr = '%s(%s)-%s[%s]\n' % (ret['source'], ret['artist'], ret['title'], ret['version'])
    uids = []
    for i,r in enumerate(json.loads(ret['rankjson'])[:10]):
        for k,v in r.items():
            uid = k
            uids.append(uid)
            sco = v
        m = ','.join(mods.getMod(int(sco[5])))
        outstr += '#%s {%s} %s分 [%sx] %s%% %s +%s\n' % (i+1, uid, sco[0], sco[1], sco[3], sco[4], m)
    res = o.get_usernames_by_uid(uids)
    for r in res:
        restr = '{%s}' % r['osuid']
        outstr = outstr.replace(restr, r['osuname'])
    return outstr[:-1]

def get_topsnum(uid, groupid, hid, mod=-1):
    ret = score.hid_mytops(uid, groupid, hid=1, mods=-1)
    if not ret:
        return '太可怜了，没有一个榜top1与{uid}有缘！'
    outstr = "{uid} 's top榜(%s个)\n" % len(ret)
    ret = ret[-1:-11:-1]
    for i,r in enumerate(ret):
        outstr = outstr + '[%s]https://osu.ppy.sh/b/%s\n' % (i+1,r['bid'])
    return outstr[:-1]

def get_topsrank(groupid, hid=1):
    ret = score.tops_rank(groupid, hid=hid)
    if not ret:
        return '你群0个榜???'
    u = osu_user.Osuer()
    uret = u.get_user_from_db3([r['uid'] for r in ret])
    udict = {r['osuid']:r['osuname'] for r in uret}
    outstr = "top榜拥有数排行\n"
    for i,r in enumerate(ret):
        outstr = outstr + '#%s %s [%s]\n' % (i+1, udict[r['uid']], r['num'])
    return outstr[:-1]

def set_alias(msg):
    ml = msg.split(' ')
    if len(ml) != 3:
        return 'usage {!setb bid name} ps:别名带上难度，保证唯一性'
    ret = score.alias2db(ml[2], bid=ml[1], uid='')
    if ret == -1:
        return '设置失败，可能重复别名'
    return 'set success'

def del_alias(c):
    ret = score.delalias(c)
    if ret == -1 or ret == 0:
        return 'del fail'
    return 'del success'

def bind_irc(msg, qq):
    uid = args_func.uid_find_or_input(qq=qq, return_type=1)
    if not uid:
        return 'QQ请绑定ID,再进行irc绑定!'
    ml = msg.split(' ')
    if len(ml) != 2:
        return 'usage {!bind 1/2/3} (1:新人群,2:分群,3:开发群)请绑定唯一群'
    else:
        gid = Config.GROUP_IRC.get(ml[1], -1)

    if gid == -1:
        return 'usage {!bind 1/2/3} (1:新人群,2:分群,3:开发群)请绑定唯一群'

    ret = score.bind_group_irc(uid, gid, qq)
    if ret == -1:
        return 'irc绑定异常'
    return 'bind success'