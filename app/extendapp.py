# -*- coding: utf-8 -*-
import os
import yaml
import json
import logging
from flask import Flask
from flask import request
from commLib import appTools

with open('./app/defindapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)


app = Flask(__name__)


@app.route('/inter3', methods=['POST'])
@appTools.deco()
def inter3(**kw):
    return 'inter3节点测试'

if __name__ == '__main__':
    app.run()
    
