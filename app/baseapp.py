# -*- coding: utf-8 -*-
import yaml
import json
import random
import logging
from flask import Flask
from flask import request
from baseappLib import baseHandler
from commLib import appTools

with open('./app/baseapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/uinfo', methods=['POST'])
@appTools.deco()
def userInfoApi(**kw):
    ins = baseHandler.baseHandler()
    rts = ins.getUserBindInfo({"qq":kw['qqid'], "groupid": kw['groupid']})
    return json.dumps(rts)


@app.route('/setid', methods=['POST'])
@appTools.deco()
def bindUserInfo(**kw):
    ins = baseHandler.baseHandler()
    osuid = kw['iargs'][0] if kw.get('iargs') else kw.get('osuid', '')
    r = ins.bindOsuUser(osuid, kw['qqid'], kw['groupid'])
    if r > 0:
        rs = '绑定成功!'
    elif r == 0:
        rs = '重复绑定!'
    elif r == -1:
        rs = '系统异常!'
    elif r == -2:
<<<<<<< HEAD
        rs = '网络异常!(带空用下划线代替,带-请加-r,setid -r -x-'
=======
        rs = '网络异常!(空格用_代替,带-加选项-r'
>>>>>>> ee097532917090c4f2f96089f502e611c90c79f4
    else:
        rs = '未知错误!'
    return rs


@app.route('/args', methods=['POST'])
@appTools.deco()
def argsApi(**kw):
    return json.dumps(kw['iargs'])

@app.route('/roll', methods=['POST'])
@appTools.deco()
def roll(**kw):
    return str(random.randint(0, 100))

@app.route('/startrcm', methods=['POST'])
@appTools.deco()
def recommendTags(**kw):
    qq = kw['atqq'] if kw.get('atqq') else kw['qqid']
    groupid = kw['groupid']
    ins = baseHandler.baseHandler()
    r = ins.recordRecMap(qq, groupid)
    rs = ''
    if r == -1:
        rs = '推荐功能执行中!'
    elif r == 1:
        rs = '开启推荐map功能,发送图链,结束后请使用!stoprcm'
    return rs

@app.route('/stoprcm', methods=['POST'])
@appTools.deco()
def remRecommendTags(**kw):
    qq = kw['atqq'] if kw.get('atqq') else kw['qqid']
    groupid = kw['groupid']
    ins = baseHandler.baseHandler()
    r = ins.stopRecordRecMap(qq, groupid)
    return str(r)

@app.route('/rcmlist', methods=['POST'])
@appTools.deco()
def recommendList(**kw):
    qq = kw['atqq'] if kw.get('atqq') else kw['qqid']
    groupid = kw['groupid']
    ins = baseHandler.baseHandler()
    r = ins.recordRecMapList(qq, groupid)
    return str(r)


if __name__ == '__main__':
    app.run()
    
