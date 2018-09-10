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


@app.route('/inter3', methods=['POST'])
@appTools.deco()
def inter3(**kw):
    return 'inter3节点响应测试'

@app.route('/check', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuid')
@appTools.deco()
def check(**kw):
    return kw['osuid']

if __name__ == '__main__':
    app.run()
    
