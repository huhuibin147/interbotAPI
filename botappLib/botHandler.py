# -*- coding: utf-8 -*-
import os
import re
import time
import json
import random
import logging
import traceback
from io import TextIOWrapper
from commLib import cmdRouter
from commLib import mods
from commLib import interMysql
from botappLib import healthCheck

class botHandler():


    def __init__(self):
        self.osufiledir = '/data/osufile/'
    
    def getOsuInfo(self, qqid, groupid):
        """取osu用户绑定信息
        Args:
            qq/groupid
        """
        ret = cmdRouter.invoke(
            '!uinfo', {"qqid": qqid, "groupid": groupid}
        )
        return json.loads(ret)

    def getOsuInfoFromAPI(self, osuid):
        """取osu用户信息 通过ppy
        Args:
            osuid
        """
        ret = cmdRouter.invoke('!osuerinfo', {"osuid": osuid})
        return json.loads(ret)

    def getRecInfo(self, osuid, limit):
        """取osu用户rec信息
        Args:
            osuid
            limit
        """
        ret = cmdRouter.invoke(
            '!rec', {"osuid": osuid, "limit": limit}
        )
        return json.loads(ret)

    def getRecBp(self, osuid, limit):
        """取osu用户bp信息
        Args:
            osuid
            limit
        """
        ret = cmdRouter.invoke(
            '!bp', {"osuid": osuid, "limit": limit}
        )
        return json.loads(ret)


    def getOppaiInfo(self, bid, extend=''):
        """取oppai结果
        Args:
            bid
            extend 附加条件  参考git
        """
        ret = cmdRouter.invoke('!oppai', {"bid": bid, "extend": extend})
        return json.loads(ret)

    def getOsuFile(self, bid):
        """取osu文件，做存储
        Args:
            bid
        """
        ret = cmdRouter.invoke('!osufile', {"bid": bid})
        return json.loads(ret)

    def getOsuBeatMap(self, bid):
        """取osu beatmap信息
        Args:
            bid
        """
        ret = cmdRouter.invoke('!beatmap', {"bid": bid})
        return json.loads(ret)

    def getSkillInfo(self, osuname):
        """取osu skill信息
        Args:
            osuname
        """
        ret = cmdRouter.invoke('!osuskill', {"osuname": osuname})
        return ret

    def getRctppRes(self, recinfo):
        # rec计算
        bid = recinfo['beatmap_id']
        rinfo = self.exRecInfo(recinfo)
        extend = self.convert2oppaiArgs(**rinfo) 
        ojson = self.oppai2json(bid, extend)

        # fc计算
        fcacc = self.calFcacc(recinfo)
        extendFc = self.convert2oppaiArgs(rinfo['mods'], fcacc)
        ojsonFc = self.oppai2json(bid, extendFc)

        # ac计算
        extendSs = self.convert2oppaiArgs(rinfo['mods'])
        ojsonSs = self.oppai2json(bid, extendSs)

        res = self.formatRctpp2(ojson, recinfo['rank'], rinfo['acc'], 
            ojsonFc['pp'], ojsonSs['pp'], bid, fcacc, recinfo['countmiss'])

        return res

    def oppai(self, bid, extend=''):
        """取oppai结果
        Args:
            bid
            extend 附加条件  参考git
        """
        try:
            self.downOsufile(bid)
            ret = os.popen('cat /data/osufile/%s.osu | /root/oppai/./oppai - %s' % (bid, extend))
            logging.info('bid[%s],extend[%s]', bid, extend)
            return ret.read()
        except:
            logging.error(traceback.print_exc())
            return ''

    def oppai2json(self, bid, extend=''):
        """取oppai结果 json"""
        try:
            self.downOsufile(bid)
            ret = os.popen('cat /data/osufile/%s.osu | /root/oppai/./oppai - %s -ojson' % (bid, extend))
            logging.info('bid[%s],extend[%s]', bid, extend)
            return json.loads(ret.read())
        except:
            logging.error(traceback.print_exc())
            return {}
        

    def downOsufile(self, bid):
        """down osu file"""
        f = '%s%s.osu' % (self.osufiledir, bid)
        if not os.path.exists(f):
            logging.info('[%s.osu]不存在,进行download', bid)
            os.system('curl https://osu.ppy.sh/osu/{0} > /data/osufile/{0}.osu'.format(bid))
        return

    def convert2oppaiArgs(self, mods='', acc='', cb='', miss=''):
        """oppai参数转换"""
        args = ''
        if mods:
            args += '+%s ' % mods
        if acc:
            args += '%s%% ' % acc
        if cb:
            args += '%sx ' % cb
        if miss:
            args += '%sm' % miss
        return args

    def exRecInfo(self, rec):
        """从rec api中提取信息"""
        mod = mods.getMod(rec['enabled_mods'])
        if 'NONE' in mod:
            mod.remove('NONE')
        ret = {
            "mods": ''.join(mod),
            "acc": mods.get_acc(rec['count300'], rec['count100'], rec['count50'], rec['countmiss']),
            "cb": rec['maxcombo'],
            "miss": rec['countmiss']
        }
        return ret

    def calFcacc(self, rec):
        acc = mods.get_acc(rec['count300'], rec['count100'], rec['count50'], 0)
        return acc

    def factBpm(self, rawbpm, modstr):
        bpm = rawbpm
        if 'DT' in modstr or 'NC' in modstr:
            bpm = rawbpm * 1.5
        elif 'HT' in modstr:
            bpm = rawbpm / 0.75
        return round(bpm)

    def formatRctpp2(self, ojson, rank, acc, ppfc, ppss, bid, fcacc, miss):
        """格式化rctpp输出"""
        outp = '{artist} - {title} [{version}] \n'
        outp += 'Beatmap by {creator} \n'
        outp += '[ar{ar} cs{cs} od{od} hp{hp}  bpm{bpm}]\n\n'
        outp += 'stars: {stars}* | {mods_str} \n'
        outp += '{combo}x/{max_combo}x | {acc}% | {rank} \n\n'
        outp += '{acc}%: {pp}pp\n'
        outp += '{fcacc}%: {ppfc}pp\n'
        outp += '100.0%: {ppss}pp\n'
        outp += '{missStr}\n'
        outp += 'https://osu.ppy.sh/b/{bid}'

        missStr = self.missReply(miss, acc, ojson['ar'], 
            ojson['combo'], ojson['max_combo'], ojson['stars'])

        mapInfo = self.getOsuBeatMapInfo(bid)
        bpm = self.factBpm(float(mapInfo['bpm']), ojson['mods_str'])
 
        out = outp.format(
            artist = mapInfo['artist'],
            title = mapInfo['title'],
            version = mapInfo['version'],
            creator = mapInfo['creator'],
            ar = ojson['ar'],
            cs = ojson['cs'],
            od = ojson['od'],
            hp = ojson['hp'],
            stars = round(ojson['stars'], 2),
            combo = ojson['combo'],
            max_combo = ojson['max_combo'],
            acc = round(acc, 2),
            mods_str = ojson['mods_str'],
            pp = round(ojson['pp'], 2),
            rank = rank,
            ppfc = round(ppfc, 2),
            ppss = round(ppss, 2),
            bid = bid,
            fcacc = fcacc,
            miss = miss,
            missStr = missStr,
            bpm = bpm
        )

        return out

    def missReply(self, miss, acc, ar, cb, maxcb, stars):
        miss = int(miss)
        r = 'emmm不知道说什么了'
        ar = float(ar)
        stars = float(stars)
        cb = int(cb)
        maxcb = int(cb)
        if miss == 0:
            if maxcb != cb:
                r = '感受滑条的魅力吧'
            else:
                if acc == 100:
                    r = '跟我一起喊爷爷!'
                elif acc >= 99:
                    r = 'emmm恐怖,建议踢了'
                else:
                    l = ['您还是人马，0miss??',
                        'miss?不存在的!']
                    r = random.choice(l)
        else:
            if miss == 1:
                if stars < 5:
                    l = ['1miss,治治你的手抖吧',
                        '1miss,再肛一肛，pp就到手了',
                        '专业破梗1miss大法上下颠倒hr']
                    r = random.choice(l)
                else:
                    l = ['1miss，pp飞了，心痛吗',
                        '出售专治1Miss绝症药，5块/瓶',
                        '差点你就爆了一群爷爷了,1miss距离',
                        '1miss惨案,默哀5分钟']
                    r = random.choice(l)
            elif miss < 10:
                if stars < 5:
                    l = ['%smiss，你还没fc吗' % miss, 
                        '%smiss，再糊糊可能就fc了' % miss]
                    r = random.choice(l)
                elif stars < 7:
                    r = '%smiss，有点恐怖啊你' % miss
                else:
                    r = '%smiss，你是什么怪物' % miss

            else:
                if stars < 4:
                    r = '打个低星图，还能%smiss，删游戏吧' % miss
                else:
                    if ar > 9.7:
                        r = '%smiss，dalou建议你开ez玩' % miss
                    elif miss > 50:
                        r = '%smiss，太菜了，不想评价' % miss
                    else:
                        r = '%smiss，接收功能建议' % miss


        if random.randint(0,100) < 20:
            r = '%smiss，接收评价建议' % miss
        return r

    def osuBeatmapInfoFromDb(self, bid):
        db = interMysql.Connect('osu')
        sql = '''
            SELECT mapjson 
            FROM beatmap WHERE bid = %s
        '''
        rs = db.query(sql, [bid])
        if not rs:
            return {}
        else:
            mapInfo = rs[0]
            return json.loads(mapInfo['mapjson'])

    def map2db(self, args):
        try:
            db = interMysql.Connect('osu')
            sql = '''
                INSERT into beatmap(bid, source, artist, title, 
                    version, creator, stars, addtime, mapjson) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            ret = db.executeMany(sql, args)
            db.commit()
            logging.info('map入库记录[%s]', ret)
            return ret
        except:
            db.rollback()
            logging.error(traceback.print_exc())

    def getOsuBeatMapInfo(self, bid):
        """取map信息，从库中取，取不到再取api
        Returns:
            dict 数据格式以ppy为准
        """
        dbMapInfo = self.osuBeatmapInfoFromDb(bid)
        if not dbMapInfo:
            dbMapInfo = self.getOsuBeatMap(bid)
            if dbMapInfo:
                dbMapInfo = dbMapInfo[0]
                insertArgs = [[
                    dbMapInfo["beatmap_id"], 
                    dbMapInfo['source'], 
                    dbMapInfo['artist'], 
                    dbMapInfo['title'], 
                    dbMapInfo['version'], 
                    dbMapInfo['creator'], 
                    dbMapInfo['difficultyrating'],
                    dbMapInfo['last_update'],
                    json.dumps(dbMapInfo) 
                ]]
                self.map2db(insertArgs)
            else:
                dbMapInfo = {}
        return dbMapInfo

    def bbpOutFormat(self, bp5, ousname):
        """bbp输出格式化
        """
        s_msg = "%s's bp!!\n" % ousname
        for i,r in enumerate(bp5[0:5]):
            msg = 'bp{x},{pp}pp,{acc}%,{rank},+{mod}'
            c50 = float(r['count50'])
            c100 = float(r['count100'])
            c300 = float(r['count300'])
            cmiss = float(r['countmiss'])
            acc = round((c50*50+c100*100+c300*300)/(c50+c100+c300+cmiss)/300*100, 2)
            msg = msg.format(
                x=i+1,
                pp=round(float(r['pp'])),
                acc=acc,rank=r['rank'],
                mod=','.join(mods.getMod(int(r['enabled_mods'])))
            )
            s_msg = s_msg + msg + '\n'
        return s_msg[:-1]

    def helpFormatOut(self):
        cmdInfo = self.cmdRefFromDb(level=[1])
        rs = 'interbot2 v1.0 (%s个功能)\n' % len(cmdInfo)
        for i, c in enumerate(cmdInfo):
            rs += '{}.[{}] {}\n'.format(
                    i+1, c["cmd"], c["reply"]
                )
        return rs[:-1]

    def cmdRefFromDb(self, level):
        """命令信息
        Args:
            level  
                Type:list
                Default: 1
        """
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT cmd, reply 
            FROM cmdRef WHERE level in (%s)
        '''
        if not level:
            level = [1]
        sql = sql % ','.join([str(l) for l in level])
        rs = db.query(sql)
        return rs

    def testFormatOut(self, userinfo, bp):
        """test输出
        """
        rs = healthCheck.health_check(userinfo, bp)
        return rs

    def todaybp(self, uid):
        # 来自int100
        bps = self.getRecBp(uid, "100")

        if len(bps) == 0:
            return '这人没有bp!!!'

        todaybp = []
        today = int(time.strftime("%Y%m%d", time.localtime()))
        i = 1
        for bp in bps:
            date = int(time.strftime("%Y%m%d", time.localtime(time.mktime(time.strptime(bp['date'], "%Y-%m-%d %H:%M:%S")))))
            if date == today:
                bp['num'] = i
                todaybp.append(bp)
            i = i + 1

        if len(bp) == 0:
            return "你太菜了!一个bp都没更新!!"

        mtext = "%s today's bp：\n" % uid

        for bp in todaybp:
            acc = mods.get_acc(bp['count300'], bp['count100'], bp['count50'], bp['countmiss'])
            mod = mods.get_mods_name(bp['enabled_mods'])
            mtext = mtext + "bp%s,%.2fpp,%.2f%%,%s,+%s\n" % (bp['num'], float(bp['pp']), acc, bp['rank'], mod)

        return mtext[:-1]

