# -*- coding: utf-8 -*-
import os
import yaml
import json
import random
import logging
import requests
from flask import Response, Flask
from flask import request
from subprocess import Popen

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


if __name__ == '__main__':
    app.run(threaded=True)
    
