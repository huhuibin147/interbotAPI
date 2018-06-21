# -*- coding: utf-8 -*-
import yaml
import json
import logging
from flask import Flask
from flask import request
from msgCenterLib import msgHandler

with open('./app/baseapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/uinfo', methods=['POST'])
def userInfoApi():
    return 'userinfoAPI test'

@app.route('/args', methods=['POST'])
def argsApi():
    iargs = request.form.get("iargs")
    args = json.loads(iargs)
    logging.info('recive args:%s' % args)
    return iargs


if __name__ == '__main__':
    app.run()
    
