# -*- coding: utf-8 -*-
import yaml
import json
import logging
import requests
from commLib import interRequest
from baseappLib import baseHandler

with open('./ppyappLib/ppy.yaml', encoding='utf8') as f:
    config = yaml.load(f)

OSU_API_KEY = config['osuApiKey']

apiv2Url = 'https://osu.ppy.sh/api/v2/{endponit}'
apiv2FailWord = 'unauthorized'

ref = {
    'recent': 'http://osu.ppy.sh/api/get_user_recent?k=%s&u={uid}&m={mode}&limit={limit}' % OSU_API_KEY,
    'get_scores': 'http://osu.ppy.sh/api/get_scores?k=%s&u={uid}&b={bid}&limit={limit}' % OSU_API_KEY,
    'userinfo': 'http://osu.ppy.sh/api/get_user?k=%s&u={uid}' % OSU_API_KEY,
    'bp': 'http://osu.ppy.sh/api/get_user_best?k=%s&u={uid}&m={mode}&limit={limit}' % OSU_API_KEY,
    'beatmap': 'http://osu.ppy.sh/api/get_beatmaps?k=%s&b={bid}' % OSU_API_KEY,
    'skill': 'http://osuskills.com/user/{osuname}',
    'skillvs': 'http://osuskills.com/user/{osuname}/vs/{vsosuname}',
    'userpage': 'http://osu.ppy.sh/pages/include/profile-userpage.php?u={uid}',
    'mp': 'http://osu.ppy.sh/api/get_match?k=%s&mp={mid}' % OSU_API_KEY
}


def apiRoute(api, **kw):
    # 填充方法
    ret = None
    url = ref[api].format(**kw)
    res = requests.get(url)
    logging.info('apiRoute url:%s|status:%s|res:%s', url, res, res.text)
    if res.status_code == 200 and res.text:
        try:
            ret = json.loads(res.text)
        except:
            return res.text

    return ret

def crawlPageByGet(api, **kw):
    # 抓取方法
    ret = None
    req = interRequest.interReq()
    url = ref[api].format(**kw)
    res = req.get(url)
    logging.info('crawlPageByGet url:%s|status:%s|', url, res)
    if res.status_code == 200 and res.text:
        ret = res.text

    return ret

def apiv2Req(endponit, token, refreshtoken, isrefresh=1, **kw):
    """apiv2请求主体
    Returns:
        ret:
            -1 请求异常
            -2 token失效
            或 list对象
    """
    url = apiv2Url.format(endponit=endponit)
    header = {
        'Authorization': 'Bearer %s' % token
    }
    ret = -1
    res = requests.get(url, headers = header)
    logging.info('apiV2 url:%s|status:%s', url, res)
    if res.status_code == 200:
        if apiv2FailWord not in res.text:
            ret = json.loads(res.text)
            return ret
            
    ret = -2
    logging.info('token失效')
    if isrefresh:
        rs = apiv2RefreshToken(refreshtoken, **kw)
        if rs not in (-1, -2):
            logging.info('token刷新成功！')
            return apiv2Req(endponit, rs, refreshtoken, isrefresh=0, **kw)

    return ret

def apiv2RefreshToken(refreshtoken, updatedb=1, **kw):
    """token刷新
    """
    url = 'https://osu.ppy.sh/oauth/token'
    header = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'grant_type': 'refresh_token',
        'client_id': '19',
        'client_secret': '46SmWQ2TyF5FMECwHrblTZ2oiYq4yyAbOH5BDDS7',
        'refresh_token': refreshtoken,
        "redirect_uri": "http://interbot.cn/apiv2/auth"
    }
    ret = -1
    res = requests.post(url, headers=header, data=params)
    logging.info('refreshtoken:%s|status:%s', url, res)
    if res.status_code == 200:
        rs = json.loads(res.text)
        if not rs.get('error'):
            ret = rs['access_token']
            if updatedb:
                baseHandler.baseHandler().updateToken(kw['qq'], kw['groupid'], 
                        rs['access_token'], rs['refresh_token'])
        else:
            ret = -2
            logging.info('token失效')

    return ret
