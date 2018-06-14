# -*- coding: utf-8 -*-
import yaml
from flask import Flask

yamlFile = open('app.yaml')
config = yaml.load(yamlFile)


app = Flask(__name__)


@app.route('/test')
def testApi():
    return 'this is a api test'


if __name__ == '__main__':
    app.run()