# -*- coding: utf-8 -*-
import json
import logging
import requests
import threading
import asyncio
import websockets
from cqhttp import CQHttp
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


bot = CQHttp(api_root='http://127.0.0.1:5700/')

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
    return


def convert(msg):
    tmps = msg.replace('&amp;', '&')
    tmps = tmps.replace('&#91;', '[')
    tmps = tmps.replace('&#93;', ']')
    tmps = tmps.replace('&#44;', ',')
    return tmps

def msgHandler(bot, context):
    res = requests.post(centerURL, data={"context": json.dumps(context)})
    if res.status_code == 200 and res.text:
        bot.send(context, res.text)

def wsgiMain():
    bot.run(host='0.0.0.0', port=8887)


# 主线程
mainThread = threading.Thread(target=wsgiMain, args=())
mainThread.start()


# ws服务
async def wsMain(websockets, path):
    recvJson = await websockets.recv()
    recvDict = json.loads(recvJson)
    # await websockets.send(msg)
    bot.send_group_msg(group_id=int(recvDict['groupid']), message=recvDict['msg'])

ser = websockets.serve(wsMain, '0.0.0.0', 12345)
asyncio.get_event_loop().run_until_complete(ser)
asyncio.get_event_loop().run_forever()



# 使用WSGI
# http_server = HTTPServer(WSGIContainer(bot.wsgi))
# http_server.listen(8887)
# IOLoop.instance().start()

