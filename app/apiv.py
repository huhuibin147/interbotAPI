# -*- coding: utf-8 -*-
import os
import yaml
import json
import random
import logging
import requests
from flask import Response, Flask
from flask import request
from apivLib import apivHandler
from commLib import interRedis
from commLib import Config

with open('./app/apiv.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


# @app.route('/auth', methods=['GET'])
# def statApi(**kw):
#     code = request.args.get('code')
#     state = request.args.get('state')
#     qq, groupid = state.split('x')
#     obj = apivHandler.apivHandler()
#     rs = obj.userOauth(code, state)
#     if rs > 0:
#         ret = '授权成功！屙屎账号成功绑定interbot！（不要期待后续功能咕咕） **请核对绑定Q号[%s]，如不正确，请去interbot生成自己的链接 重新绑定！ ' % qq
#     else:
#         ret = '绑定出错，请联系inter!'
#     return ret

@app.route('/auth', methods=['GET'])
def newSetid(**kw):
    code = request.args.get('code')
    state = request.args.get('state')
    qq, gid = state.split('x')
    logging.info('回调记录,qq[%s]' % qq)
    
    rds = interRedis.connect('osu2')
    key = Config.OAUTH_CACHE_KEY.format(qq=qq, gid=gid)
    if not rds.get(key):
        logging.error('redis验证失败')
        return "由于你点击了别人的认证链接(或者已过期)，绑定失败，请在群中发送!oauth获取你的认证链接"

    obj = apivHandler.apivHandler()
    rs = obj.newUserOauth(code, state)
    if rs > 0:
        ret = '授权成功！屙屎账号成功绑定interbot！ **请核对绑定Q号[%s]，如不正确，请去interbot生成自己的链接 重新绑定！ ' % qq
    elif rs == -1:
        ret = 'ppy通讯异常，可重试链接，多次失败请私聊联系inter!'
    else:
        ret = '系统异常，绑定出错，请私聊联系inter!'
    return ret


if __name__ == '__main__':
    app.run(threaded=True)
    
