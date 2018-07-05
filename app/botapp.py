# -*- coding: utf-8 -*-
import yaml
import json
import logging
import requests
from flask import Flask
from flask import request
from botappLib import botHandler
from commLib import appTools

with open('./app/botapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/rctpp', methods=['POST'])
@appTools.deco()
def rctpp(**kw):
    # todo 加入未绑定传id情况
    b = botHandler.botHandler()
    osuinfo = b.getOsuInfo({"qqid":kw['qqid'], "groupid": kw['groupid']})
    logging.info(osuinfo)
    if osuinfo:
        osuid = osuinfo[0]['osuid']
        recinfo = b.getRecInfo({"osuid": osuid, "limit": "1"})
        logging.info(recinfo)
        if not recinfo:
            res = "please play game!"
        else:
            # rec计算
            bid = recinfo[0]['beatmap_id']
            rinfo = b.exRecInfo(recinfo[0])
            extend = b.convert2oppaiArgs(**rinfo) 
            oppainfo = b.oppai(bid, extend)
            ret = b.formatRctpp(oppainfo, recinfo[0]['rank'])

            # fc计算
            fcacc = b.calFcacc(recinfo[0])
            extendFc = b.convert2oppaiArgs(rinfo['mods'], fcacc)
            oppainfoFc = b.oppai(bid, extendFc)
            ppFc = b.oppai2pp(oppainfoFc)

            # ac计算
            extendAc = b.convert2oppaiArgs(rinfo['mods'])
            oppainfoAc = b.oppai(bid, extendAc)
            ppAc = b.oppai2pp(oppainfoAc)
            bidurl = 'https://osu.ppy.sh/b/%s' % bid
            res = "%s | fc: %s | ss: %s\n%s" % (ret, ppFc, ppAc, bidurl)
    else:
        res = "u don't bind!"
    return res

@app.route('/rec', methods=['POST'])
@appTools.deco()
def recent(**kw):
    uid = kw['iargs'][0]
    url = "http://interbot.top/osuppy/recent"
    res = requests.post(url, data={"osuid": uid, "limit": "1"})
    return res.text


if __name__ == '__main__':
    app.run()
    
