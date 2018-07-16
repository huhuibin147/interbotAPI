# -*- coding: utf-8 -*-
import yaml
import json
import logging
from flask import Flask
from flask import request

with open('./app/defindapp.yaml', encoding='utf8') as f:
    config = yaml.load(f)


app = Flask(__name__)


@app.route('/defindmsg', methods=['POST'])
def defindmsg():
    context = request.form.get("context")
    context = json.loads(context)
    logging.info(context)
    return ''


if __name__ == '__main__':
    app.run(threaded=True)
