# -*- coding: utf-8 -*-
from flask import Flask



app = Flask(__name__)


@app.route('/hellofunc', methods=['GET','POST'])
def hello(**kw):
    return 'hello from yukiroki node' 




if __name__ == '__main__':
    app.run(threaded=True)
    

