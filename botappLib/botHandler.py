# -*- coding: utf-8 -*-
import os
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

    def oppai2dict(self, oppairet):
        """oppai text处理"""
        r1 = oppairet.split('\n')
        t = r1[11:]
        logging.info(oppairet)
        newdict = {
            "title": t[0][:t[0].find('+')] if t[0].find('+') else t[0], # 去除尾部mod
            "mod": t[0][t[0].find('+')+1:] if t[0].find('+') > 0 else 'none',
            "odarcshp": t[1],
            "combo": t[2],
            "circles": t[3],
            "miss": t[4],
            "acc": t[5],
            "scovev": t[6],
            "stars": t[8],
            "aimstar": t[9].split(',')[0],
            "speedstar": t[9].split(',')[1][1:],
            "aim": t[11],
            "speed": t[12],
            "accuracy": t[13],
            "pp": t[18]
        }
        return newdict

    def oppai2pp(self, oppairet):
        """oppai pp提取"""
        r1 = oppairet.split('\n')
        t = r1[11:]
        return t[18]


    def formatRctpp(self, oppairet, rank):
        """格式化rctpp输出"""
        oppdict = self.oppai2dict(oppairet)
        ret = "{title}\n[{odarcshp}]\n\nstars:{stars} | {aimstar} | {speedstar}\n{aim} | {speed} | {accuracy}\n\n{combo} | {acc} | {mod} | {rank}\n{scovev}: {pp}".format(
                title=oppdict['title'].replace('(', '\nBeatmap by ').replace(')', ''),
                odarcshp=oppdict['odarcshp'],
                combo=oppdict['combo'].replace(' combo', 'x'),
                acc=oppdict['acc'],
                mod=oppdict['mod'],
                stars=oppdict['stars'].replace(' stars', '*'),
                scovev=oppdict['scovev'].replace('score', ''),
                pp=oppdict['pp'],
                aimstar=oppdict['aimstar'].replace(' stars', '')+'*',
                speedstar=oppdict['speedstar'].replace(' stars', '')+'*',
                aim=oppdict['aim'],
                accuracy=oppdict['accuracy'],
                speed=oppdict['speed'],
                rank=rank
            )
        return ret


