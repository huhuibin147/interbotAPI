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
from commLib import Config
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

    def getSkillvsInfo(self, osuname, vsosuname):
        """取osu skill vs信息
        Args:
            osuname
            vsosuname
        """
        ret = cmdRouter.invoke('!osuskillvs', 
            {"osuname": osuname, "vsosuname": vsosuname})
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

    def getRctppResNew(self, recinfo):
        # rec计算
        bid = recinfo['beatmap_id']
        rinfo = self.exRecInfo(recinfo)
        extend = self.convert2oppaiArgs(**rinfo) 
        ojson = self.oppai2json(bid, extend)
        pp = self.get_pp_from_str(self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(**rinfo)))

        # fc计算
        fcacc = self.calFcacc(recinfo)
        extendFc = self.convert2oppaiArgs(rinfo['mods'], fcacc)
        fcpp = self.get_pp_from_str(self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods'], fcacc)))

        # ac计算
        extendSs = self.convert2oppaiArgs(rinfo['mods'])
        sspp = self.get_pp_from_str(self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods'])))

        logging.info('ppppppp,%s,%s,%s', pp, fcpp, sspp)

        res = self.formatRctpp2New(ojson, recinfo['rank'], rinfo['acc'], 
            fcpp, sspp, bid, fcacc, recinfo['countmiss'], pp)

        return res

    def getRctppBatchRes(self, recinfos):
        """批量版本
        """
        ret = ""
        l = len(recinfos)
        totalMiss = 0
        totalStars = 0
        totalpp = 0
        totalppfc = 0
        totalppss = 0
        totalacc = 0
        for i, recinfo in enumerate(recinfos):
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

            res, data = self.formatRctpp3(ojson, recinfo['rank'], rinfo['acc'], 
                ojsonFc['pp'], ojsonSs['pp'], bid, fcacc, recinfo['countmiss'])
            totalStars += data["stars"]
            totalMiss += int(data["miss"])
            totalpp += data["pp"]
            totalppfc += data["ppfc"]
            totalppss += data["ppss"] 
            totalacc += data["acc"]

            ret = ret + '[%s].' % (i+1) + res + '\n---------------------------------\n'

        avgStars = round(totalStars/l, 2)
        avgAcc = round(totalacc/l, 2)
        avgMiss = totalMiss/l
        totalpp = round(totalpp, 2)
        totalppfc = round(totalppfc, 2)
        totalppss = round(totalppss, 2)
        ret += '平均star:{stars}*/acc:{acc}%/Miss:{miss}x \n'.format(stars=avgStars, acc=avgAcc, miss=avgMiss) 
        ret += '总计{pp}pp /{ppfc}pp /{ppss}pp'.format(pp=totalpp, ppfc=totalppfc, ppss=totalppss)
        return ret

    def oppai(self, bid, extend=''):
        """取oppai结果
        Args:
            bid
            extend 附加条件  参考git
        """
        try:
            self.downOsufile(bid)
            ret = os.popen('cat /data/osufile/%s.osu | oppai - %s' % (bid, extend))
            logging.info('bid[%s],extend[%s]', bid, extend)
            return ret.read()
        except:
            logging.error(traceback.format_exc())
            return ''

    def ppy_tools_pp(self, bid, extend='', recusion=0):
        """ppy pp计算工具
        """
        try:
            if recusion == 0:
                self.downOsufile(bid)
            else:
                self.downOsufile(bid, compulsiveWrite=1)

            path = Config.PP_TOOLS_PATH
            cmd = 'dotnet %s/PerformanceCalculator.dll simulate osu /data/osufile/%s.osu %s' % (path, bid, extend)
            ret = os.popen(cmd)
            res = ret.read()
            logging.info('bid[%s],extend[%s]', bid, extend)
            return res
        except:
            if recusion == 0:
                return self.oppai2json(bid, extend, recusion=1)
            logging.error(traceback.format_exc())
            return {}

    def get_pp_from_str(self, s):
        """从pp工具返回结果中提取pp值
        Returns:
            pp int
        """
        p = re.compile('pp.*:(.*)') 
        res = p.findall(s) 
        pp = round(float(res[0]))
        return pp


    def oppai2json(self, bid, extend='', recusion=0):
        """取oppai结果 json"""
        try:
            if recusion == 0:
                self.downOsufile(bid)
            else:
                self.downOsufile(bid, compulsiveWrite=1)
            ret = os.popen('cat /data/osufile/%s.osu | oppai - %s -ojson' % (bid, extend))
            logging.info('bid[%s],extend[%s]', bid, extend)
            return json.loads(ret.read())
        except:
            if recusion == 0:
                return self.oppai2json(bid, extend, recusion=1)
            logging.error(traceback.format_exc())
            return {}
        

    def downOsufile(self, bid, compulsiveWrite=0):
        """down osu file"""
        f = '%s%s.osu' % (self.osufiledir, bid)
        if compulsiveWrite == 1 or not os.path.exists(f):
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

    def convert2oppaiArgsNew(self, mods='', acc='', cb='', miss=''):
        """oppai参数转换"""
        args = ''
        for i in range(0, len(mods), 2):
            args += '-m %s ' % mods[i:i+2]
        if acc:
            args += '-a %s ' % acc
        if cb:
            args += '-c %s ' % cb
        if miss:
            args += '-X %s ' % miss
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
            ar = round(ojson['ar'], 2),
            cs = ojson['cs'],
            od = round(ojson['od'], 2),
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

    def formatRctpp2New(self, ojson, rank, acc, ppfc, ppss, bid, fcacc, miss, pp):
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

        mapInfo = self.getOsuBeatMapInfo(bid)

        missStr = self.missReply(miss, acc, ojson['ar'], 
            ojson['combo'], ojson['max_combo'], mapInfo['difficultyrating'])

        bpm = self.factBpm(float(mapInfo['bpm']), ojson['mods_str'])
 
        out = outp.format(
            artist = mapInfo['artist'],
            title = mapInfo['title'],
            version = mapInfo['version'],
            creator = mapInfo['creator'],
            ar = round(ojson['ar'], 2),
            cs = ojson['cs'],
            od = round(ojson['od'], 2),
            hp = ojson['hp'],
            stars = round(float(mapInfo['difficultyrating']), 2),
            combo = ojson['combo'],
            max_combo = ojson['max_combo'],
            acc = round(acc, 2),
            mods_str = ojson['mods_str'],
            pp = pp,
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

    def formatRctpp3(self, ojson, rank, acc, ppfc, ppss, bid, fcacc, miss):
        """格式化rctpp简版输出"""
        outp = '{artist} - {title} [{version}][ar{ar}][bpm{bpm}] {mods_str} \n'
        outp += '{stars}* | {rank} | {acc}% | {combo}x/{max_combo}x | {miss}x \n'
        outp += '{pp}pp /{ppfc}pp /{ppss}pp'

        missStr = self.missReply(miss, acc, ojson['ar'], 
            ojson['combo'], ojson['max_combo'], ojson['stars'])

        mapInfo = self.getOsuBeatMapInfo(bid)
        bpm = self.factBpm(float(mapInfo['bpm']), ojson['mods_str'])
 
        data = {
            'artist': mapInfo['artist'],
            'title': mapInfo['title'],
            'version': mapInfo['version'],
            # 'creator': mapInfo['creator'],
            'ar': ojson['ar'],
            # 'cs': ojson['cs'],
            # 'od': ojson['od'],
            # 'hp': ojson['hp'],
            'stars': round(ojson['stars'], 2),
            'combo': ojson['combo'],
            'max_combo': ojson['max_combo'],
            'acc': round(acc, 2),
            'mods_str': ojson['mods_str'],
            'pp': round(ojson['pp'], 2),
            'rank': rank,
            'ppfc': round(ppfc, 2),
            'ppss': round(ppss, 2),
            # 'bid': bid,
            # 'fcacc': fcacc,
            'miss': miss,
            # 'missStr': missStr,
            'bpm': bpm
        }

        out = outp.format(**data)

        return out, data


    def missReply(self, miss, acc, ar, cb, maxcb, stars):
        miss = int(miss)
        r = 'emmm不知道说什么了'
        ar = float(ar)
        stars = float(stars)
        cb = int(cb)
        maxcb = int(maxcb)
        ranReply = self.replyFromDb()
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
                        r = '%smiss，%s' % (miss, ranReply)


        if random.randint(0,100) < 50:
            r = '%smiss，%s' % (miss, ranReply)
        return r

    def replyFromDb(self):
        """自动回复信息
        """
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT count(1) c FROM defContent 
        '''
        c = db.query(sql)[0]['c']
        skip = random.randint(0, c-1)
        sql2 = '''
            SELECT content FROM defContent
            WHERE ctype = 'rctpp' limit %s, %s
        '''
        args = [skip, 1]
        rs = db.query(sql2, args)
        return rs[0]['content']

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
            logging.error(traceback.format_exc())

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
                mapjson = json.dumps(dbMapInfo) 
                insertArgs = [[
                    dbMapInfo["beatmap_id"], 
                    dbMapInfo['source'], 
                    dbMapInfo['artist'], 
                    dbMapInfo['title'], 
                    dbMapInfo['version'], 
                    dbMapInfo['creator'], 
                    dbMapInfo['difficultyrating'],
                    dbMapInfo['last_update'],
                    mapjson
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
        # 修改自int100
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

    def thanksFormatOut(self):
        rs = '感谢列表\n'
        rs += '------------------\n'
        rs += '1.iron大哥(ironwitness) 2018-08-31 捐赠了50软妹币\n'
        rs += '2.无敌阿卡蕾(arcareh) 2018-08-31 捐赠了66软妹币\n'
        rs += '2.富婆(sxyyyy) 2019-02-03 捐赠了100软妹币\n'
        rs += '------------------\n'
        rs += '小声bibi骗钱万岁'
        return rs

    def getBpNumBybid(self, bplist, ousname, bid):
        """输入bid得到bp几
        """
        rs = ""
        for i, bp in enumerate(bplist):
            if bp["beatmap_id"] == bid:
                rs = 'bid:%s，是你的bp%s' % (bid, str(i+1))
                break
        else:
            rs = "不存在的!" 
        return rs

    def room2DB(self, osuname, qqid, groupid, roomname, roompwd, rtype):
        """入库
        """
        try:
            db = interMysql.Connect('osu')
            sql = '''
                INSERT into room(roomname, password, uid, qq, groupid, 
                    rtype, status, createtime)
                VALUES(%s, %s, %s, %s, %s, %s, %s, now())
            '''
            args = [roomname, roompwd, osuname, qqid, groupid,
                rtype, 0]
            ret = db.execute(sql, args)
            db.commit()
            logging.info('room入库记录[%s]', ret)
            return ret
        except:
            db.rollback()
            logging.error(traceback.format_exc())

    def createMpRoom(self, osuname, qqid, groupid, roomname, roompwd):
        """创建房间
        """
        rs = self.room2DB(osuname, qqid, groupid, roomname, roompwd, rtype='mp')
        if not rs:
            return '创建失败！'
        else:
            return '创建成功！请到游戏中创建mp房，更新mplink！（后续操作查看帮助）'

    def getMpRoom(self, qqid, groupid):
        """取mp房信息
        """
        msg = ''
        rs = self.queryRoomInfo(qqid, groupid)
        if not rs:
            return '不存在记录！'
        # 暂时取第一条
        row = rs[0]
        msg += '房间号:%s\n' % (row['id'])
        msg += '房间名:%s\n' % (row['roomname'])
        msg += '创建者:%s\n' % (row['uid'])
        msg += '密码:%s\n' % (row['password'])
        msg += '房间类型:%s\n' % (row['rtype'])
        msg += '房间状态:%s\n' % (row['status'])
        msg += 'link:%s\n' % (row['mplink'])
        msg += '开始时间:%s\n' % (row['starttime'])
        msg += '创建时间:%s' % (row['createtime'])
        return msg


    def queryRoomInfo(self, qqid, groupid):
        """读库
        """
        db = interMysql.Connect('osu')
        sql = '''
            SELECT id, roomname, mplink, password,
                uid, rtype, status, starttime, 
                createtime
            FROM room 
            WHERE qq = %s and groupid = %s
        '''
        args = [qqid, groupid]
        rs = db.query(sql, args)
        return rs

    def joinMpRoom(self):
        """加房
        """
        rs = self.roomMember2DB()
        if rs:
            return '加入成功！'
        else:
            return '加入失败！'

    def roomMember2DB(self, roomid, mtype, oid, oname, pp, qq, groupid, userjson):
        """入库
        """
        try:
            db = interMysql.Connect('osu')
            sql = '''
                INSERT into roommembers(roomid, membertype, osuuid, osuname, pp, 
                    qq, groupid, userjson)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            '''
            args = [roomid, mtype, oid, oname, pp, qq, groupid, userjson]
            ret = db.execute(sql, args)
            db.commit()
            logging.info('member入库记录[%s]', ret)
            return ret
        except:
            db.rollback()
            logging.error(traceback.format_exc())
