# -*- coding: utf-8 -*-
import logging
import traceback
import random
from botappLib import botHandler
from commLib import interMysql

class extendHandler():


    def __init__(self):
        pass
    
    def checkUser(self, osuid, osuname):
        """预测
        """
        try:
            botObj = botHandler.botHandler()
            apiUserInfo = botObj.getOsuInfoFromAPI(osuid)
            if not apiUserInfo:
                return 0, 0, 0
            pp = apiUserInfo[0]['pp_raw']
            bpinfo = botObj.getRecBp(osuid, limit=10)
            count_num = 0
            count_pp = 0
            maxpp = 0
            conn = interMysql.Connect('osu')
            for r in bpinfo:
                maxcombo1 = int(r['maxcombo']) - 10
                maxcombo2 = int(r['maxcombo']) + 10
                c50 = float(r['count50'])
                c100 = float(r['count100'])
                c300 = float(r['count300'])
                cmiss = float(r['countmiss'])
                acc = round((c50*50+c100*100+c300*300)/(c50+c100+c300+cmiss)/300*100,2)
                acc1 = acc - 0.2
                acc2 = acc + 0.2
                args = [r['beatmap_id'], r['enabled_mods'], acc1, acc2, maxcombo1, maxcombo2]
                sql='''
                    SELECT avg(u.pp_raw) a, count(1) b 
                    FROM osu_bp b INNER JOIN osu_user u on b.user_id=u.user_id 
                    WHERE b.beatmap_id = %s and b.mods=%s and b.acc BETWEEN %s and %s and b.maxcombo BETWEEN %s and %s 
                '''
                res = conn.query(sql, args)
                
                res = res[0]
                if res['a'] is None:
                    continue
                if res['a'] > maxpp:
                    maxpp = res['a']
                if res['b'] != 1: 
                    count_num += 1
                    count_pp += res['a']
            if count_num == 0:
                yugu_pp = pp
            else:
                yugu_pp = round(count_pp/count_num)
            if maxpp == 0:
                maxpp = float(pp)
            return pp,yugu_pp,round(maxpp)
        except:
            logging.error(traceback.format_exc())
            return 0, 0, 0

    def checkFormat(self, osuid, osuname):
        """输出
        """
        pp, pp2, maxpp = self.checkUser(osuid, osuname)
        if not pp:
            return '你在逗我把,哪来的pp???'
        return '%s\npp:%spp\n薛定谔的屁屁:%spp\n薛定谔的潜力:%spp' % (osuname, pp, pp2, maxpp)

    def choiceMap(self, osuid):
        '''低端推荐pp图'''
        try:
            conn = interMysql.Connect('osu')
            botObj = botHandler.botHandler()
            apiUserInfo = botObj.getOsuInfoFromAPI(osuid)
            pp = apiUserInfo[0]['pp_raw']
            if not pp:
                return 0,0
            pp = float(pp)
            sql = '''
                SELECT beatmap_id,count(beatmap_id) num FROM osu_user ta INNER JOIN osu_bp tb on ta.user_id = tb.user_id where ta.pp_raw BETWEEN %s and %s GROUP BY beatmap_id ORDER BY num desc limit 0,20; 
            '''
            res = conn.query(sql, [pp, pp+20])
            if not res:
                return 0,0
            ret = random.choice(res)
            return ret['beatmap_id'],ret['num']
        except:
            logging.error(traceback.format_exc())
            return 0,0
