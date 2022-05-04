# -*- coding: utf-8 -*-
import logging
import traceback
import random
import re
import json
import requests
from html.parser import HTMLParser
from commLib import mods
from datetime import datetime, timedelta
from ppyappLib import ppyAPI
from baseappLib import baseHandler
from botappLib import botHandler
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from bs4 import BeautifulSoup
from draws import score


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
    
    def getScores(self, uid, bid, limit=10):
        kw = {
            'uid': uid,
            'bid': bid,
            'limit': limit
        }
        logging.info(kw)
        return ppyAPI.apiRoute('get_scores', **kw)
    
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

    def getSkillInfo(self, osuname):
        """Skill抓取
        """
        try:
            kw = {'osuname': osuname}
            res = ppyAPI.crawlPageByGet('skill', **kw)
            if not res:
                return '网络异常!!'
            s_msg = osuname+"'s skill\n"
            value = re.compile(r'<output class="skillValue">(.*?)</output>')
            values = value.findall(res)
            if not values:
                return '抓取不到相关信息!!'
            skills = ['Stamina', 'Tenacity', 'Agility', 'Accuracy', 'Precision', 'Reaction']
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
            logging.error(traceback.format_exc())
            return '那个破网站连不上!!'

    def skillVsInfo(self, uid, uid2):
        try:
            kw = {'osuname': uid, 'vsosuname': uid2}
            res = ppyAPI.crawlPageByGet('skillvs', **kw)
            if not res:
                return '网络异常!!'
            value = re.compile(r'<output class="skillValue">(.*?)</output>')
            values = value.findall(res)
            if not values:
                return '那个破网站连不上,你们还是去床上解决吧!!'
            skills = ['Stamina', 'Tenacity', 'Agility', 'Accuracy', 'Precision', 'Reaction']
            s_msg = '%s vs %s\n'%(uid, uid2)
            for i,s in enumerate(skills):
                v1 = int(values[i])
                v2 = int(values[i+8])
                vv = str(abs(v1-v2))
                fuhao = ' -- '
                if v1 > v2:
                    s_msg = s_msg + s + ' : ' + values[i]+'(+'+vv+')' + fuhao + values[i+8] +'\n'
                elif v1 < v2:
                    s_msg = s_msg + s + ' : ' + values[i] + fuhao + values[i+8] +'(+'+vv+')'+'\n'
                else:
                    s_msg = s_msg + s + ' : ' + values[i] + fuhao + values[i+8] +'\n'
            return s_msg[0:-1]
        except:
            logging.error(traceback.format_exc())
            return '那个破网站连不上,你们还是去床上解决吧!!'

    def getFriends(self, qq, groupid):
        uinfo = baseHandler.baseHandler().getUserBindInfo({"qq": qq})
        token = uinfo[0]["acesstoken"]
        refreshtoken = uinfo[0]["refreshtoken"]
        osuname = uinfo[0]["osuname"]
        res = self.autov2Req(qq, groupid, "friends", token, refreshtoken)
        if isinstance(res, str):
            return res
        else:
            friendsNum = len(res)
            rs = "%s's friends(%s)\n" % (osuname, friendsNum)
            if friendsNum < 10:
                fs = res
            else:
                fs = random.sample(res, 10)
            for i, r in enumerate(fs):
                rs += '%s.%s\n' % (i+1, r["username"])
        return rs[:-1]

    def getV2MyInfo(self, qq, groupid):
        uinfo = baseHandler.baseHandler().getUserBindInfo({"qq": qq})
        token = uinfo[0]["acesstoken"]
        refreshtoken = uinfo[0]["refreshtoken"]
        osuname = uinfo[0]["osuname"]
        res = self.autov2Req(qq, groupid, "me", token, refreshtoken)
        if isinstance(res, str):
            return res
        else:
            return json.dumps(res)

    def getV2osuInfo(self, qq, groupid):
        uinfo = baseHandler.baseHandler().getUserBindInfo({"qq": qq})
        if len(uinfo) < 1:
            return -3, "请使用oauth进行认证绑定!"
        token = uinfo[0]["acesstoken"]
        refreshtoken = uinfo[0]["refreshtoken"]
        osuname = uinfo[0]["osuname"]
        return self.autov2Req2(qq, groupid, "me", token, refreshtoken)

    def autov2Req2(self, qq, groupid, endponit, token, refreshtoken):
        if not token:
            return -3, '请使用oauth进行认证绑定!'
        res = ppyAPI.apiv2Req(endponit, token, refreshtoken, qq=qq, groupid=groupid)
        if res in (-1, -2):
            return -1, 'token失效!请使用oauth进行认证绑定!'
        else:
            return 1, res

    def autov2Req(self, qq, groupid, endponit, token, refreshtoken):
        if not token:
            return '请使用oauth进行认证绑定!'
        res = ppyAPI.apiv2Req(endponit, token, refreshtoken, qq=qq, groupid=groupid)
        if res in (-1, -2):
            return 'token失效!请使用oauth进行认证绑定!'
        else:
            return res

    def osuV2stat(self, qq, groupid):
        rs = ""
        status, ret = self.getV2osuInfo(qq, groupid)
        if status < 0:
            return ret

        uid = ret["id"]
        grade_counts = ret['statistics']['grade_counts']
        pp = ret['statistics']['pp']
        pc = ret['statistics']['play_count']
        acc = ret['statistics']['hit_accuracy']
        username = ret["username"]
        join_time = ret['join_date'].split('T')[0]

        total_hits = ret["statistics"]["total_hits"]
        tth_pc_incr = int(total_hits / pc)
        total_hits_str = self.numberFormat2w(total_hits)
        tth_pc_incr_str = self.numberFormat2w(tth_pc_incr)

        play_time = ret["statistics"]["play_time"]
        play_days = play_time / 84600
        play_hours = play_time % 84600 / 3600

        if not ret['last_visit']:
            last_visit_str = '?'
        else:
            last_visit_f, last_visit_s = ret['last_visit'].split('T')
            last_visit_utc = '%s %s' % (last_visit_f, last_visit_s.split('+')[0])
            last_visit = datetime.strptime(last_visit_utc, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)
            last_visit_str = datetime.strftime(last_visit, '%Y-%m-%d %H:%M')

        follower_count = ret["follower_count"]
        avatar = ret["avatar_url"]
        join_days = (datetime.now()-datetime.strptime(join_time, '%Y-%m-%d')).days
        pp_days_incr = round(float(pp) / join_days, 2)
        pc_days_incr = round(float(pc) / join_days, 2)

        # bp
        botIns = botHandler.botHandler()
        bpinfo = botIns.getRecBp(uid, "5")
        bp1 = bpinfo[0]
        c50,c100,c300,cmiss = int(bp1['count50']),int(bp1['count100']),int(bp1['count300']),int(bp1['countmiss'])
        bp1_acc = round((c50*50+c100*100+c300*300)/(c50+c100+c300+cmiss)/300*100, 2)
        bp1_mod = ','.join(mods.getMod(int(bp1['enabled_mods'])))
        bp1_pp = round(float(bp1['pp']))
        bp1_rank = bp1['rank']
        bp1_data = bp1['date']
        bp1_bid = bp1['beatmap_id']
        bp1_days = (datetime.now()-datetime.strptime(bp1_data, '%Y-%m-%d %H:%M:%S')).days
        if bp1_days > 365:
            bp1_days_str = '%s年前' % int(bp1_days / 365)
        elif bp1_days > 182:
            bp1_days_str = '半年前'
        elif bp1_days > 30:
            bp1_days_str = '%s个月前' % int(bp1_days / 30)
        else:
            bp1_days_str = '%s天前' % bp1_days
        # map
        bp1_mapInfo = botIns.getOsuBeatMapInfo(bp1_bid)
        bp1_stars = bp1_mapInfo["difficultyrating"][:3]

        rs += '{username}\n'.format(username=username)
        rs += '[CQ:image,cache=0,file={avatar}]\n'.format(avatar=avatar)
        rs += '{pp}pp ({pp_days_incr}/day)\n'.format(pp=int(pp), pp_days_incr=pp_days_incr)
        rs += '{pc}pc ({pc_days_incr}/day)\n'.format(pc=pc, pc_days_incr=pc_days_incr)
        rs += '{tth}tth ({tth_pc_incr}/pc)\n'.format(tth=total_hits_str, tth_pc_incr=tth_pc_incr_str)
        rs += '--------------------\n'
        rs += 'SS+({ssh}) | SS({ss}) | S+({sh}) | S({s}) | A({a})\n'.format(**grade_counts)
        rs += 'bp1: {pp}pp,{stars}*,{acc}%,+{mod}({d})\n'.format(pp=bp1_pp, acc=bp1_acc, mod=bp1_mod, d=bp1_days_str, stars=bp1_stars)
        rs += '--------------------\n'
        rs += '粉丝数: {follower_count}\n'.format(follower_count=follower_count)
        rs += '爆肝时长: {play_days}天{play_hours}小时\n'.format(play_days=int(play_days), play_hours=int(play_hours))
        rs += '最后登录: {last_visit_str}\n'.format(last_visit_str=last_visit_str)
        rs += '注册时间: {join_time} ({join_days}天)'.format(join_time=join_time, join_days=join_days)
        return rs

    # def drawRankLine(self, y, osuname, pp, locate, rank1, rank2):
        
    #     x=[i for i in range(len(y))]

    #     plt.figure(figsize=(6,3))
    #     ys1 = max(y) - (max(y) - min(y)) / 10
    #     ys2 = max(y) - (max(y) - min(y)) / 10 * 1.8
    #     ys3 = max(y) - (max(y) - min(y)) / 10 * 2.6
    #     plt.text(30, ys3, 'interbot 1,688pp')
    #     plt.text(30, ys2, 'china #5,232')
    #     plt.text(31, ys1, '#161,188')
    #     plt.plot(x, y)

    #     ax = plt.gca()
    #     ax.invert_yaxis()

    #     plt.savefig('rank.png')


    def drawRankLine(self, res, qq):
        y = res['rankHistory']['data']
        x=[i for i in range(len(y))]
        osuname = res['username']
        pp = format(int(float(res['statistics']['pp'])), ',')
        rank = res['statistics']['rank']
        globalrank = format(int(rank.get('global', 0)), ',')
        countryrank = format(int(rank.get('country', 0)), ',')
        countryname = res['country']['name']
        plt.figure(figsize=(6,3))
        maxy = max(y)
        miny = min(y)
        ys1 = maxy - (maxy - miny) / 10
        ys2 = maxy - (maxy - miny) / 10 * 1.8
        ys3 = maxy - (maxy - miny) / 10 * 2.6
        plt.text(30, ys3, '%s %spp' % (osuname, pp))
        plt.text(30, ys2, '%s #%s' % (countryname, countryrank))
        plt.text(31, ys1, '#%s' % globalrank)
        plt.plot(x, y)

        ax = plt.gca()
        ax.invert_yaxis()

        imgPath = '/static/interbot/image/tmp/%s_rank.png' % qq
        plt.savefig(imgPath)

        return 'http://interbot.cn/itbimage/tmp/%s_rank.png' % qq

    def drawPlayCount(self, res, qq):
        data = res['monthly_playcounts']
        dates = []
        counts = []
        for d in data[-10:]:
            dates.append(d["start_date"])
            counts.append(int(d["count"]))
            
        xs=[datetime.strptime(d, "%Y-%m-%d").date() for d in dates]
        ys = counts
        # 配置横坐标
        plt.figure(figsize=(6,3))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.plot(xs, ys)
        # 自动旋转日期标记
        plt.gcf().autofmt_xdate()  

        imgPath = '/static/interbot/image/tmp/%s_playcount.png' % qq
        plt.savefig(imgPath)

        return 'http://interbot.cn/itbimage/tmp/%s_playcount.png' % qq

    def numberFormat2w(self, n):
        """数值转换为带w的字符串"""
        rs = n
        if n >= 10000:
            rs = '%sw' % int(n/10000)
        return rs

    def get_user_page(self, uid, name, page):
        kw = {
            'uid': uid
        }
        res = ppyAPI.apiRoute('userpage', **kw)
        if not res or len(res) < 1:
            return '抓取不到个人主页信息！'
        result = (res).replace('<br />','\n')
        repatt = re.compile(r'<.*?>')
        result = re.sub(repatt,'',result)
        result = HTMLParser().unescape(result)
        pagesize = 250
        total = (len(result)+pagesize)//pagesize
        if page > total:
            page = total
        s_msg = name+"'s userpage   "
        s_msg = s_msg + '第%s页,共%s页\n'%(str(page),str(total))
        return s_msg + result[pagesize*(page-1):pagesize*page]

    def get_pp_plus_info(self, osuname):
        try:
            url = f"https://syrin.me/pp+/u/{osuname}/"
            res = requests.get(url, timeout=120)
            if not res:
                return '网络异常!!'
            
            soup = BeautifulSoup(res.content, 'html.parser', from_encoding='utf-8')
            per_t = soup.find_all(class_="performance-table")

            s = f"{osuname}'s pp+\n"
            uinfo = self.getOsuUserInfo(osuname)
            raw_pp = float(uinfo[0]['pp_raw'])
            ppp = per_t[0].find_all('th')[1].text
            diff = float(ppp.replace(',', '').replace('pp', '')) - raw_pp
            s += f"{ppp}-{raw_pp:,.0f}pp({diff:+.0f}pp)\n"

            for i, r in enumerate(per_t[0].find_all("td")):
                if "Sum" in r.text:
                    break
                s += r.text
                if i % 2 != 0:
                    s += "\n"
            return s[:-1]
        except:
            logging.error(traceback.format_exc())
            return '那个破网站连不上!!'

    def refresh_mapinfo2db(self, bids):
        mapsinfo = [self.getOsuBeatMapInfo(bid) for bid in bids]
        map_args = score.args_format('map', mapsinfo)
        ret = score.map2db(map_args)
        return ret
