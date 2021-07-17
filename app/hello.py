# -*- coding: utf-8 -*-
from flask import Flask
from commLib import appTools
from ppyappLib import ppyHandler



app = Flask(__name__)


@app.route('/hellofunc', methods=['GET','POST'])
def hello(**kw):
    return 'hello from yukiroki node' 

@app.route('/ppplus', methods=['POST'])
@appTools.deco(autoOusInfoKey='osuname')
def ppplus(**kw):
    b = ppyHandler.ppyHandler()
    osuname = kw['autoOusInfoKey']['osuname']
    res = b.get_pp_plus_info(osuname)
    return res



if __name__ == '__main__':
    app.run(threaded=True)
    

