# -*- coding: utf-8 -*-
import sys
sys.path.append('./')

import os
import re
import time
import json
import random
import logging
import datetime
import traceback
from io import TextIOWrapper
from commLib import cmdRouter
from commLib import mods
from commLib import Config
from commLib import interRedis
from commLib import interMysql
from commLib import pushTools
from botappLib import healthCheck
from ppyappLib import ppyHandler
from draws import drawReplay



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
    
    def getOsuInfo2(self, qqid):
        """取osu用户绑定信息
        Args:
            qq
        """
        ret = cmdRouter.invoke(
            '!uinfo2', {"qqid": qqid}
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

    def getBestInfo(self, osuid, bid, limit):
        """取osu用户最好成绩
        Args:
            osuid
            bid
            limit
        """
        ret = cmdRouter.invoke(
            '!ubest', {"osuid": osuid, "bid": bid, "limit": limit}
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

    def getPpplusInfo(self, osuname):
        """取pp+信息
        Args:
            osuname
        """
        ret = cmdRouter.invoke('!ppplus', {"osuname": osuname})
        return ret

    def getRctppRes(self, recinfo, showdate=None):
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

        res, kv  = self.formatRctpp2(ojson, recinfo['rank'], rinfo['acc'], 
            ojsonFc['pp'], ojsonSs['pp'], bid, fcacc, recinfo['countmiss'], showdate)

        return res, kv 

    def getRctppResNew(self, recinfo):
        # rec计算
        bid = recinfo['beatmap_id']
        rinfo = self.exRecInfo(recinfo)
        extend = self.convert2oppaiArgs(**rinfo) 
        ojson = self.oppai2json(bid, extend)
        # pp = self.get_pp_from_str(self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(**rinfo)))
        newppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(**rinfo))
        pp = newppMap.get("pp")
        star = newppMap.get("difficulty_attributes", {}).get("star_rating")

        # fc计算
        fcacc = self.calFcacc(recinfo)
        extendFc = self.convert2oppaiArgs(rinfo['mods'], fcacc)
        ojsonFc = self.oppai2json(bid, extendFc)
        fcppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods'], fcacc, 
                            int(newppMap['performance_attributes']['max_combo']), 0, rinfo['count100'], rinfo['count50']))
        fcpp = fcppMap.get("pp")
        fcCalAcc = fcppMap.get("score", {}).get("accuracy")

        # ac计算
        extendSs = self.convert2oppaiArgs(rinfo['mods'])
        ojsonSs = self.oppai2json(bid, extendSs)
        ssppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods']))
        sspp = ssppMap.get("pp")

        res, kv = self.formatRctpp2New(ojson, recinfo['rank'], rinfo['acc'], 
            fcpp, sspp, bid, fcCalAcc, recinfo['countmiss'], pp, star, ojsonFc['pp'], ojsonSs['pp'])

        return res, kv 

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

    def getRctppBatchRes2(self, recinfos):
        """批量版本2
        """
        ret = ""
        l = len(recinfos)
        totalMiss = 0
        totalStars = 0
        totalpp = 0
        totalppfc = 0
        totalppss = 0
        totalacc = 0
        # 需要切换到新的上 to-do
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

            res, data = self.formatRctpp4(ojson, recinfo['rank'], rinfo['acc'], 
                ojsonFc['pp'], ojsonSs['pp'], bid, fcacc, recinfo['countmiss'])
            totalStars += data["stars"]
            totalMiss += int(data["miss"])
            totalpp += data["pp"]
            totalppfc += data["ppfc"]
            totalppss += data["ppss"] 
            totalacc += data["acc"]

            ret += f'{res}' 
            ret += '\n---------------------------------\n'

        avgStars = round(totalStars/l, 2)
        avgAcc = round(totalacc/l, 2)
        avgPp = round(totalpp/l, 0)
        
        ret += f"{avgStars}* - {avgAcc:.1f}% - {avgPp:.0f}pp (ps:这个是老算法)"
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
            cmd = 'dotnet %s/PerformanceCalculator.dll simulate osu /data/osufile/%s.osu -j %s' % (path, bid, extend)
            ret = os.popen(cmd)
            res = ret.read()
            logging.info('bid[%s],extend[%s]', bid, extend)
            logging.info(res)
            return json.loads(res)
        except:
            logging.error(traceback.format_exc())
            if recusion == 0:
                return self.oppai2json(bid, extend, recusion=1)
            return {}
    
    def ppy_tools_difficulty(self, bid, extend=''):
        """ppy 地图难度计算工具
        """
        try:
            path = Config.PP_TOOLS_PATH
            extendStr = ''
            for index in range(0, len(extend)):
                if(index % 2 == 0):
                   extendStr += ' -m '
                extendStr += extend[index]

            cmd = 'dotnet %s/PerformanceCalculator.dll difficulty /data/osufile/%s.osu %s' % (path, bid, extendStr)
            ret = os.popen(cmd)
            res = ret.read()
            logging.info(res)
            difficulty = self.get_difficulty_from_str(res, bid)
            return difficulty
        except:
            logging.error(traceback.format_exc())
            return -1

    def get_pp_from_str(self, s):
        """从pp工具返回结果中提取pp值
        Returns:
            pp int
        """
        p = re.compile('pp.*:(.*)') 
        res = p.findall(s) 
        pp = round(float(res[0]), 2)
        return pp

    def get_difficulty_from_str(self, s, bid):
        p = re.compile('\d{1,4}\.\d\d')
        res = p.findall(s)
        if not res:
            p = re.compile('\d')
            p2 = re.compile('\d+ - .*[),\]]+')
            r_str = re.sub(p2, '', s)
            rs = p.findall(r_str)
            logging.info(rs)
            r = '%s.%s%s' % (rs[0], rs[1], rs[2])
        else:
            r = res[0]
        return float(r)

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

    def convert2oppaiArgs(self, mods='', acc='', cb='', miss='', **kwargs):
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

    def convert2oppaiArgsNew(self, mods='', acc='', cb='', miss='', count100='', count50='', **kwargs):
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
        if count100:
            args += '-G %s ' % count100
        if count50:
            args += '-M %s ' % count50
        return args

    def exRecInfo(self, rec):
        """从rec api中提取信息"""
        mod = mods.getMod(rec['enabled_mods'])
        if 'NONE' in mod:
            mod.remove('NONE')
        logging.info(rec)
        ret = {
            "mods": ''.join(mod),
            "acc": mods.get_acc(rec['count300'], rec['count100'], rec['count50'], rec['countmiss']),
            "cb": rec['maxcombo'],
            "miss": rec['countmiss'],
            "count100": rec['count100'],
            "count50": rec['count50'],
        }
        return ret

    def calFcacc(self, rec):
        acc = mods.get_acc(int(rec['count300'])+int(rec['countmiss']), rec['count100'], rec['count50'], 0)
        return acc

    def factBpm(self, rawbpm, modstr):
        bpm = rawbpm
        if 'DT' in modstr or 'NC' in modstr:
            bpm = rawbpm * 1.5
        elif 'HT' in modstr:
            bpm = rawbpm * 0.75
        return round(bpm)

    def formatRctpp2(self, ojson, rank, acc, ppfc, ppss, bid, fcacc, miss, showdate=None):
        """格式化rctpp输出"""
        outp = '{artist} - {title} [{version}] \n'
        outp += 'Beatmap by {creator} \n'
        outp += '[ar{ar} cs{cs} od{od} hp{hp}  bpm{bpm}]\n'
        outp += Config.bg_thumb
        outp += 'stars: {stars}* | {mods_str} \n'
        outp += '{combo}x/{max_combo}x | {acc}% | {rank} \n\n'
        outp += '{acc}%: {pp}pp\n'
        outp += '{fcacc}%: {ppfc}pp\n'
        outp += '100.0%: {ppss}pp\n'
        outp += '{missStr}\n'
        if showdate:
            outp += f'{showdate}\n'
        outp += 'https://osu.ppy.sh/b/{bid}'

        missStr = self.missReply(miss, acc, ojson['ar'], 
            ojson['combo'], ojson['max_combo'], ojson['stars'])

        mapInfo = self.getOsuBeatMapInfo(bid)
        bpm = self.factBpm(float(mapInfo['bpm']), ojson['mods_str'])
        ar = round(ojson['ar'], 2)
        acc = round(acc, 2)
 
        out = outp.format(
            artist = mapInfo['artist'],
            title = mapInfo['title'],
            version = mapInfo['version'],
            creator = mapInfo['creator'],
            ar = ar,
            cs = ojson['cs'],
            od = round(ojson['od'], 2),
            hp = ojson['hp'],
            stars = round(ojson['stars'], 2),
            combo = ojson['combo'],
            max_combo = ojson['max_combo'],
            acc = acc,
            mods_str = ojson['mods_str'],
            pp = round(ojson['pp'], 2),
            rank = rank,
            ppfc = round(ppfc, 2),
            ppss = round(ppss, 2),
            bid = bid,
            fcacc = fcacc,
            miss = miss,
            missStr = missStr,
            bpm = bpm,
            sid = mapInfo["beatmapset_id"]
        )
        # 供外部smoke使用
        kv = {
            "stars": ojson['stars'], 
            "rank": rank,
            "ar": ar,
            "acc": acc
        }
        return out, kv


    def formatRctpp2New(self, ojson, rank, acc, ppfc, ppss, bid, fcacc, miss, pp, stars, oldfcpp, oldsspp):
        """格式化rctpp输出"""
        outp = '{artist} - {title} [{version}] \n'
        outp += 'Beatmap by {creator} \n'
        outp += '[ar{ar} cs{cs} od{od} hp{hp}  bpm{bpm}]\n'
        outp += Config.bg_thumb
        outp += 'stars: {stars}*({oldstar}*) | {mods_str} \n'
        outp += '{combo}x/{max_combo}x | {acc}% | {rank} \n\n'
        outp += '{acc}%: {pp}pp({oldpp}pp)\n'
        outp += '{fcacc}%: {ppfc}pp({oldfcpp}pp)\n'
        outp += '100.0%: {ppss}pp({oldsspp}pp)\n'
        outp += '{missStr}\n'
        outp += 'https://osu.ppy.sh/b/{bid}'

        mapInfo = self.getOsuBeatMapInfo(bid)
        # if not ojson['mods_str']:
        #     stars = mapInfo['difficultyrating']
        # else:
        #     stars = self.ppy_tools_difficulty(bid, ojson['mods_str'])
        #     if stars == -1:
        #         stars = mapInfo['difficultyrating']

        stars = round(float(stars), 2)
        missStr = self.missReply(miss, acc, ojson['ar'], 
            ojson['combo'], ojson['max_combo'], stars)

        bpm = self.factBpm(float(mapInfo['bpm']), ojson['mods_str'])
        ar = round(ojson['ar'], 2)
        fcacc = round(fcacc, 2)
 
        out = outp.format(
            artist = mapInfo['artist'],
            title = mapInfo['title'],
            version = mapInfo['version'],
            creator = mapInfo['creator'],
            ar = ar,
            cs = ojson['cs'],
            od = round(ojson['od'], 2),
            hp = ojson['hp'],
            stars = stars,
            oldstar = round(ojson['stars'], 2),
            combo = ojson['combo'],
            max_combo = ojson['max_combo'],
            acc = round(acc, 2),
            mods_str = ojson['mods_str'],
            pp = round(pp),
            rank = rank,
            ppfc = round(ppfc),
            ppss = round(ppss),
            bid = bid,
            fcacc = fcacc,
            miss = miss,
            missStr = missStr,
            bpm = bpm,
            sid = mapInfo["beatmapset_id"],
            oldpp = round(ojson['pp']),
            oldfcpp = round(oldfcpp),
            oldsspp = round(oldsspp),
        )
        # 供外部smoke使用
        kv = {
            "stars": stars, 
            "rank": rank,
            "ar": ar,
            "acc": acc
        }
        return out, kv

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

    def formatRctpp4(self, ojson, rank, acc, ppfc, ppss, bid, fcacc, miss):
        """格式化rctpp简版输出"""
        outp = ''
        outp += Config.bg_thumb
        outp += '[{stars}* ar{ar:.1f} bpm{bpm:.0f}] {mods_str}\n'
        outp += '{combo}x/{max_combo}({miss}x) | {acc:.1f}% | {rank} \n'
        outp += '{pp:.0f}pp | {ppfc:.0f}pp | {ppss:.0f}pp'

        missStr = self.missReply(miss, acc, ojson['ar'], 
            ojson['combo'], ojson['max_combo'], ojson['stars'])

        mapInfo = self.getOsuBeatMapInfo(bid)
        bpm = self.factBpm(float(mapInfo['bpm']), ojson['mods_str'])
 
        data = {
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
            'miss': miss,
            'bpm': bpm,
            'sid': mapInfo["beatmapset_id"]
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

    def bbpOutFormat(self, bp5, ousname, offset=0):
        """bbp输出格式化
        """
        s_msg = "%s's bp!!\n" % ousname
        for i,r in enumerate(bp5[0:5]):
            msg = 'bp{x}, {pp}pp,{acc:.2f}%,{rank},+{mod}'
            c50 = float(r['count50'])
            c100 = float(r['count100'])
            c300 = float(r['count300'])
            cmiss = float(r['countmiss'])
            acc = round((c50*50+c100*100+c300*300)/(c50+c100+c300+cmiss)/300*100, 2)
            msg = msg.format(
                x=i+offset,
                pp=round(float(r['pp'])),
                acc=acc,rank=r['rank'],
                mod=','.join(mods.getMod(int(r['enabled_mods'])))
            )
            s_msg = s_msg + msg + '\n'
        return s_msg[:-1]

    def bbpOutFormat2(self, bp5, ousname, offset=0):
        """bbp输出格式化
        """
        s_msg = "%s's bp!!\n" % ousname
        for i,r in enumerate(bp5[0:3]):
            mapInfo = self.getOsuBeatMapInfo(r["beatmap_id"])
            msg = Config.bg_thumb.format(sid=mapInfo["beatmapset_id"])
            msg += 'bp{x}, {pp}pp,{acc:.2f}%,{rank},+{mod}'
            c50 = float(r['count50'])
            c100 = float(r['count100'])
            c300 = float(r['count300'])
            cmiss = float(r['countmiss'])
            acc = round((c50*50+c100*100+c300*300)/(c50+c100+c300+cmiss)/300*100, 2)
            msg = msg.format(
                x=i+offset,
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

        if len(todaybp) == 0:
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
        rs += '3.富婆(sxyyyy) 2019-02-03 捐赠了100软妹币\n'
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

    def rctppSmoke(self, groupid, qq, kv, iswarn=0):
        """超星机制
        Args:
            iswarn:
                提醒模式
        规则：
            新人群
                5.7星 0.01*10分钟
                6.0星 0.01*20分钟
                ar > 9.7 & acc < 90%  0.1*60分钟
            进阶群
                6.51-8.00 评级A以下 0.01*10分钟
                8.01-20.00 fail    0.01*20分钟
        """
        flag = 0
        stars = kv["stars"]
        rank = kv["rank"]
        acc = kv["acc"]
        ar = kv["ar"]
        logging.info(kv)
        ts = 0
        res_mark = []
        if int(groupid) == Config.GROUPID["XINRENQUN"]:
            if stars > 5.7:
                if stars < 6:
                    ts += (stars - 5.7) * 10 * 6000
                else:
                    ts += (stars - 5.7) * 20 * 6000
                res_mark.append(f'超星法(>5.7*)，你打了{stars:.1f}*')
                flag = 1
            
            # if ar > 9.7 and acc < 90:
            #     ts += (ar - 9.7) * 36000
            #     res_mark.append('高ar法(ar>9.7&acc<90)')
            #     flag = 1
            
            if ts > 0:
                # 记录时间
                rds = interRedis.connect('osu2')
                nowts = time.time()
                endts = nowts + ts
                key = f'SMOKE_TS_{groupid}|{qq}'
                v = json.dumps({'nowts': nowts, 'endts': endts, 'ts': ts})
                logging.info('key:%s,v:%s,ts:%s', key, v, ts)
                rds.setex(key, v, int(ts))

        # elif int(groupid) == Config.GROUPID["JINJIEQUN"]:
        #     if 8.0 > stars > 6.5:
        #         if rank.lower() in ("b", "c", 'd', 'f'):
        #             ts = (stars - 6.5) * 10 * 6000
        #             flag = 1
        #     elif 20.0 > stars > 8.0:
        #         if rank.lower() in ("f", ):
        #             ts = (stars - 8) * 20 * 6000
        #             flag = 1
        if flag:
            if iswarn:
                return "".join(res_mark)
            else:
                pushTools.pushSmokeCmd(groupid, qq, ts)
                res = f'因触犯{"".join(res_mark)}入狱'
                return res
        return

    def groupPlayerCheck(self, groupid):
        """群检测机制
        """
        method = "get_group_member_list"
        kv = {'group_id': str(groupid)}
        callbackcmd = "!scancallback"
        callbackargs = str(groupid)
        pushTools.pushCallbackCmd(method, kv, callbackcmd, callbackargs)
        # return "发起检测..."
        return ""

    def groupPpCheck(self, groupid):
        """群pp分布检测
        """
        method = "get_group_member_list"
        kv = {'group_id': str(groupid)}
        callbackcmd = "!ppcheckcallback"
        callbackargs = str(groupid)
        pushTools.pushCallbackCmd(method, kv, callbackcmd, callbackargs)
        return ""

    def scanPlayers(self, groupid, users):
        """检测群列表
        """
        qqids = [u["user_id"] for u in users]
        a = len(qqids)
        # 取绑定数
        ret = self.getBindNum2(qqids)
        n, bindRet = self.countBindDiff(ret, qqids)
        p = round(n / a * 100, 2)
        # 取超限数
        ExLimits = self.getExceedsLimitPlayers(bindRet, int(groupid))
        n2 = len(ExLimits)

        msg = "本群人数[%s],绑定用户数[%s],占比[%s%%],超限人数[%s]" % (a, n, p, n2) 
        if n2:
            msg += '\n超限列表:\n'
            for r in ExLimits:
                msg += '%s(%spp)\n' % (r["username"], r["pp"])
            msg = msg[:-1]
        pushTools.pushMsgOne(groupid, msg)
        return "suc"

    def getExceedsLimitPlayers(self, bindRet, groupid):
        """检测超限
        """
        if groupid == Config.GROUPID["XINRENQUN"]:
            limit_pp = 3100
        elif groupid == Config.GROUPID["JINJIEQUN"]:
            limit_pp = 4500
        else:
            limit_pp = 0

        if not limit_pp:
            return 0
            
        db = interMysql.Connect('osu')
        sql = '''
            SELECT username, pp FROM user2 where username in %s and time>=%s and pp>%s
        '''
        username = [r["osuname"] for r in bindRet]
        ret = db.query(sql, [tuple(username), self.today_date(), limit_pp])
        return ret

    def scanPlayers2(self, groupid, users):
        """pp分布
        """
        qqids = [u["user_id"] for u in users]
        a = len(qqids)
        # 取绑定数
        ret = self.getBindNum2(qqids)
        n, bindRet = self.countBindDiff(ret, qqids)
        p = round(n / a * 100, 2)
        
        msg = "本群人数[%s],绑定用户数[%s],占比[%s%%]\n" % (a, n, p) 
        
        
        # 取分布，按群细分
        msg += "本群pp分布: \n"
        msg += self.ppStatics(bindRet, int(groupid))
        pushTools.pushMsgOne(groupid, msg)
        return "suc"

    def ppStatics(self, bindRet, groupid):
        """分层
        """
        # 初始化层级
        pp_static = [0,0,0,0,0,0]

        db = interMysql.Connect('osu')
        sql = '''
            SELECT username, pp FROM user2 where username in %s and time>=%s
        '''
        username = [r["osuname"] for r in bindRet]
        rs = db.query(sql, [tuple(username), self.today_date()])
        for r in rs:
            pp = float(r["pp"])
            if pp < 1000:
                pp_static[0] += 1
            elif pp < 2000:
                pp_static[1] += 1
            elif pp < 3100:
                pp_static[2] += 1
            elif pp < 4500:
                pp_static[3] += 1
            elif pp < 6000:
                pp_static[4] += 1
            else:
                pp_static[5] += 1

        cnt = len(rs)
        msg = ""
        msg += "0~1k:   %s人(%s%%)\n" % (pp_static[0], round(pp_static[0]/cnt*100))
        msg += "1~2k:   %s人(%s%%)\n" % (pp_static[1], round(pp_static[1]/cnt*100))
        msg += "2~3.1k:   %s人(%s%%)\n" % (pp_static[2], round(pp_static[2]/cnt*100))
        msg += "3.1k~4.5k:   %s人(%s%%)\n" % (pp_static[3], round(pp_static[3]/cnt*100))
        msg += "4.5k~6k:   %s人(%s%%)\n" % (pp_static[4], round(pp_static[4]/cnt*100))
        msg += ">6k:   %s人(%s%%)"   % (pp_static[5], round(pp_static[5]/cnt*100))
        return msg


    def getBindNum(self, qqids):
        """检查绑定数量-in版本
        """
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT count(distinct(qq)) n FROM user where qq in %s
        '''
        ret = db.query(sql, [tuple(qqids)])
        return ret[0]["n"]

    def getBindNum2(self, qqids):
        """检查绑定数量-暴力对比版本
        """
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT distinct(qq) qq, osuname FROM user
        '''
        ret = db.query(sql)
        return ret

    def countBindDiff(self, ret, qqids):
        bindusers = []
        for r in ret:
            if r["qq"]:
                bindusers.append(int(r["qq"]))
        n = set(qqids) - set(list(bindusers))
        n2 = set(qqids) & set(list(bindusers))
        diffRet = []
        for r in ret:
            if r["qq"] and int(r["qq"]) in n2:
                diffRet.append(r)
        diff = len(qqids) - len(n)
        return diff, diffRet

    def is_insert_today(self):
        """今天是否插入过
        """
        db = interMysql.Connect('osu')
        time = self.today_date()
        sql = '''
            SELECT count(1) cnt from user2 where time>=%s
        '''
        ret = db.query(sql, time)
        if ret[0]["cnt"]:
            return True
        else:
            return False

    def today_date(self):
        return datetime.date.today()

    def insert_forday(self, ousernames=[]):
        """插入任务
        """
        logging.info('开始执行插入任务')
        if not ousernames:
            ousernames = self.get_user_list_fromDB()
        ppyIns = ppyHandler.ppyHandler()
        for uid in ousernames:
            try:
                res = ppyIns.getOsuUserInfo(uid)
                get_num = 0
                while not res:
                    if get_num < 5:
                        get_num += 1
                        res = ppyIns.getOsuUserInfo(uid)
                    else:
                        break 
                if not res:
                    continue
                result = res
                if result:         
                    result = result[0]
                else:
                    continue
                username = result['username']
                osuid = result['user_id']
                pp = result['pp_raw']
                in_pp = float(pp)
                rank = result['pp_rank']
                acc1 = round(float(result['accuracy']),2)
                pc =  result['playcount']
                count300 = result['count300']
                count100 = result['count100']
                count50 = result['count50']
                tth = eval(count300)+eval(count50)+eval(count100)
                self.insert_user(username,in_pp,acc1,pc,rank,tth,osuid)
                logging.info('[%s]插入成功', uid)
                time.sleep(2)
            except:
                logging.exception('[%s]插入失败' % uid)

        logging.info('插入任务结束')

    def get_user_list_fromDB(self):
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT distinct(osuname) from user
        '''
        ret = db.query(sql)
        return [r["osuname"] for r in ret]

    def insert_user(self, *user):
        try:
            db = interMysql.Connect('osu')
            sql = 'insert into user2(username,pp,acc,pc,rank,tth,time,osuid) values(%s,%s,%s,%s,%s,%s,now(),%s)'
            ret = db.execute(sql,tuple(user))
            print('插入数据结果:'+str(ret))
            db.commit()
        except:
            db.rollback()
            logging.exception('插入失败')

    def osu_stats(self, osuname, days=0):
        try:
            ppyIns = ppyHandler.ppyHandler()
            result = ppyIns.getOsuUserInfo(osuname)
            if not result:
                return ''
            result = result[0]
            username = result['username']
            osuid = result['user_id']
            pp = result['pp_raw']
            in_pp = float(pp)
            rank = result['pp_rank']
            acc1 = round(float(result['accuracy']),2)
            acc = str(acc1)
            pc =  result['playcount']
            count300 = result['count300']
            count100 = result['count100']
            count50 = result['count50']
            tth = eval(count300)+eval(count50)+eval(count100)
            tth_w = str(tth//10000)
            #与本地数据比较
            u_db_info = self.get_user_fromDB(osuname, days)
            if u_db_info:
                info = u_db_info[0]
                add_pp = round(in_pp - float(info["pp"]),2)
                if add_pp >= 0:
                    add_pp = '+'+str(add_pp)
                else:
                    add_pp = str(add_pp)
                add_rank = info["rank"] - int(rank)
                if add_rank >= 0:
                    add_rank = '+'+str(add_rank)
                else:
                    add_rank = str(add_rank)
                add_acc =  round(acc1 - float(info["acc"]),2)
                if add_acc >=0.0:
                    add_acc = '+'+str(add_acc)
                else:
                    add_acc = str(add_acc)
                add_pc = str(int(pc) - int(info["pc"]))
                add_tth = str(tth - int(info["tth"]))
                times = info["time"].strftime('%Y-%m-%d')
                d = username+'\n'+pp+'pp('+add_pp+')\n'+'rank: '+rank+'('+add_rank+')\n'+'acc  : '+acc+'%('+add_acc+')\n'+'pc    : '+pc+'pc(+'+add_pc+')\n'+'tth   : '+tth_w+'w(+'+add_tth+')\n'+times
            else:
                d = username+'\n'+pp+'pp(+0)\n'+'rank: '+rank+'(+0)\n'+'acc : '+acc+'%(+0)\n'+'pc  : '+pc+'pc(+0)\n'+'tth  : '+tth_w+'w(+0)\n'+str(datetime.date.today())

            return d
        except:
            logging.exception("osu_stats error")

    def get_user_fromDB(self, username, days=0):
        db = interMysql.Connect('osu')
        if not days:
            time = self.today_date()
        else:
            time = self.get_daystime(days)
        sql = '''
            SELECT * from user2 where username=%s and time>=%s limit 1
        '''
        res = db.query(sql, (username, time))
        return res

    def get_daystime(self, days):
        now = datetime.datetime.now()
        date = now - datetime.timedelta(days = days)
        return date.strftime('%Y-%m-%d')

    def get_user_stats_today(self, uid):
        conn = interMysql.Connect('osu')
        sql = 'SELECT * FROM user2 where osuid = %s order by time desc limit 1'
        ret = conn.query(sql, uid)
        if not ret:
            return None
        return ret

    def get_usernames_by_uid(self, uids):
        conn = interMysql.Connect('osu2')
        sql = 'SELECT osuid,osuname FROM user where osuid in (%s)'
        sql = sql % (','.join(map(lambda x:'%s', uids)))
        ret = conn.query(sql, uids)
        if not ret:
            return None
        return ret

    def set_id_content_cmd(self, osuname, content):
        n = self.get_id_cmd_num(osuname)
        if n == None:
            n = ''
        else:
            n += 1
        cmd = '%s%s' % (osuname, n)
        self.set_id_cmd_to_db(cmd, content)
        return cmd

    def get_id_cmd_num(self, osuname):
        conn = interMysql.Connect('osu2')
        sql = '''SELECT cmd FROM cmdRef where cmd like %s order by id desc limit 1'''
        ret = conn.query(sql, (osuname+'%', ))
        logging.info('ret:%s', ret)
        if not ret:
            return None
        cmd = ret[0]['cmd']
        n = cmd[len(osuname):]
        if not n:
            return 0
        else:
            return int(n)

    def set_id_cmd_to_db(self, cmd, content):
        try:
            db = interMysql.Connect('osu2')
            sql = '''
                INSERT INTO cmdRef(cmd, reply) VALUES(%s, %s)
            '''
            db.execute(sql, [cmd, content])
            sql2 = '''
                INSERT INTO permission(ptype, gtype, cmd, groupid)
                VALUES(%s, %s, %s, %s)
            '''
            # 默认权限组2
            db.execute(sql2, [2,2,cmd,2])
            db.commit()
        except:
            db.rollback()
            logging.exception('cmd[%s]插入失败', cmd)

    def get_best_map_rec_from_db(self, bid, uid):
        db = interMysql.Connect('osu')
        sql = '''
            SELECT * from recinfo where uid=%s and bid=%s
        '''
        ret = db.query(sql, [bid, uid])
        if not ret:
            return None
        return ret[0]
    
    def random_maps(self, minstar, maxstar, limit):
        x = random.uniform(minstar, maxstar)
        maps = self.get_maps_by_stars(x, limit)
        if not maps:
            return "暂无推荐，请换个难度重试！"

        out = f"随机推图  本次推荐星级:{maps[0]['stars']:.1f}*\n"
        for i, r in enumerate(maps):
            out += f'[{i+1}] {r["artist"]} - {r["title"]} [{r["version"]}] '
            out += f'Beatmap by {r["creator"]}\n'
            out += f'https://osu.ppy.sh/b/{r["bid"]}\n'
        return out[:-1]
        


    def get_maps_by_stars(self, minstar, limit):
        db = interMysql.Connect('osu')
        sql = '''
            SELECT bid, source, artist, title, version, creator, stars
            FROM beatmap where stars >= %s limit %s
        '''
        ret = db.query(sql, [minstar, limit])
        return ret

    def avg_pp_count(self, osuid):
        apiUserInfo = self.getOsuInfoFromAPI(osuid)
        pp = float(apiUserInfo[0]['pp_raw'])
        username = apiUserInfo[0]['username']
        avg_pps = self.get_bpmsg_pp_avg(pp-20, pp+20)
        bpinfo = self.getRecBp(osuid, "5")
        s = f"{username}'s pp指数\n"
        s += f"统计分段 {pp-20:.0f}pp~{pp+20:.0f}pp\n"
        diff = 0
        for i, r in enumerate(bpinfo):
            avg_pp = float(avg_pps[i]["pp"])
            u_pp = float(r["pp"])
            s += f"{i+1}. {u_pp:.0f}pp -- {avg_pp:.0f}pp ({(u_pp-avg_pp):+.0f})\n"
            diff += u_pp-avg_pp
        if diff >= 0:
            s += f"高于均值,累积差: {diff:.1f}pp"
        else:
            s += f"低于均值,累积差: {diff:.1f}pp"
        return s

    def get_bpmsg_pp_avg(self, ppMin, ppMax):
        db = interMysql.Connect('osu')
        sql = '''
            SELECT bp_rank, avg(score_pp) pp
            FROM bpmsg
            where user_pp >= %s and user_pp<=%s 
            GROUP BY bp_rank
            ORDER BY bp_rank
        '''
        ret = db.query(sql, [ppMin, ppMax])
        return ret

    def drawRctpp(self, osuid="", osuname="", recinfo={}, userjson={}, mapjson={}, bestinfo={}):
        ppyIns = ppyHandler.ppyHandler()
        # 最近游戏记录
        if not recinfo:
            recinfos = ppyIns.getRecent(osuid, limit="1")
            if not recinfos:
                return "没有最近游戏记录,绑定用户为%s" % osuname
            recinfo = recinfos[0]
        bid = recinfo["beatmap_id"]
        
        # 用户信息
        if not userjson:
            userinfos = ppyIns.getOsuUserInfo(osuid)
            if not userinfos:
                return "找不到[%s]的用户信息" % osuname
            userjson = userinfos[0]

        # 铺面信息
        if not mapjson:
            mapinfos = ppyIns.getOsuBeatMapInfo(bid)
            if not mapinfos:
                return "找不到铺面信息"
            mapjson = mapinfos[0]

        # 最佳成绩
        if not bestinfo:
            bestinfos = ppyIns.getScores(osuid, bid, limit=1)
            if not bestinfos:
                bestinfo = recinfo
            else:
                bestinfo = bestinfos[0]

        return self.drawReplayRes(recinfo, bestinfo, mapjson, userjson)

    def drawReplayRes(self, recinfo, bestinfo, mapjson, userjson):
        # rec计算
        bid = recinfo["beatmap_id"]
        rinfo = self.exRecInfo(recinfo)
        # oppai算铺面信息
        extend = self.convert2oppaiArgs(**rinfo) 
        ojson = self.oppai2json(bid, extend)
        bpm = self.factBpm(float(mapjson['bpm']), ojson['mods_str'])

        # osu-tools计算
        newppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(**rinfo))
        pp = newppMap.get("pp")
        star = newppMap.get("difficulty_attributes", {}).get("star_rating")

        # fc计算
        fcacc = self.calFcacc(recinfo)
        fcppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods'], fcacc, 
                            int(newppMap['performance_attributes']['max_combo']), 0, rinfo['count100'], rinfo['count50']))
        fcpp = fcppMap.get("pp")
        fcCalAcc = fcppMap.get("score", {}).get("accuracy")

        # ac计算
        ssppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods']))
        sspp = ssppMap.get("pp")

        # 时长与物件数计算
        # to-do

        kwargs = {
            "pp": float(pp),
            "fcpp": float(fcpp),
            "acpp": float(sspp),
            "ar": round(ojson['ar'], 2),
            "cs": round(ojson['cs'], 2),
            "od": round(ojson['od'], 2),
            "hp": round(ojson['hp'], 2),
            "star": round(star, 2),
            "bpm": bpm
        }

        kv = {
            "stars": star, 
            "rank": recinfo["rank"],
            "ar": ojson['ar'],
            "acc": rinfo['acc']
        }

        pfs = drawReplay.drawRec(mapjson, recinfo, bestinfo, userjson, **kwargs)
        return pfs, kv



if __name__ == "__main__":
    b = botHandler()
    # b.drawRctpp(osuid="11788070", osuname="interbot")
