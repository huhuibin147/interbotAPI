# -*- coding:utf8 -*-
import json
import logging
import websocket


class pushC():


    def __init__(self, ws=None):
        self.ws = ws if ws else 'ws://interbot.cn:12345/'

    def sendCq(self, groupid, msg):
        ws = websocket.create_connection(self.ws)
        ws.send(json.dumps({
                "groupid": groupid,
                "msg": msg
            }))
        logging.info('send to[%s],msg[%s]', groupid, msg)
        ws.close()


def pushMsgOne(groupid, msg):
    pushC().sendCq(groupid, msg)

def pushGroupMsg(groupids, msg):
    obj = pushC()
    logging.info('群发开始')
    for groupid in groupids:
        obj.sendCq(groupid, msg)
    logging.info('群发结束')

if __name__ == '__main__':
    groupids = [614892339, 514661057, 641236878, 758120648]
    msg = "interbot通知消息：pro已到期(续不起费)，准备进行降级到air版本，直接影响功能[群榜单]，rank榜上传不受影响，但是查询功能会失效"
    pushGroupMsg(groupids, msg)