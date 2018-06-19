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


if __name__ == '__main__':
    app.run()
    