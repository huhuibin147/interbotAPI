# -*- coding: utf-8 -*-
import yaml
import json
import random
import logging
from flask import Flask
from flask import request
from baseappLib import baseHandler
from commLib import appTools
from commLib import Config

with open('./app/baseapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/uinfo', methods=['POST'])
@appTools.deco()
def userInfoApi(**kw):
    ins = baseHandler.baseHandler()
    rts = ins.getUserBindInfo({"qq":kw['qqid']})
    return json.dumps(rts)

@app.route('/uinfo2', methods=['POST'])
@appTools.deco()
def userInfoApi2(**kw):
    ins = baseHandler.baseHandler()
    rts = ins.getUserBindInfo2(kw['qqid'])
    return json.dumps(rts)


@app.route('/setid', methods=['POST'])
@appTools.deco()
def bindUserInfo(**kw):
    ins = baseHandler.baseHandler()
    osuid = ' '.join(kw['iargs']) if kw.get('iargs') else kw.get('osuid', '')
    r = ins.bindOsuUser(osuid, kw['qqid'], kw['groupid'])
    if r > 0:
        rs = '绑定成功!'
    elif r == 0:
        rs = '重复绑定!'
    elif r == -1:
        rs = '系统异常!'
    elif r == -2:
        rs = '网络或者用户名异常!'
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

@app.route('/chat', methods=['POST'])
@appTools.deco()
def chat(**kw):
    inputs = ' '.join(kw['iargs'])
    ins = baseHandler.baseHandler()
    r = ins.chat2bot(inputs)
    return r

@app.route('/oauth', methods=['POST'])
@appTools.deco()
def bindUserToken(**kw):
    ins = baseHandler.baseHandler()
    ins.setOauthCache(kw['qqid'], kw['groupid'])
    url = 'https://osu.ppy.sh/oauth/authorize?client_id=19&response_type=code&state=%sx%s&scope=friends.read%%20identify&redirect_uri=http://interbot.cn/apiv2/auth' % (kw['qqid'], kw['groupid'])
    ret = url + '\n*可在http://interbot.cn/help中的oauth指令说明获取模板，自行替换到与图片相同信息，在浏览器中打开认证\n如果不使用v2认证，也可暂时使用老版绑定(无法使用部分v2功能)，!setid osuname'
    return ret

@app.route('/permission', methods=['POST'])
@appTools.deco()
def userPermission(**kw):
    ins = baseHandler.baseHandler()
    ret = ins.getUserPermission(kw['qqid'])
    return ret

@app.route('/settokenpms', methods=['POST'])
@appTools.deco()
def userPermissionSet(**kw):
    ins = baseHandler.baseHandler()
    pms = Config.TOKEN_PERMISSION
    levels = pms.keys()
    usage = 'usage: ¡settokenpms %s\n注:' % ('/'.join(levels))
    for k in levels:
        usage += k + '-' + pms[k] + ' '
    if not kw.get('iargs'):
        return usage
    inputLevel = kw['iargs'][0]
    if inputLevel not in levels:
        return usage
    ret = ins.updateUserPermission(kw['qqid'], inputLevel)
    rs = "token权限更新成功!\n当前权限: %s-%s" % (inputLevel, pms[inputLevel])
    if ret <= 0:
        rs = "token权限更新失败!\n当前权限: %s-%s" % (inputLevel, pms[inputLevel])
    return rs

if __name__ == '__main__':
    app.run(threaded=True)
    
