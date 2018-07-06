# -*- coding: utf-8 -*-
import os
import re
import json
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

    def formatRctpp2(self, ojson, rank, acc, ppfc, ppss, bid):
        """格式化rctpp输出"""
        outp = '{artist} - {title} [{version}] \n'
        outp += 'Beatmap by {creator} \n'
        outp += '[ar{ar} cs{cs} od{od} hp{hp}]\n\n'
        outp += 'stars: {stars}* | {mods_str} \n'
        outp += 'aim: 0.47 | speed: 0.43 | accuracy: 0\n\n'
        outp += '{combo}x/{max_combo}x | {acc}% | {rank} \n'
        outp += 'pp: {pp}pp | fc: {ppfc}pp | ss: {ppss}pp\n'
        outp += 'https://osu.ppy.sh/b/{bid}'

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
            bid = bid
        )

        return out

