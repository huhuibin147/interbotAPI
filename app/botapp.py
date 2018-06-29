# -*- coding: utf-8 -*-
import yaml
import json
import logging
from flask import Flask
from flask import request
from botappLib import botHandler
from commLib import appTools

with open('./app/botapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)

app = Flask(__name__)


@app.route('/rctpp', methods=['POST'])
@appTools.deco()
def rctpp(**kw):
    logging.info(kw['qq'])
    return 'rctpp'



if __name__ == '__main__':
    app.run()
    
