# -*- coding: utf-8 -*-
import json
import logging
import requests
import threading
from cqhttp import CQHttp
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


bot = CQHttp(api_root='http://127.0.0.1:5701/')

centerURL = 'http://118.24.91.98/center/msg'

# 初始化日志格式
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s]%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@bot.on_message()
def handle_msg(context):
    context['message'] = convert(context['message'])
    t = threading.Thread(target=msgHandler, args=(bot, context, ))
    t.start()


def convert(msg):
    tmps = msg.replace('&amp;', '&')
    tmps = tmps.replace('&#91;', '[')
    tmps = tmps.replace('&#93;', ']')
    tmps = tmps.replace('&#44;', ',')
    return tmps

def msgHandler(bot, context):
    res = requests.post(centerURL, data={"context": json.dumps(context)})
    if res.status_code == 200 and res.text:
        logging.info(res.text)
        bot.send(context, res.text)

# 使用WSGI
http_server = HTTPServer(WSGIContainer(bot.wsgi))
http_server.listen(8887)
IOLoop.instance().start()

