# -*- coding:utf8 -*-
import json
import logging
import websocket


class pushC():


    def __init__(self, ws=None):
        self.ws = ws if ws else 'ws://inter4.com:12345/'

    def sendCq(self, groupid, msg):
        ws = websocket.create_connection(self.ws)
        ws.send(json.dumps({
                "groupid": groupid,
                "msg": msg
            }))
        logging.info('send to[%s],msg[%s]', groupid, msg)
        ws.close()

    def sendCqPrivate(self, qqid, msg):
        ws = websocket.create_connection(self.ws)
        ws.send(json.dumps({
                "qqid": qqid,
                "msg": msg
            }))
        logging.info('send to[%s],msg[%s]', qqid, msg)
        ws.close()


def pushMsgOne(groupid, msg):
    pushC().sendCq(groupid, msg)

def pushMsgOnePrivate(qqid, msg):
    pushC().sendCqPrivate(qqid, msg)

def pushGroupMsg(groupids, msg):
    obj = pushC()
    logging.info('群发开始')
    for groupid in groupids:
        obj.sendCq(groupid, msg)
    logging.info('群发结束')

if __name__ == '__main__':
    groupids = [514661057,758120648,669361496,885984366,713688443,609633978,709804864]
    msg = "【interbot通知消息】\nxxxxx"
    pushGroupMsg(groupids, msg)
