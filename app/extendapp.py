# -*- coding: utf-8 -*-
import os
import yaml
import json
import logging
from flask import Flask
from commLib import appTools
from extendappLib import extendHandler

with open('./app/defindapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)


app = Flask(__name__)


@app.route('/inter3', methods=['POST', 'GET'])
@appTools.deco()
def inter3(**kw):
    return 'inter3节点响应测试'

@app.route('/check', methods=['POST', 'GET'])
@appTools.deco(autoOusInfoKey='osuid,osuname')
def check(**kw):
    osuid = kw['autoOusInfoKey']['osuid']
    osuname = kw['autoOusInfoKey']['osuname']
    extObj = extendHandler.extendHandler()
    ret = extObj.checkFormat(osuid, osuname)
    return ret

@app.route('/map', methods=['POST', 'GET'])
@appTools.deco(autoOusInfoKey='osuid,osuname')
def map(**kw):
    osuid = kw['autoOusInfoKey']['osuid']
    osuname = kw['autoOusInfoKey']['osuname']
    extObj = extendHandler.extendHandler()
    map_id, num = extObj.choiceMap(osuid)
    if not map_id:
        return '本bot根本不想给你推荐图'
    return 'inter推荐给%s的图:https://osu.ppy.sh/b/%s  推荐指数:%s' %(osuname, map_id, num)

if __name__ == '__main__':
    app.run(threaded=True)
    
