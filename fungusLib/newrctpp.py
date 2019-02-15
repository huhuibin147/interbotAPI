import os
import re
import time
import json
import random
import logging
import traceback
import subprocess
from io import TextIOWrapper
from commLib import mods


class newrctpp():

    def rctppjson(self, bid, extend='', recusion=0):
        try:
            bid = '/data/osufile/%s.osu' % (bid)
            """
            bid="\"F:/osu!/Songs/411894 Remo Prototype[CV- Hanamori Yumiri] - Sendan Life/Remo Prototype[CV Hanamori Yumiri] - Sendan Life (Narcissu) [Crystal's Garakowa].osu\""
            """
            cmd=(
                'dotnet ./fungusLib/netcoreapp2.0/PerformanceCalculator.dll simulate osu %s %s' % (bid, extend))
            print(cmd)
            ret=os.popen(cmd)
            retStr=ret.read()
            print(retStr)
            retStr=retStr[retStr.find('Accuracy'):]
            ret.close()
            return self.convertJSON(retStr)
        except:
            if recusion == 0:
                return self.rctppjson(bid, extend, recusion = 1)
            logging.error(traceback.format_exc())
            return {}

    def convertArgs(self, mods = '', acc = '', cb = '', miss = ''):
        args=''
        modlist=mods.split("-")
        modlist.remove("")
        for mod in modlist:
            args += '-m %s ' % mod
        if acc:
            args += '-a %s ' % acc
        if cb:
            args += '-c %s ' % cb
        if miss:
            args += '-X %s ' % miss
        return args

    def convertJSON(self, str):
        str=str.replace(' ', '')
        strlist=re.split('[:\n]', str)
        ret={}
        for i in range(0, 14):
            key=strlist[i*2]
            value=strlist[i*2+1]
            ret.update({'%s' % (key): value})
        return ret

    def test(self):
        rinfo={
            "mods": '-HD-HR',
            "acc": 100,
            "cb": 479,
            "miss": 0
        }
        extend = self.convertArgs(**rinfo)
        ojson = self.rctppjson("941270", extend)
        print(ojson)
