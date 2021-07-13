# -*- coding: utf-8 -*-
import os
import yaml
import json
import random
import logging
import requests
from flask import Response, Flask
from flask import request



app = Flask(__name__)


@app.route('/hellofunc', methods=['GET','POST'])
def hello(**kw):
    return 'hello from yukiroki node' 


if __name__ == '__main__':
    app.run(threaded=True)
    

