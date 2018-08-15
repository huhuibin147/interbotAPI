# -*- coding: utf-8 -*-
import logging
import traceback
import re
from ppyappLib import ppyAPI

class ppyHandler():


    def __init__(self):
        pass
    
    def getRecent(self, uid, mode=0, limit=10):
        kw = {
            'uid': uid,
            'mode': mode,
            'limit': limit
        }
        logging.info(kw)
        return ppyAPI.apiRoute('recent', **kw)
    
    def getOsuUserInfo(self, uid):
        kw = {'uid': uid}
        logging.info(kw)
        return ppyAPI.apiRoute('userinfo', **kw)
    
    def getOsuUserBp(self, uid, mode=0, limit=10):
        kw = {
            'uid': uid,
            'mode': mode,
            'limit': limit
        }
        logging.info(kw)
        return ppyAPI.apiRoute('bp', **kw)
    
    def getOsuBeatMapInfo(self, bid):
        kw = {'bid': bid}
        logging.info(kw)
        return ppyAPI.apiRoute('beatmap', **kw)

    def getSkillInfo(self, uid):
        """Skill抓取
        """
        try:
            kw = {'uid': uid}
            res = ppyAPI.crawlPageByGet('skill', kw)
            if not res:
                return '没有数据,太弱了!!'
            s_msg = uid+"'s skill\n"
            value = re.compile(r'<output class="skillValue">(.*?)</output>')
            values = value.findall(res.text)
            if not values:
                return '那个破网站连不上!!'
            skills = ['Stamina', 'Tenacity', 'Agility', 'Accuracy', 'Precision', 'Reaction', 'Memory', 'Reading']
            #skills_list = list(map(lambda x,y:x+y ,skills,values))
            for i,s in enumerate(skills):
                val = int(values[i])
                if  1000 > val >= 100:
                    snum = int(values[i][0:1])
                elif val >= 1000:
                    snum = int(values[i][0:2])
                else:
                    snum = 0
                star = '*' * snum
                skillkey = '%s:' % s
                valueskey = '%s ' % values[i]
                s_msg = s_msg+skillkey+valueskey+star+'\n'
            return s_msg[0:-1]
        except:
            logging.error(traceback.print_exc())
            return '那个破网站连不上!!'