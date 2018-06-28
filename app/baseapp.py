# -*- coding: utf-8 -*-
import yaml
import json
import logging
from flask import Flask
from flask import request
from baseappLib import baseHandler

with open('./app/baseapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/uinfo', methods=['POST'])
def userInfoApi():
    iargs = request.form.get("iargs")
    args = json.loads(iargs)
    logging.info('recive args:%s' % args)
    if len(args) != 1:
        return '缺少参数 error:1001'
    ins = baseHandler.baseHandler()
    rts = ins.getUserBindInfo(ins.autokvqq(args[0]))
    return json.dumps(rts)

@app.route('/args', methods=['POST'])
def argsApi():
    iargs = request.form.get("iargs")
    args = json.loads(iargs)
    logging.info('recive args:%s' % args)
    return iargs


if __name__ == '__main__':
    app.run()
    
