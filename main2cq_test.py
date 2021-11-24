# -*- coding: utf-8 -*-
import json
import logging
import aiohttp
from aiocqhttp import CQHttp


centerURL = 'http://inter1.com/center/msg'

# 初始化日志格式
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s]%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


bot = CQHttp()

@bot.on_message()
async def handle_msg(event):
    if event.get('message'):
        event['message'] = convert(event['message'])

    # 频道消息过滤
    if event.get("channel_id"):
        return

    async with aiohttp.ClientSession() as session:
        async with session.post(centerURL, 
                data={"context": json.dumps(event)}) as res:
            rs = await res.text()
            if rs:
                await bot.send(event, rs)
    return

def convert(msg):
    tmps = msg.replace('&amp;', '&')
    tmps = tmps.replace('&#91;', '[')
    tmps = tmps.replace('&#93;', ']')
    tmps = tmps.replace('&#44;', ',')
    return tmps


bot.run(host='127.0.0.1', port=8089)

