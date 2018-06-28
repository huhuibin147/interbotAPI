# -*- coding: utf-8 -*-
import yaml
import json
import logging
from flask import Flask
from flask import request

with open('./app/ppyapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)


app = Flask(__name__)


@app.route('/bp', methods=['POST'])
def bpApi():
    return 'bpApi test'


if __name__ == '__main__':
    app.run()
    