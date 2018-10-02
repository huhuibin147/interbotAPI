# -*- coding: utf-8 -*-
import os
import yaml
import json
import random
import logging
import requests
import traceback
from flask import Response, Flask
from flask import request
from subprocess import Popen
from ppyappLib import ppyHandler

with open('./app/apiapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/stat2', methods=['GET'])
def stat2Api(**kw):
    u = request.args.get('u')
    m = request.args.get('m', '')
    p = Popen('wget "http://interbot.club/stat/profile.php?u={u}&m={m}" -O /static/interbot/image/{u}.jpg'.format(
            u = u,
            m = m
        ), shell=True)
    p.wait()
    return "http://interbot.cn/itbimage/{u}.jpg".format(u=u)

@app.route('/stat', methods=['GET'])
def statApi(**kw):
    u = request.args.get('u')
    m = request.args.get('m', '')
    r = requests.get("http://interbot.club/stat/profile.php?u={u}&m={m}".format(
            u = u,
            m = m,
        ))
    resp = Response(r.content, mimetype="image/jpeg")
    return resp

@app.route('/me', methods=['POST'])
def apiv2me(**kw):
    qqid = request.form.get('qqid')
    groupid = request.form.get('groupid')
    url = "http://139.199.10.126/osubot/v2me"
        data = {
            "qqid": b.qq,
            "groupid": b.group_id
        }
        r = requests.post(url, timeout=10, data=data)
        try:
            rdata = json.loads(r.text)
            imgpath = ppyHandler.ppyHandler().drawRankLine(rdata, b.qq)
            return imgpath
        except:
            logging.error(traceback.format_ext())
            if len(r.text) < 50:
                return r.text
            else:
                return '异常'
    return resp


if __name__ == '__main__':
    app.run(threaded=True)
    
