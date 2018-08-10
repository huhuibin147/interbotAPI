# -*- coding: utf-8 -*-
import os
import re
import json
import random
import logging
import traceback
from io import TextIOWrapper
from commLib import cmdRouter
from commLib import mods

class botHandler():


    def __init__(self):
        self.osufiledir = '/data/osufile/'
    
    def getOsuInfo(self, args):
        """取osu用户绑定信息
        Args:
            qq/groupid
        """
        ret = cmdRouter.invoke('!uinfo', args)
        return json.loads(ret)

    def getRecInfo(self, args):
        """取osu用户rec信息
        Args:
            osuid
        """
        ret = cmdRouter.invoke('!rec', args)
        return json.loads(ret)

    def getRecBp(self, args):
        """取osu用户bp信息
        Args:
            osuid
        """
        ret = cmdRouter.invoke('!bp', args)
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

    def formatRctpp2(self, ojson, rank, acc, ppfc, ppss, bid, fcacc, miss):
        """格式化rctpp输出"""
        outp = '{artist} - {title} [{version}] \n'
        outp += 'Beatmap by {creator} \n'
        outp += '[ar{ar} cs{cs} od{od} hp{hp}]\n\n'
        outp += 'stars: {stars}* | {mods_str} \n'
        outp += '{combo}x/{max_combo}x | {acc}% | {rank} \n\n'
        outp += '{acc}%: {pp}pp\n'
        outp += '{fcacc}%: {ppfc}pp\n'
        outp += '100.0%: {ppss}pp\n'
        outp += '{missStr}\n'
        outp += 'https://osu.ppy.sh/b/{bid}'

        missStr = self.missReply(miss, acc, ojson['ar'], 
            ojson['combo'], ojson['max_combo'], ojson['stars'])

        out = outp.format(
            artist = ojson['artist'],
            title = ojson['title'],
            version = ojson['version'],
            creator = ojson['creator'],
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
            missStr = missStr
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
                    l = ['1miss，治治你的手抖吧',
                        '再肛一肛，pp就到手了',
                        '专业破梗大法上下颠倒hr']
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
                        r = '%smiss，不知道说啥，卖个广告吧' % miss


        if random.randint(0,100) < 20:
            r = '%smiss，广告位出租' % miss
        return r