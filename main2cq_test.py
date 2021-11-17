# -*- coding: utf-8 -*-
import json
import logging
import requests
import threading
import asyncio
import websockets
from aiocqhttp import CQHttp
# from tornado.wsgi import WSGIContainer
# from tornado.httpserver import HTTPServer
# from tornado.ioloop import IOLoop
from commLib import cmdRouter

bot = CQHttp(api_root='http://127.0.0.1:5700/')
#bot = CQHttp(api_root='http://xfs.com:5700/')

centerURL = 'http://inter1.com/center/msg'

# 初始化日志格式
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s]%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



@bot.on_message()
async def handle_msg(context):
    if context.get('message'):
        context['message'] = convert(context['message'])
    res = requests.post(centerURL, data={"context": json.dumps(context)})
    if res.status_code == 200 and res.text:
        await bot.send(context, res.text)
    return

@bot.on_request()
def handle_request(context):
    logging.info('on_request.....')
    logging.info(context)
    t = threading.Thread(target=msgHandler, args=(bot, context, ))
    t.start()
    return

@bot.on_notice()
def handle_notice(context):
    logging.info('on_notice.....')
    logging.info(context)
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

bot.run(host='0.0.0.0', port=8889)

# def wsgiMain():
#     #bot.run(host='0.0.0.0', port=8887)
#     bot.run(host='0.0.0.0', port=8889)


# # 主线程
# mainThread = threading.Thread(target=wsgiMain, args=())
# mainThread.start()


# ws服务
async def wsMain(websockets, path):
    recvJson = await websockets.recv()
    recvDict = json.loads(recvJson)
    # await websockets.send(msg)
    interface = recvDict.get('interface', 'send_msg')
    if interface == "send_msg":
        if 'groupid' in recvDict:
            bot.send_group_msg(group_id=int(recvDict['groupid']), message=recvDict['msg'])
        elif 'qqid' in recvDict:
            bot.send_private_msg(user_id=int(recvDict['qqid']), message=recvDict['msg'])
    elif interface == "smoke":
        bot.set_group_ban(group_id=int(recvDict["groupid"]), user_id=int(recvDict["qqid"]), duration=int(recvDict["ts"]))
    elif interface == "send_like":
        bot.send_like(user_id=int(recvDict["qqid"]), times=int(recvDict["times"]))
    elif interface == "kick":
        bot.set_group_kick(group_id=int(recvDict["groupid"]), user_id=int(recvDict["qqid"]))
    elif interface == "callback":
        rs = getattr(bot, recvDict["method"])(**recvDict["kv"])
        params = {
            "ret": json.dumps(rs),
            "callbackargs": recvDict["callbackargs"]
        }
        cThread = threading.Thread(target=callbackMain, args=(recvDict["callbackcmd"], params))
        cThread.start()
    elif interface == "set_group_add_request":
        bot.set_group_add_request(flag=recvDict["flag"], sub_type=recvDict["sub_type"], approve=recvDict["approve"], reason=recvDict["reason"])

def callbackMain(callbackcmd, args):
    cmdRouter.invoke(callbackcmd, args)

ser = websockets.serve(wsMain, '0.0.0.0', 12345)
asyncio.get_event_loop().run_until_complete(ser)
asyncio.get_event_loop().run_forever()



# 使用WSGI
# http_server = HTTPServer(WSGIContainer(bot.wsgi))
# http_server.listen(8887)
# IOLoop.instance().start()

