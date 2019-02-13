# -*- coding: utf-8 -*-
import yaml
import json
import logging
from flask import Flask
from flask import request
from sysappLib import sysHandler

with open('./app/sysapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/nodetest', methods=['POST'])
def nodeTestApi(**kw):
    inst = sysHandler.sysHandler()
    r = inst.nodeAliveTest()
    return r

@app.route('/functest', methods=['POST'])
def funcTestApi(**kw):
    inst = sysHandler.sysHandler()
    r = inst.funcAliveTest()
    return r




if __name__ == '__main__':
    app.run(threaded=True)
    
