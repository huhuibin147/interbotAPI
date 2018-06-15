# -*- coding: utf-8 -*-
import yaml
import json
import logging
from flask import Flask
from flask import request

yamlFile = open('app.yaml')
config = yaml.load(yamlFile)


app = Flask(__name__)


@app.route('/msg', methods=['POST'])
def testApi():
    context = request.form.get("context")
    logging.info('recive:%s' % context)
    logging.info('msg:%s' % json.loads(context))
    return 'this is a api test'


if __name__ == '__main__':
    app.run()
