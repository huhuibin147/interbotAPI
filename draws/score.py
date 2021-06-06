# -*- coding: utf-8 -*-
import traceback
import json
import logging
from commLib import interMysql
from commLib import mods

def map2db(args):
    try:
        conn = interMysql.Connect('osu')
        sql = '''
            INSERT into beatmap(bid, source, artist, title, version, creator, stars, addtime, mapjson) 
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            source=%s, artist=%s, title=%s, version=%s, creator=%s, stars=%s, addtime=%s, mapjson=%s
        '''
        ret = conn.executeMany(sql, args)
        conn.commit()
        logging.info('map入库记录 %s' % ret)
        return ret
    except:
        conn.rollback()
        traceback.print_exc()

def rec2db(args):
    try:
        conn = interMysql.Connect('osu')
        sql = '''
            INSERT into recinfo(hid, bid, uid, score, maxcombo, mods, playdate, lastdate, rank, recjson) 
            VALUES(%s, %s, %s, %s, %s, %s, %s, now(), %s, %s)
            ON DUPLICATE KEY UPDATE 
            score=%s, maxcombo=%s, playdate=%s, lastdate=now(), rank=%s, recjson=%s
        '''
        ret = conn.executeMany(sql, args)
        conn.commit()
        logging.info('rec入库记录 %s' % ret)
        return ret
    except:
        conn.rollback()
        traceback.print_exc()

def rank2db(args):
    try:
        # print('入库参数:%s'%args)
        conn = interMysql.Connect('osu')
        sql = '''
            INSERT into maprank(gid, hid, bid, uid, type, mods, lastdate, rankjson) 
            VALUES(%s, %s, %s, %s, %s, %s, now(), %s)
            ON DUPLICATE KEY UPDATE 
            uid=%s, type=%s, lastdate=now(), rankjson=%s
        '''
        ret = conn.executeMany(sql, args)
        conn.commit()
        logging.info('rank入库记录 %s' % ret)
        print('rank入库记录 %s' % ret)
        return ret
    except:
        conn.rollback()
        traceback.print_exc()

def alias2db(cname, bid='', uid=''):
    try:
        conn = interMysql.Connect('osu')
        sql = '''
            INSERT into alias(bid, uid, cname) 
            VALUES(%s, %s, %s)
        '''
        ret = conn.execute(sql, [bid, uid, cname])
        conn.commit()
        logging.info('alias入库记录 %s' % ret)
        return ret
    except:
        conn.rollback()
        traceback.print_exc()
        return -1

def delalias(cname):
    try:
        conn = interMysql.Connect('osu')
        sql = '''
            DELETE from alias where cname = %s
        '''
        ret = conn.execute(sql, cname)
        conn.commit()
        logging.info('alias删除记录 %s' % ret)
        return ret
    except:
        conn.rollback()
        traceback.print_exc()
        return -1

def bind_group_irc(osuname, groupid, qq):
    try:
        conn = interMysql.Connect('osu')
        sql = '''
            INSERT into ircbind(osuname, groupid, qq) 
            VALUES(%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            groupid=%s, qq=%s
        '''
        ret = conn.execute(sql, [osuname, groupid, qq, groupid, qq])
        conn.commit()
        logging.info('ircbind入库记录 %s' % ret)
        return ret
    except:
        conn.rollback()
        traceback.print_exc()
        return -1


def check_rec(bids, rec, uid):
    # 提取新记录成绩
    conn = interMysql.Connect('osu')
    sql = '''
        SELECT bid, score, mods from recinfo where bid in (%s) and uid = %s
    '''
    sql = sql % (','.join(map(lambda x:'%s', bids)), uid)
    ret = conn.query(sql, bids)
    if not ret:
        # 成绩过滤
        return rec
    newRec = []
    ret_dict = {}
    # 最大成绩录入
    max_dict = {}
    for r in ret:
        if r['bid'] in ret_dict:
            ret_dict[r['bid']][r['mods']] = r['score']
            if int(r['score']) > max_dict[r['bid']]:
                max_dict[r['bid']] = int(r['score'])
        else:
            ret_dict[r['bid']] = {r['mods']: r['score']}
            max_dict[r['bid']] = int(r['score'])
    # 单mod成绩比较
    for r in rec:
        if r['beatmap_id'] in ret_dict and int(r['enabled_mods']) in ret_dict[r['beatmap_id']]:
            if int(r['score']) > int(ret_dict[r['beatmap_id']][int(r['enabled_mods'])]) or int(r['score']) > max_dict[r['beatmap_id']]:
                newRec.append(r)
        else:
            newRec.append(r)
    return newRec

def filter_beatmapid(bids):
    conn = interMysql.Connect('osu')
    sql = '''
        SELECT bid from beatmap where bid in (%s) 
    '''
    sql = sql % (','.join(map(lambda x:'%s', bids)))
    ret = conn.query(sql, bids)
    db_bids = set([r['bid'] for r in ret])
    new_bids = set(bids) - db_bids
    return list(new_bids)


def maps_top(bids, groupid, hid=1):
    conn = interMysql.Connect('osu')
    sql = '''
        SELECT gid,hid,bid,mods,uid,type,lastdate,rankjson from maprank where gid = %s and hid = %s and bid in (%s)
    '''
    sql = sql % ('%s', '%s', ','.join(map(lambda x:'%s', bids)))
    args = [groupid, hid] + bids
    ret = conn.query(sql, args)
    return ret

def rec_highscore(rec):
    # 过滤同bid成绩，保留不同mod
    newRec = []
    r_dict = {}
    i_s = []
    for i,r in enumerate(rec):
        bid = r['beatmap_id']
        mod = r['enabled_mods']
        score = r['score']
        if bid in r_dict:
            if mod in r_dict[bid]:
                if int(score) > int(r_dict[bid][mod][0]):
                    i_s.pop(i_s.index(r_dict[bid][mod][1]))
                    r_dict[bid][mod] = [score, i] 
                    i_s.append(i)
            else:
                r_dict[bid][mod] = [score, i] 
                i_s.append(i)
        else:
            r_dict[bid] = {}
            r_dict[bid][mod] = [score, i] 
            i_s.append(i)
    for i,r in enumerate(rec):
        if i in i_s:
            newRec.append(r)
    return newRec

def rec_highscore_nomod(rec):
    # 只保留最高分bid，mod去除，总榜使用
    newRec = []
    r_dict = {}
    i_s = []
    for i,r in enumerate(rec):
        bid = r['beatmap_id']
        mod = r['enabled_mods']
        score = r['score']
        if bid in r_dict:
            if int(score) > int(r_dict[bid][0]):
                i_s.pop(i_s.index(r_dict[bid][1]))
                r_dict[bid] = [score, i] 
                i_s.append(i)
        else:
            r_dict[bid] = [score, i] 
            i_s.append(i)
    for i,r in enumerate(rec):
        if i in i_s:
            newRec.append(r)
    return newRec

def map_rank(rec, groupid, hid=1, rtype=1, topslimit=50):
    bids = [r['beatmap_id'] for r in rec]
    ranks_ret = maps_top(bids, groupid, hid)
    topusers, rankjsons = [],[]
    # print('rtype%s,rec %s'%(rtype,rec))
    newRec = []
    # 总榜处理,对rec进行扩展
    if rtype == 1:
        # mod成绩优化
        rec = rec_highscore_nomod(rec)

        for r in rec:
            r['true_mods'] = r['enabled_mods']
            r['enabled_mods'] = -1
    if not ranks_ret:
        newRec = rec
        topusers = [r['user_id'] for r in rec]
        # {uname:[score,cb,time]}
        if rtype == 1:
            rankjsons = [json.dumps([{t['user_id']: [t['score'], t['maxcombo'], t['date'], mods.get_acc(t['count300'],\
                t['count100'], t['count50'], t['countmiss']), t['rank'], t['true_mods']]}]) for t in rec]
        else:
            rankjsons = [json.dumps([{t['user_id']: [t['score'], t['maxcombo'], t['date'], mods.get_acc(t['count300'],\
                t['count100'], t['count50'], t['countmiss']), t['rank'], t['enabled_mods']]}]) for t in rec]
    else:
        # 两个分支
        ranks_dict = {}
        for r in ranks_ret:
            # groupid,hid固定，免去判断
            if r['bid'] not in ranks_dict:
                ranks_dict[r['bid']] = {}
            ranks_dict[r['bid']][r['mods']] = [r['gid'], r['hid'], r['uid'], r['type'], r['lastdate'], r['rankjson']]
        for r in rec:
            # 已存在榜单
            if str(r['beatmap_id']) in ranks_dict and int(r['enabled_mods']) in ranks_dict[r['beatmap_id']]:
                # 入榜判断
                rankj = ranks_dict[r['beatmap_id']][int(r['enabled_mods'])][-1]
                rankj = json.loads(rankj)
                score_list = []
                topuser_list = []
                for rs in rankj:
                    for k,v in rs.items():
                        score_list.append(int(v[0]))
                        topuser_list.append(k)
                # 原上榜成绩,更新判断
                up_flag = 0
                if str(r['user_id']) in topuser_list:
                    # 刷新成绩
                    i = topuser_list.index(r['user_id'])
                    if int(r['score']) > score_list[i]:
                        score_list.pop(i)
                        rankj.pop(i)
                        up_flag = 1
                        newRec.append(r)
                    else:
                        continue
                else:
                    up_flag = 1
                    newRec.append(r)

                if up_flag == 1:
                    # 成绩查找
                    inindex = check_rankj(score_list, r['score'])
                    m = r['true_mods'] if rtype == 1 else r['enabled_mods']
                    rankj.insert(inindex, {r['user_id']: [r['score'], r['maxcombo'], r['date'], mods.get_acc(r['count300'],\
                        r['count100'], r['count50'], r['countmiss']), r['rank'], m]})
                    if inindex == 0:
                        topuser = r['user_id']
                    else:
                        topuser = ranks_dict[r['beatmap_id']][int(r['enabled_mods'])][2]
                    rankj = rankj[:topslimit]
                else:
                    topuser = ranks_dict[r['beatmap_id']][int(r['enabled_mods'])][2]
            else:
                # print('重置了！！！！！！！！！')
                topuser = r['user_id']
                m = r['true_mods'] if rtype == 1 else r['enabled_mods']
                rankj = [{r['user_id']: [r['score'], r['maxcombo'], r['date'], mods.get_acc(r['count300'],\
                    r['count100'], r['count50'], r['countmiss']), r['rank'], m]}]
                newRec.append(r)
            topusers.append(topuser)
            rankjsons.append(json.dumps(rankj))
    # 总榜与mod榜分支
    if rtype == 1:
        for r in newRec:
            r['enabled_mods'] = -1
    args = args_format('rank', newRec, groupid=groupid, hid=hid, rtype=rtype, rankjsons=rankjsons, topusers=topusers)
    rank2db(args)

def check_rankj(score_list, score):
    # 成绩查找
    inindex = len(score_list)
    for i,s in enumerate(score_list):
        if int(score) >= s:
            inindex = i
            break
    # print(inindex)
    return inindex



def args_format(agrstype, res, **kwargs):
    args = []
    if agrstype == 'map':
        for r in res:
            r = r[0]
            mapjson = json.dumps(r)
            args.append([r['beatmap_id'], r['source'], r['artist'], r['title'], r['version'], r['creator'], r['difficultyrating'],\
                r['last_update'], mapjson, r['source'], r['artist'], r['title'], r['version'], r['creator'], r['difficultyrating'],\
                r['last_update'], mapjson])
    elif agrstype == 'rec':
        for r in res:
            recjson = json.dumps(r)
            args.append([kwargs.get('hid', 1), r['beatmap_id'], r['user_id'], r['score'], r['maxcombo'], r['enabled_mods'], r['date'], r['rank'],\
                recjson, r['score'], r['maxcombo'], r['date'], r['rank'], recjson])
    elif agrstype == 'rank':
        # 入参的topusers与json以列表传入
        for i,r in enumerate(res):
            args.append([kwargs.get('groupid'), kwargs.get('hid'), r['beatmap_id'], kwargs.get('topusers')[i], kwargs.get('rtype'),\
                r['enabled_mods'], kwargs.get('rankjsons')[i], kwargs.get('topusers')[i], kwargs.get('rtype'),\
                kwargs.get('rankjsons')[i]])
    return args

def hid_ranks(bid, groupid, hid=1, mods=-1):
    # 指定式查询 -- 未扩展
    conn = interMysql.Connect('osu')
    sql = '''
        SELECT a.bid, a.mods, a.rankjson, b.title, b.artist, b.version, b.source, b.mapjson
        from maprank a INNER JOIN beatmap b ON a.bid=b.bid 
        where a.gid = %s and a.hid = %s and a.bid = %s and a.mods = %s
    '''
    ret = conn.query(sql, [groupid, hid, bid, mods])
    return ret

def hid_mytops(uid, groupid, hid=1, mods=-1):
    # top1数量列表
    conn = interMysql.Connect('osu')
    sql = '''
        SELECT bid FROM maprank where gid=%s and hid=%s and mods=%s and uid=%s
    '''
    ret = conn.query(sql, [groupid, hid, mods, uid])
    return ret

def tops_rank(groupid, hid=1):
    # top榜排行
    conn = interMysql.Connect('osu')
    sql = '''
        SELECT uid,count(uid) num FROM maprank 
        WHERE gid = %s and hid = %s and mods = %s
        GROUP BY uid ORDER BY num desc LIMIT 10
    '''
    ret = conn.query(sql, [groupid, hid, -1])
    return ret

def get_alias(cname, rtype=1):
    conn = interMysql.Connect('osu')
    sql = '''
        SELECT * from alias where cname = %s
    '''
    ret = conn.query(sql, cname)
    if not ret:
        return -1
    if rtype == 1:
        return ret[0]['bid']
    elif rtype == 2:
        return ret[0]['uid']

def get_ircbind(osuname):
    conn = interMysql.Connect('osu')
    sql = '''
        SELECT * from ircbind where osuname = %s
    '''
    ret = conn.query(sql, osuname)
    if not ret:
        return -1
    return ret[0]['groupid']
