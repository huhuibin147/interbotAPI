# -*- coding: utf-8 -*-
import yaml
import json
import logging
import requests
from commLib import interRequest

with open('./ppyappLib/ppy.yaml', encoding='utf8') as f:
    config = yaml.load(f)

OSU_API_KEY = config['osuApiKey']

ref = {
    'recent': 'https://osu.ppy.sh/api/get_user_recent?k=%s&u={uid}&m={mode}&limit={limit}' % OSU_API_KEY,
    'userinfo': 'https://osu.ppy.sh/api/get_user?k=%s&u={uid}' % OSU_API_KEY,
    'bp': 'https://osu.ppy.sh/api/get_user_best?k=%s&u={uid}&m={mode}&limit={limit}' % OSU_API_KEY,
    'beatmap': 'https://osu.ppy.sh/api/get_beatmaps?k=%s&b={bid}' % OSU_API_KEY,
    'skill': 'http://osuskills.tk/user/{osuname}',
    'skillvs': 'http://osuskills.tk/user/{osuname}/vs/{vsosuname}'
}


def apiRoute(api, **kw):
    # 填充方法
    ret = None
    url = ref[api].format(**kw)
    res = requests.get(url)
    logging.info('apiRoute url:%s|status:%s|res:%s', url, res, res.text)
    if res.status_code == 200 and res.text:
        ret = json.loads(res.text)

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