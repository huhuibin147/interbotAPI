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
from chatbotLib import chatHandler
from draws import drawTools
from draws import draw_data






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
        # pp = newppMap.get("pp")
        pp = newppMap.get("performance_attributes", {}).get("pp")
        star = newppMap.get("difficulty_attributes", {}).get("star_rating")
        max_combo = newppMap.get("difficulty_attributes", {}).get("max_combo")

        # fc计算
        fcacc = self.calFcacc(recinfo)
        extendFc = self.convert2oppaiArgs(rinfo['mods'], fcacc)
        # ojsonFc = self.oppai2json(bid, extendFc)
        fcppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods'], fcacc, 
                            int(max_combo), 0, rinfo['count100'], rinfo['count50']))
        #fcpp = fcppMap.get("pp")
        fcpp = fcppMap.get("performance_attributes", {}).get("pp")
        fcCalAcc = fcppMap.get("score", {}).get("accuracy")

        # ac计算
        extendSs = self.convert2oppaiArgs(rinfo['mods'])
        # ojsonSs = self.oppai2json(bid, extendSs)
        ssppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods']))
        #sspp = ssppMap.get("pp")
        sspp = ssppMap.get("performance_attributes", {}).get("pp")
        
        res, kv = self.formatRctpp2New(ojson, recinfo['rank'], rinfo['acc'], 
            fcpp, sspp, bid, fcCalAcc, recinfo['countmiss'], pp, star, recinfo.get('date', '')) # , ojsonFc['pp'], ojsonSs['pp']

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

    def getRctppBatchResDraw2(self, osuname, recinfos):
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
        d = drawTools.DrawTool(width=600)
        d.autoDrawText(f"{osuname}")
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

            data = self.formatRctppDraw4(ojson, recinfo['rank'], rinfo['acc'], 
                ojsonFc['pp'], ojsonSs['pp'], bid, fcacc, recinfo['countmiss'], d)

            totalStars += data["stars"]
            totalMiss += int(data["miss"])
            totalpp += data["pp"]
            totalppfc += data["ppfc"]
            totalppss += data["ppss"] 
            totalacc += data["acc"]

        avgStars = round(totalStars/l, 2)
        avgAcc = round(totalacc/l, 2)
        avgPp = round(totalpp/l, 0)
        
        d.autoDrawText("---------------------------------")
        d.autoDrawText(f"{avgStars}* - {avgAcc:.1f}% - {avgPp:.0f}pp (ps:这个是老算法)")
        ret = d.startDraw()
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
        outp += Config.bg_thumb + '\n'
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
            "acc": acc,
            "bid": bid
        }
        return out, kv


    def formatRctpp2New(self, ojson, rank, acc, ppfc, ppss, bid, fcacc, miss, pp, stars, date, oldfcpp=0, oldsspp=0):
        """格式化rctpp输出"""
        outp = '{artist} - {title} [{version}] \n'
        outp += 'Beatmap by {creator} \n'
        outp += '[ar{ar} cs{cs} od{od} hp{hp}  bpm{bpm}]\n'
        outp += Config.bg_thumb + '\n'
        # outp += 'stars: {stars}*({oldstar}*) | {mods_str} \n'
        outp += 'stars: {stars}* | {mods_str} \n'
        outp += '{combo}x/{max_combo}x | {acc}% | {rank} \n\n'
        # outp += '{acc}%: {pp}pp({oldpp}pp)\n'
        # outp += '{fcacc}%: {ppfc}pp({oldfcpp}pp)\n'
        # outp += '100.0%: {ppss}pp({oldsspp}pp)\n'
        outp += '{acc}%: {pp}pp\n'
        outp += '{fcacc}%: {ppfc}pp\n'
        outp += '100.0%: {ppss}pp\n'
        outp += '{missStr}\n'
        # outp += 'https://osu.ppy.sh/b/{bid}'
        outp += '{date}  (bid:{bid})'

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
            # oldstar = round(ojson['stars'], 2),
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
            date = date[:10]
            # oldpp = round(ojson['pp']),
            # oldfcpp = round(oldfcpp),
            # oldsspp = round(oldsspp),
        )
        # 供外部smoke使用
        kv = {
            "stars": stars, 
            "rank": rank,
            "ar": ar,
            "acc": acc,
            "bid": bid
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
        outp += Config.bg_thumb + '\n'
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

    def formatRctppDraw4(self, ojson, rank, acc, ppfc, ppss, bid, fcacc, miss, d):
        """格式化rctpp简版输出"""
        mapInfo = self.getOsuBeatMapInfo(bid)
        bpm = self.factBpm(float(mapInfo['bpm']), ojson['mods_str'])

        m = {
            'ar': ojson['ar'],
            'cs': ojson['cs'],
            'od': ojson['od'],
            'hp': ojson['hp'],
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

        d.autoDrawImage(save_name=drawTools.MAP_COVER_FILE.format(sid=m["sid"]), 
                url=drawTools.MAP_COVER.format(sid=m["sid"]), autoResizeW=1)

        d.autoDrawText(f"{mapInfo['artist']} - {mapInfo['title']} [{mapInfo['version']}]")
        d.autoDrawText(f"[ar{ojson['ar']:.1f} cs{ojson['cs']} od{ojson['od']} hp{ojson['hp']}  bpm{bpm:.0f}]  {m['stars']}*")
        d.autoDrawText(f"{ojson['combo']}x/{ojson['max_combo']}({miss}x) | {acc:.1f}% | {rank}")
        d.autoDrawText(f"{m['pp']:.0f}pp | {ppfc:.0f}pp | {ppss:.0f}pp")

        return m


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

        randn = random.randint(0,100)
        if randn < 30:
            return '%smiss，%s' % (miss, ranReply)
        elif randn < 70:
            c = chatHandler.chatHandler()
            ranReply = c.get_random_speak()
            return '%smiss，%s' % (miss, ranReply)

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
            mapInfo = self.getOsuBeatMapInfo(r["beatmap_id"])
            msg = 'bp{x}, {pp}pp, {star:.2f}*, {acc:.2f}%,{rank},+{mod}'
            c50 = float(r['count50'])
            c100 = float(r['count100'])
            c300 = float(r['count300'])
            cmiss = float(r['countmiss'])
            acc = round((c50*50+c100*100+c300*300)/(c50+c100+c300+cmiss)/300*100, 2)
            msg = msg.format(
                x=i+offset,
                pp=round(float(r['pp'])),
                acc=acc,rank=r['rank'],
                mod=','.join(mods.getMod(int(r['enabled_mods']))),
                star = float(mapInfo["difficultyrating"])
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
            msg += '\nbp{x}, {pp}pp,{acc:.2f}%,{rank},+{mod}'
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

    def bbpOutFormatDraw2(self, bp5, ousname, offset=0):
        """bbp输出格式化
        """
        d = drawTools.DrawTool(width=600)
        d.autoDrawText("%s's bp!!" % ousname)
        for i,r in enumerate(bp5):
            mapInfo = self.getOsuBeatMapInfo(r["beatmap_id"])
            d.autoDrawImage(save_name=drawTools.MAP_COVER_FILE.format(sid=mapInfo["beatmapset_id"]), 
                    url=drawTools.MAP_COVER.format(sid=mapInfo["beatmapset_id"]), autoResizeW=1)
            d.autoDrawText(f'{mapInfo["artist"]} - {mapInfo["title"]} [{mapInfo["version"]}] ')
            bp_text = 'bp{x}, {pp}pp, {star:.2f}*, {acc:.2f}%,{rank},+{mod}   (bid:{bid})'
            c50 = float(r['count50'])
            c100 = float(r['count100'])
            c300 = float(r['count300'])
            cmiss = float(r['countmiss'])
            acc = round((c50*50+c100*100+c300*300)/(c50+c100+c300+cmiss)/300*100, 2)
            bp_text = bp_text.format(
                x=i+offset,
                pp=round(float(r['pp'])),
                acc=acc,rank=r['rank'],
                mod=','.join(mods.getMod(int(r['enabled_mods']))),
                star = float(mapInfo["difficultyrating"]),
                bid = r["beatmap_id"]
            )
            d.autoDrawText(bp_text)
        filename = d.startDraw()
        return filename

    def helpFormatOut(self):
        cmdInfo = self.cmdRefFromDb(level=[1])
        rs = 'interbot2 v1.0 (%s个功能)\n' % len(cmdInfo)
        for i, c in enumerate(cmdInfo):
            rs += '{}.[{}] {}\n'.format(
                    i+1, c["cmd"], c["reply"]
                )
        return rs[:-1]
    
    def out_html(self, data):
        r = f'<pre>{data}</pre>'
        return r

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

    def groupAdminMsgCheck(self, groupid, send_gid):
        """群管理发言统计
        """
        method = "get_group_member_list"
        kv = {'group_id': str(groupid)}
        callbackcmd = "!adminmsgrankcallback"
        callbackargs = str(send_gid)
        pushTools.pushCallbackCmd(method, kv, callbackcmd, callbackargs)
        return ""

    def groupMsgCheck(self, groupid, send_gid):
        """群发言统计
        """
        method = "get_group_member_list"
        kv = {'group_id': str(groupid)}
        callbackcmd = "!msgrankcallback"
        callbackargs = str(send_gid)
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

    def calAdminMsgRank(self, send_gid, users, days=7):
        """管理员发言排行统计
        """
        if len(users) == 0:
            return "users zero error"
            
        gid = users[0]['group_id']
        admins = {}
        for u in users:
            if u['user_id'] == Config.BOT_QQ:
                continue
            if u['role'] in ('admin', 'owner'):
                admins[str(u['user_id'])] = u
                if u['card'] == '':
                    u['card'] = u['nickname']
        rs = self.get_user_chatlog_cnt(admins.keys(), gid, days)
        for k, v in admins.items():
            v["n"] = rs.get(k, 0)
        sortrs = sorted(admins.items(), key=lambda x: x[1]['n'], reverse=True)
        ret = f"群({gid})管理近7天发言统计\n"
        for i, r in enumerate(sortrs):
            m = r[1]
            ret += f"{i+1}.{m['card']} ----- {m['n']}\n"
        ret = ret[:-1]
        logging.info(ret)
        
        img = drawTools.drawText(ret)
        if img:
            img = Config.ImgTmp % img
            pushTools.pushMsgOne(send_gid, img)
        else:
            pushTools.pushMsgOne(send_gid, "图片结果生成失败，请重试")
        
        return ret

    def calMsgRank(self, send_gid, days=7):
        rds = interRedis.connect('osu2')
        rs1 = rds.get(Config.GROUP_MEMBER_LIST.format(gid=Config.XINRENQUN))
        rs2 = rds.get(Config.GROUP_MEMBER_LIST.format(gid=Config.JINJIEQUN))
        if rs1 is not None and rs2 is not None:
            user1 = json.loads(rs1)
            user2 = json.loads(rs2)

            userlist = []
            for user in [user1, user2]:
                m = {}
                for u in user:
                    m[str(u['user_id'])] = u
                    if u['card'] == '':
                        u['card'] = u['nickname']
                userlist.append(m)

            data1 = self.get_group_chatlog_cnt(user1[0]['group_id'], days)
            data2 = self.get_group_chatlog_cnt(user2[0]['group_id'], days)
            
            s = ""
            for i, data in enumerate([data1, data2]):
                range_m = [
                    [10, 0],
                    [50, 0],
                    [100, 0],
                    [500, 0],
                    [1000, 0],
                    [10000, 0],
                    [999999, 0],
                ]
                s += f"新人群" if i == 0 else "进阶群"
                s += "近7天活跃度统计\n"
                tt = 0
                for r in data:
                    for rg in range_m:
                        if r['cnt'] < rg[0]:
                            rg[1] += 1
                            break
                    tt += r['cnt']
                s += f"总发言人数:{len(data)}, 总条数:{tt}, 平均:{tt//len(data)}条/人\n"

                s += "----活跃榜----\n"
                for idx,r in enumerate(data[:5]):
                    u = userlist[i].get(r['qq'], {})
                    s += f"{idx+1}.{u.get('card')} ----- {r['cnt']}\n"

                s += "----活跃区间----\n"
                last = 1
                for r in range_m:
                    if r[1] == 0:
                        last = r[0]
                        continue                    
                    s += f"{last}~{r[0]}条: {r[1]}人 {'*'*(r[1]//10+1)}\n"
                    last = r[0]

                if i == 0:
                    s += '\n'
            
                print(range_m)

            s = s[:-1]
            print(s)
            logging.info(s)

            img = drawTools.drawText(s)
            if img:
                img = Config.ImgTmp % img
                pushTools.pushMsgOne(send_gid, img)
            else:
                pushTools.pushMsgOne(send_gid, "图片结果生成失败，请重试")

            return True
        return False



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

    def osu_stats_info(self, osuname):
        try:
            ppyIns = ppyHandler.ppyHandler()
            result = ppyIns.getOsuUserInfo(osuname)
            if not result:
                return ''
            result = result[0]
            # result = {'user_id': '11788070', 'username': 'interbot', 'join_date': '2018-02-22 07:51:46', 
            # 'count300': '1620764', 'count100': '347130', 'count50': '45364', 'playcount': '5406', 
            # 'ranked_score': '2168793737', 'total_score': '4861318224', 'pp_rank': '161898', 
            # 'level': '89.9191', 'pp_raw': '3200.76', 'accuracy': '95.2582015991211', 'count_rank_ss': '0', 
            # 'count_rank_ssh': '0', 'count_rank_s': '49', 'count_rank_sh': '0', 'count_rank_a': '273', 'country': 'CN', 
            # 'total_seconds_played': '508223', 'pp_country_rank': '2705', 'events': []}
            username = result['username']
            osuid = result['user_id']
            pp = result['pp_raw']
            rank = int(result['pp_rank'])
            acc1 = round(float(result['accuracy']),2)
            acc = str(acc1)
            pc =  int(result['playcount'])
            count300 = result['count300']
            count100 = result['count100']
            count50 = result['count50']
            tth = eval(count300)+eval(count50)+eval(count100)
            country = result["country"]
            pp_country_rank = int(result["pp_country_rank"])
            join_date = result["join_date"]
            
            d = f"{username}\n"
            d += f"{pp}pp\n"
            d += f"{acc}%\n"
            d += f"{pc:,}pc\n"
            d += f"{tth:,}tth\n"
            d += f"#{rank:,}({country}#{pp_country_rank:,})\n"
            d += f"{join_date}"
            return d
        except:
            logging.exception("get osu info error")
            return "get osu info error"

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
        self.remove_cmd_cache()
        return cmd

    def del_id_content_cmd(self, cmd):
        self.del_id_cmd_to_db(cmd)
        self.remove_cmd_cache()
        return cmd

    def reset_id_content_cmd(self, cmd, content):
        n = self.get_id_cmd_num(cmd)
        if n == None:
            return ""
            
        if not self.reset_id_cmd_to_db(cmd, content):
            return "设置失败"
        self.remove_cmd_cache()
        return cmd

    def remove_cmd_cache(self):
        rds = interRedis.connect('osu2')
        rds.delete(Config.ALL_CMD_KEY)

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

    def del_id_cmd_to_db(self, cmd):
        try:
            db = interMysql.Connect('osu2')
            sql = '''
                DELETE FROM cmdRef where cmd=%s
            '''
            db.execute(sql, [cmd])
            sql2 = '''
                DELETE FROM permission where cmd=%s
            '''
            db.execute(sql2, [cmd])
            db.commit()
        except:
            db.rollback()
            logging.exception('cmd[%s]删除失败', cmd)

    def reset_id_cmd_to_db(self, cmd, content):
        try:
            db = interMysql.Connect('osu2')
            sql = '''
                update cmdRef set reply=%s where cmd=%s
            '''
            db.execute(sql, [content, cmd])
            db.commit()
            return True
        except:
            db.rollback()
            logging.exception('cmd[%s]修改失败', cmd)
            return False

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
            m = json.loads(r['mapjson'])
            sid = m["beatmapset_id"]
            out += f'[{i+1}] {r["artist"]} - {r["title"]} [{r["version"]}] '
            out += f'Beatmap by {r["creator"]}\n'
            out += f'{Config.bg_thumb.format(sid=sid)}\n'
            out += f'<a href="https://osu.ppy.sh/b/{r["bid"]}">https://osu.ppy.sh/b/{r["bid"]}</a>  '
            out += f'<a href="{Config.sayo_down_api.format(sid=sid)}">download</a>\n\n'
        return out[:-1]
    
    def random_maps_draw(self, minstar, maxstar, limit):
        x = random.uniform(minstar, maxstar)
        maps = self.get_maps_by_stars(x, limit)
        if not maps:
            return ""

        d = drawTools.DrawTool(width=600)
        d.autoDrawText(f"本次推荐星级:{maps[0]['stars']:.1f}*")
        for i, r in enumerate(maps):
            m = json.loads(r['mapjson'])
            d.autoDrawImage(save_name=drawTools.MAP_COVER_FILE.format(sid=m["beatmapset_id"]), 
                    url=drawTools.MAP_COVER.format(sid=m["beatmapset_id"]), autoResizeW=1)

            d.autoDrawText(f'[{i+1}] {r["artist"]} - {r["title"]} [{r["version"]}] ')
            d.autoDrawText(f'Beatmap by {r["creator"]}')
            d.autoDrawText(f'https://osu.ppy.sh/b/{r["bid"]}')
        return d.startDraw()


    def get_maps_by_stars(self, minstar, limit):
        db = interMysql.Connect('osu')
        sql = '''
            SELECT bid, source, artist, title, version, creator, stars, mapjson
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
        #pp = newppMap.get("pp")
        pp = newppMap.get("performance_attributes", {}).get("pp")
        star = newppMap.get("difficulty_attributes", {}).get("star_rating")
        max_combo = newppMap.get("difficulty_attributes", {}).get("max_combo")

        # fc计算
        fcacc = self.calFcacc(recinfo)
        fcppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods'], fcacc, 
                            int(max_combo), 0, rinfo['count100'], rinfo['count50']))
        #fcpp = fcppMap.get("pp")
        fcpp = fcppMap.get("performance_attributes", {}).get("pp")
        fcCalAcc = fcppMap.get("score", {}).get("accuracy")

        # ac计算
        ssppMap = self.ppy_tools_pp(bid, self.convert2oppaiArgsNew(rinfo['mods']))
        #sspp = ssppMap.get("pp")
        sspp = ssppMap.get("performance_attributes", {}).get("pp")

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
            "acc": rinfo['acc'],
            "bid": bid
        }

        pfs = drawReplay.drawRec(mapjson, recinfo, bestinfo, userjson, **kwargs)
        return pfs, kv

    def annual_sammry(self, osuid, osuname):
        
        db = interMysql.Connect('osu')
        sql = '''
            SELECT * FROM `recinfo` where lastdate >='2021-01-01' and lastdate <= '2022-01-01' and uid=%s
        '''
        ret = db.query(sql, [osuid])

        tt = len(ret)
        if tt < 1:
            return "无上传记录!"

        rankNum = {}
        score_tt = 0
        acc_tt = 0
        max_cb = 0
        one_miss_tt = 0
        miss_tt = 0
        cb_tt = 0
        modNum = {}
        dayNum = {}
        flag_t_0_6 = 0
        lastTime0_6 = datetime.datetime(year=2021, month=1, day=1, hour=0, minute=0, second=0)
        lastTime6_24 = datetime.datetime(year=2021, month=1, day=1, hour=0, minute=0, second=0)
        lastTime0_6_d = None
        lastTime6_24_d = None

        for r in ret:
            try:
                m = json.loads(r['recjson'])
                rankNum[m['rank']] = rankNum.get(m['rank'], 0) + 1
                score_tt += int(m['score'])
                m['acc'] = mods.get_acc(m['count300'], m['count100'], m['count50'], m['countmiss'])
                acc_tt += m['acc']
                if int(m['maxcombo']) > max_cb:
                    max_cb = int(m['maxcombo'])
                if m['countmiss'] == "1":
                    one_miss_tt += 1
                cb_tt += int(m['maxcombo'])
                miss_tt += int(m['countmiss'])
                mod = mods.getMod(m['enabled_mods'])
                for mo in mod:
                    modNum[mo] = modNum.get(mo, 0) + 1
                t = datetime.datetime.strptime(m['date'], "%Y-%m-%d %H:%M:%S")
                d = t.date()

                t2 = datetime.datetime(year=2021, month=1, day=1, hour=t.hour, minute=t.minute, second=t.second)
                
                dayNum[d] = dayNum.get(d, 0) + 1
                if t.hour <= 5:
                    if t2.timestamp() > lastTime0_6.timestamp():
                        lastTime0_6 = t2
                        lastTime0_6_d = t
                        flag_t_0_6 = 1
                else:
                    if t2.timestamp() > lastTime6_24.timestamp():
                        lastTime6_24 = t2
                        lastTime6_24_d = t
            except:
                logging.exception("")
            
        acc_avg = acc_tt / tt

        s = f"{osuname}的2021年度总结\n"
        s += f"上传总数：{tt}\n"
        s += f"总得分：{score_tt:,}\n"
        s += f"平均Acc：{acc_avg:.1f}%\n"
        s += f"最大Combo：{max_cb}\n"
        s += f"累计cb总数：{cb_tt:,}\n"
        s += f"累计Miss总数：{miss_tt:,}\n"
        s += f"1miss的图的总数：{one_miss_tt}\n"

        modNum_s = sorted(modNum.items(), key=lambda x:x[1], reverse=True)
        s += f"最爱的mod：{modNum_s[0][0]}({modNum_s[0][1]}次)\n"

        lastTime = lastTime0_6_d if flag_t_0_6 else lastTime6_24_d
        s += f"最晚的那天：{str(lastTime)}\n"

        dayNum_s = sorted(dayNum.items(), key=lambda x:x[1], reverse=True)
        s += f"查的最多的一天是：{dayNum_s[0][0]}({dayNum_s[0][1]}次)\n"

        s += f"总rank分布："
        for k in sorted(rankNum):
            s += f"{k}:{rankNum[k]}  "

        sql2 = '''
            SELECT * FROM `user2` where time>='2021-01-01' and osuid=%s order by time limit 1
        '''
        ret2 = db.query(sql2, [osuid])
        if ret2:
            u = ret2[0]
            ppyIns = ppyHandler.ppyHandler()
            userinfos = ppyIns.getOsuUserInfo(osuid)
            if userinfos:
                r = userinfos[0]
                incr_pp = float(r['pp_raw']) - float(u['pp'])
                incr_acc = float(r['accuracy']) - float(u['acc'])
                incr_rank = int(r['pp_rank']) - int(u['rank'])
                incr_pc = int(r['playcount']) - int(u['pc'])
                incr_tth = int(r['count300']) + int(r['count100']) + int(r['count50']) - int(u['tth'])
                s += f"\n今年你的pp增加了{incr_pp:.0f}pp({round(float(r['pp_raw'])):,}pp)\n" if incr_pp >= 0 else f"\n今年你的pp减少了{abs(incr_pp):.0f}pp({round(float(r['pp_raw'])):,}pp)\n"
                s += f"今年你的acc增加了{incr_acc:.2f}%({float(r['accuracy']):.2f}%)\n" if incr_acc >= 0 else f"今年你的acc减少了{abs(incr_acc):.2f}%({float(r['accuracy']):.2f}%)\n"
                s += f"今年你的排名上升了{abs(incr_rank):,}名({round(float(r['pp_rank'])):,})\n" if incr_rank < 0 else f"今年你的排名下降了{abs(incr_rank):,}名({round(float(r['pp_rank'])):,})\n"
                s += f"今年你总共打了{incr_pc:,}pc\n"
                s += f"今年你总共敲击了{incr_tth:,}下\n"
                s += f"计算的时间起点：{u['time']}"

        # print(s)
        return s
    
    def osu_mp(self, groupid=None):
        if self.check_mp_idle():
            mid = self.check_mp_mid()
            mpinfo = self.get_xrq_mp_base_info(mid)
            return mpinfo 
        
        if groupid:
            pushTools.pushMsgOne(groupid, "mp房间不存在，请稍等，正在创建...")

        npmrun_ret = self.make_mp_idle()
        logging.info("os system npm run res:%s", npmrun_ret)
        idle_flag = 0
        for i in range(20):
            time.sleep(5)
            logging.info("[%s].checking npm process...", i+1)
            if idle_flag == 0 and self.check_mp_idle(kill=0):
                idle_flag = 1

            if idle_flag == 1:
                mid = self.check_mp_mid()
                if groupid and mid:
                    pushTools.pushMsgOne(groupid, "mp房间创建完成，频道为#mp_%s" % mid)
                    return "房名: xinrenqun mp | auto host rotate \n密码: x114514"

        return "房间创建结果未知..."
    
    def make_mp_idle(self):
        return os.system('cd /root/code/osu-ahr; nohup npm run start m xinrenqunmp > ser.log 2>&1 &')
    
    def check_mp_idle(self, kill=1):
        ret = os.popen("ps axu|grep 'xinrenqunmp'|grep -v grep")
        ret = ret.read()
        logging.info(ret)
        if "xinrenqunmp" in ret:
            if kill == 1:
                mid = self.check_mp_mid()
                if not mid:
                    logging.info("check mp mid fail")
                    self.mp_idle_kill()
                    return False
                if not self.check_mp_network():
                    self.mp_idle_kill()
                    return False
                if not self.check_mp_terminated():
                    self.mp_idle_kill()
                    return False
                # if not self.check_mp_start_time(mid):
                #     self.mp_idle_kill()
                #     return False
                # if not self.check_mp_timeout():
                #     self.mp_idle_kill()
                #     return False
            return True
        return False
    
    def check_mp_alive(self, mid):
        ret = os.popen("ps axu|grep 'xinrenqunmp'|grep -v grep")
        ret = ret.read()
        logging.info(ret)
        if "xinrenqunmp" in ret:
            # mid = self.check_mp_mid()
            # if not mid:
            #     logging.info("check mp mid fail")
            #     return False
            if not self.check_mp_network():
                return False
            if not self.check_mp_terminated():
                return False
            # if not self.check_mp_start_time(mid):
            #     return False
            return True
        return False
    
    def check_mp_mid(self):
        ret = os.popen("cd /root/code/osu-ahr; grep '#mp' ser.log|tail -1")
        s = ret.read()
        mpid = None
        if "#mp" in s:
            p = re.compile("#mp_(\d+)")
            rs = p.findall(s)
            if len(rs) > 0:
                mpid = rs[0]
        return mpid

    def get_mp_link(self):
        mid = self.check_mp_mid()
        link = f"https://osu.ppy.sh/community/matches/{mid}"
        return link

    def mp_idle_kill(self):
        rs = os.system("ps axu|grep 'xinrenqunmp'|grep -v grep|awk '{print $2}'|xargs kill")
        logging.info("kill mp idle rs:%s", rs)
        return rs

    def check_mp_network(self):
        ret = os.popen("cd /root/code/osu-ahr; grep 'network reconnection detected' ser.log|tail -1")
        s = ret.read()
        if 'network reconnection detected' in s:
            logging.info('network reconnection detected!')
            return False
        return True

    def check_mp_terminated(self):
        ret = os.popen("cd /root/code/osu-ahr; grep 'terminated lobby' ser.log|tail -1")
        s = ret.read()
        if 'terminated lobby' in s:
            logging.info('terminated lobby!')
            return False
        return True

    def check_mp_start_time(self, mid):
        st = self.get_mp_start_time_with_cache(mid)
        if st:
            diff = datetime.datetime.now() - self.timestr_add8_dt(st)
            if diff.days > 1:
                logging.info(f"mp start_time:{st} over 1 day, diff:{diff}")
                return False
        return True

    def get_mp_start_time_with_cache(self, mid):
        rds = interRedis.connect('osu2')
        rs = rds.get(Config.MP_START_TIME.format(mid=mid))
        if rs:
            return rs
        obj = ppyHandler.ppyHandler()
        res = obj.getOsuMpInfo(mid)
        minfo = res.get('match', {})
        st = ""
        if minfo:
            st = minfo['start_time']
            rds.set(Config.MP_START_TIME.format(mid=mid), st, 86400)
        return st

    def check_mp_timeout(self):
        ret = os.popen('cd /root/code/osu-ahr; grep "check timeout" ser.log |wc -l')
        s = ret.read()
        if int(s) > 10:
            logging.info('check timeout:%s', s)
            return False
        return True

    def get_admins(self, gid="595985887", days=7):
        with open(Config.USERLIST_FILE, 'r', encoding='utf-8') as f:
            confs = json.load(f)
        users = confs[gid]["admin_users"]
        rs = self.get_user_chatlog_cnt(users.keys(), gid, days)
        for k, v in users.items():
            v["n"] = rs.get(k, 0)
        sortrs = sorted(users.items(), key=lambda x: x[1]['n'], reverse=True)
        ret = "新人群管理近7天发言统计\n"
        for i, r in enumerate(sortrs):
            m = r[1]
            ret += f"{i+1}.{m['nickname']:<14}   {m['n']}\n"
        return ret[:-1]

    def get_match_bids(self, bid_idx, hid):
        with open(Config.MATCHLIST_FILE, 'r', encoding='utf-8') as f:
            confs = json.load(f)
        return confs.get(hid, {}).get(bid_idx)
    
    def get_user_chatlog_cnt(self, qq, gid, days=7):
        db = interMysql.Connect('osu')
        sql = f'''
            SELECT qq, count(*) cnt FROM `chat_logs` where 
            qq in %s
            and group_number=%s and
            create_time>=DATE_ADD(CURDATE(),interval -{days} DAY)
            GROUP BY qq
        '''
        ret = db.query(sql, [tuple(qq), gid])
        rs = {r['qq']:r['cnt'] for r in ret}
        return rs
    
    def get_group_chatlog_cnt(self, gid, days=7):
        db = interMysql.Connect('osu')
        sql = f'''
            SELECT qq, count(*) cnt FROM `chat_logs` where 
            group_number=%s and
            create_time>=DATE_ADD(CURDATE(),interval -{days} DAY)
            GROUP BY qq order by cnt desc
        '''
        ret = db.query(sql, [gid])
        return ret

    def match_rank(self, hid, gid):
        db = interMysql.Connect('osu')
        sql = 'SELECT bid, rankjson from maprank a where gid = %s and hid = %s'
        ret = db.query(sql, [gid, hid])
        u_cnt = {}
        for r in ret:
            rk = json.loads(r['rankjson'])
            for i, s in enumerate(rk):
                uid, v = list(s.items())[0]
                if uid not in u_cnt:
                    u_cnt[uid] = []
                u_cnt[uid].append(i+1)
        # print(u_cnt)
        u_rank = {}
        for k,v in u_cnt.items():
            u_rank[k] = sum(v)/len(v)
        # print(u_rank)
        rank_s = sorted(u_rank.items(), key=lambda x:x[1])
        # print(rank_s)
        
        db2 = interMysql.Connect('osu2')
        sql2 = 'SELECT DISTINCT(osuid), osuname FROM user where osuid in %s'
        ret2 = db2.query(sql2, [tuple(u_rank.keys())])
        # print(ret2)
        u_d = {}
        for r in ret2:
            u_d[r['osuid']] = r['osuname']

        rs = f"新人群S{hid}群赛 平均排名                   \n"
        for i, r in enumerate(rank_s):
            uid = r[0]
            n = round(r[1], 1)
            osuname = u_d.get(uid, uid)
            rs += f"{i+1}.{osuname}: {n}\n"
        # print(rs)
        return rs[:-1]

    def check2(self, osuid):
        rs = self.getOsuInfoFromAPI(osuid)
        if not rs:
            return "用户信息不存在"
        userinfo = rs[0]

        bp = self.getRecBp(osuid, limit=10)
        if not bp:
            return "用户bp信息不存在"

        acc = float(userinfo['accuracy'])
        pc = float(userinfo['playcount'])
        tth = float(int(userinfo['count300']) + int(userinfo['count100']) + int(userinfo['count50']))
        bpacc = bppp = 0
        for r in bp:
            bppp += float(r['pp'])
            bpacc += float(mods.get_acc(r['count300'], r['count100'], r['count50'], r['countmiss']))
        newpp_w, acc_w, bpacc_w, bppp_w, pc_w, tth_w, newpp, acc_c, bpacc_c, bppp_c, pc_c, tth_c = self.pp2(acc, bpacc, bppp, pc, tth)
        print(acc, bpacc, bppp, pc, tth)
        print(acc_w, bpacc_w, bppp_w, pc_w, tth_w)
        print(acc_c, bpacc_c, bppp_c, pc_c, tth_c)
        ret = "%s\n实际pp:%spp\n预测水平:%spp\n" % (osuid, round(float(userinfo['pp_raw']),0), newpp)
        ret += f"acc:{acc:.1f}   指标值:{acc_c:.0f} (权重:{acc_w:.3f})\n"
        ret += f"pc:{pc:,.0f}   指标值:{pc_c:.0f} (权重:{pc_w:.3f})\n"
        ret += f"tth:{tth:,.0f}   指标值:{tth_c:.0f} (权重:{tth_w:.3f})\n"
        ret += f"bp10(acc):{bpacc/10:.1f}   指标值:{bpacc_c:.0f} (权重:{bpacc_w:.3f})\n"
        ret += f"bp10(pp):{bppp/10:.1f}   指标值:{bppp_c:.0f} (权重:{bppp_w:.3f})"
        return ret
    
    def pp2(self, acc, bpacc, bppp, pc, tth):
        w = [0.22483119, -0.1217108, 0.82082623, 0.0294727, 0.06772371]
        b = [4.95929298e-09]
        pp_m = 2218.589021413463
        pp_s = 1567.8553119973133
        acc_m = 95.69755708902649
        acc_s = 3.014845506352131
        bpacc_m = 961.4064515140441
        bpacc_s = 38.812586876313496
        bppp_m = 1177.9167271984384
        bppp_s = 808.798796955419
        pc_m = 15030.912107867616
        pc_s = 17940.253798480247
        tth_m = 2756676.6760339583
        tth_s = 3498224.778143693
        acc_c = (acc-acc_m)/acc_s*(w[0])
        bpacc_c = (bpacc-bpacc_m)/(bpacc_s)*(w[1])
        bppp_c = (bppp-bppp_m)/bppp_s*(w[2])
        pc_c = (pc-pc_m)/pc_s*(w[3])
        tth_c = (tth-tth_m)/tth_s*(w[4]) + (b[0])
        pp = acc_c + bpacc_c + bppp_c + pc_c + tth_c
        res = [pp, acc_c, bpacc_c, bppp_c, pc_c, tth_c]
        res2 = [round(r*pp_s+pp_m,1) for r in res]
        return res + res2

    def save_last_query_bid_cache(self, bid, gid):
        rds = interRedis.connect('osu2')
        rds.set(Config.LAST_BID % gid, bid, 86400*30)
        logging.info("set last bid cache: %s > %s", gid, bid)
        return

    def get_last_query_bid_cache(self, gid):
        rds = interRedis.connect('osu2')
        return rds.get(Config.LAST_BID % gid)

    def get_xrq_mp_base_info(self, matchid):
        # obj = ppyHandler.ppyHandler()
        # res = obj.getOsuMpInfo(matchid)
        # minfo = res.get('match', {})
        # if not minfo:
        #     return f"#mp_{matchid}不存在"
        
        alive = self.check_mp_alive(matchid)
        # st = self.timestr_add8_dtstr(minfo['start_time'])
        # ed = self.timestr_add8_dtstr(minfo['end_time']) if minfo['end_time'] else ""
        users, map_name, diffc, st, ed, games = self.get_mp_info_from_osuahr_log()
        # n = len(res['games'])
        n = games
        # last_game_users = 0
        # if n > 0:
        #     last_game_users = len(res['games'][-1]['scores'])
        s = f"房名: xinrenqun mp | auto host rotate (x114514)\n"
        s += f"总局数: {n}\n"
        s += f"当前人数: {len(users)}\n"
        s += f"当前曲子: {map_name}\n"
        s += f"当前难度: {diffc}\n"
        s += f"当前玩家: "
        for i, u in enumerate(users):
            s += f"{u} "
            if (i+1)%3==0:
                s += '\n'
        if not s.endswith('\n'):
            s += '\n'
        s += f"开始时间: {st}\n"
        if ed:
            s += f"结束时间: {ed}\n"
        if not alive:
            s += f"状态: 已关闭\n"
        else:
            s += f"状态: 存活\n"
        s += f"https://osu.ppy.sh/community/matches/{matchid}"
        return s

    def timestr_add8_dt(self, timestr):
        t = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        t += datetime.timedelta(hours=8)
        return t

    def timestr_add8_dtstr(self, timestr):
        t = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        t += datetime.timedelta(hours=8)
        return t.strftime("%Y-%m-%d %H:%M:%S")
        
    def get_mp_info_from_osuahr_log(self):
        try:
            ret = os.popen("cd /root/code/osu-ahr; grep 'host order' ser.log|tail -1")
            s = ret.read()
            s = s.replace("\u200b", "")
            users = s.replace("\n","").split(":")[-1].split(", ")
            if users[0] == '':
                users = users[1:]
            else:
                users[0] = users[0][1:]

            users = set(users)
            ret = os.popen("cd /root/code/osu-ahr; grep 'mp host' ser.log|tail -1")
            s = ret.read()
            host_user = s.replace("\n","").split("mp host ")[-1]
            if len(host_user)>0 and not host_user.startswith("#"):
                users.add(host_user)
            st_str = s.split("][INFO")[0].split("[")[-1]
            print(st_str)
            ret = os.popen(f"cd /root/code/osu-ahr; sed -n '/{st_str}/,//p' ser.log|grep inout")
            s = ret.read()
            for r in s.split("\n"):
                if len(r) == 0:
                    continue
                rs = r.split("inout")[1].split(" ")
                u = rs[3].split('(')[0]
                if rs[2][0] == '-':
                    if u in users:
                        users.remove(u)
                else:
                    users.add(u)
            logging.info(users)

            ret = os.popen("cd /root/code/osu-ahr; grep 'beatmap changed' ser.log|tail -1")
            s = ret.read()
            map_name = s.replace("\n","").split("b/")[-1]
            logging.info(map_name)

            ret = os.popen("cd /root/code/osu-ahr; grep '!mp map' ser.log|tail -1")
            s = ret.read()
            s = s.replace("\n","")
            logging.info(s)

            p = re.compile('star=.*?-')
            res = p.findall(s)
            star = res[0] if res else ""
            star = star.replace(" -", "")

            ret = os.popen("cd /root/code/osu-ahr; grep 'Making lobby' ser.log|head -1")
            s = ret.read()
            st = s.split("][INFO")[0].split("[")[-1][:5]

            ret = os.popen("cd /root/code/osu-ahr; grep 'terminated lobby' ser.log|head -1")
            s = ret.read()
            ed = s.split("][INFO")[0].split("[")[-1][:5]

            ret = os.popen("cd /root/code/osu-ahr; grep 'match started' ser.log|wc -l")
            s = ret.read()
            games = s.replace('\n','').replace(' ','')

            return users, map_name, star, st, ed, games
        except:
            logging.exception("")
            return "", "", "", "", "", ""



if __name__ == "__main__":
    b = botHandler()
    # b.drawRctpp(osuid="11788070", osuname="interbot")
    # b.annual_sammry(osuid = "11788070", osuname="interbot")
    # b.osu_mp("595985887")
    # print(b.check_mp_mid())
    # b.get_admins()
    # b.match_rank("", 25, 25)
    # print(b.check2("sakamata1"))
    # print(b.osu_stats_info("interbot"))
    # print(b.calMsgRank(""))
    # print(b.check_mp_start_time("105465538"))
    # print(b.check_mp_alive())
    print(b.get_xrq_mp_base_info("105533347"))
    # print(b.get_mp_info_from_osuahr_log())
