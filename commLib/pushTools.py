# -*- coding:utf8 -*-
import json
import logging
import websocket


class pushC():


    def __init__(self, ws=None):
        self.ws = ws if ws else 'ws://inter1.com:12345/'

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

    def sendCqSmoke(self, groupid, qqid, ts):
        ws = websocket.create_connection(self.ws)
        ws.send(json.dumps({
                "interface": "smoke",
                "groupid": groupid,
                "qqid": qqid,
                "ts": ts
            }))
        logging.info('smoke group[%s] qq[%s] ts[%s]', groupid, qqid, ts)
        ws.close()

    def sendCqLike(self, qqid, ts):
        ws = websocket.create_connection(self.ws)
        ws.send(json.dumps({
                "interface": "send_like",
                "qqid": qqid,
                "times": ts
            }))
        logging.info('send like qq[%s] ts[%s]', qqid, ts)
        ws.close()

    def sendCqKick(self, groupid, qqid):
        ws = websocket.create_connection(self.ws)
        ws.send(json.dumps({
                "interface": "kick",
                "qqid": qqid,
                "groupid": groupid
            }))
        logging.info('send kick groupid[%s] qq[%s]', groupid, qqid)
        ws.close()

    def sendCqCallback(self, method, kv, callbackcmd, callbackargs):
        ws = websocket.create_connection(self.ws)
        ws.send(json.dumps({
                "interface": "callback",
                "method": method,
                "callbackcmd": callbackcmd,
                "callbackargs": callbackargs,
                "kv": kv
            }))
        logging.info('sendCqCallback method[%s] kv[%s] callbackcmd[%s]', method, kv, callbackcmd)
        ws.close()

    def sendCqSetRequest(self, flag, sub_type="add", approve="true", reason=""):
        ws = websocket.create_connection(self.ws)
        ws.send(json.dumps({
                "interface": "set_group_add_request",
                "flag": flag,
                "sub_type": sub_type,
                "approve": approve,
                "reason": reason
            }))
        logging.info('sendCqSetRequest flag[%s], approve[%s]', flag, approve)
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

def pushSmokeCmd(groupid, qqid, ts):
    pushC().sendCqSmoke(groupid, qqid, ts)

def pushLikeCmd(qqid, ts):
    pushC().sendCqLike(qqid, ts)

def pushKickCmd(groupid, qqid):
    pushC().sendCqKick(groupid, qqid)

def pushSetRequestCmd(flag, sub_type, approve, reason=""):
    pushC().sendCqSetRequest(flag, sub_type, approve, reason)

def pushCallbackCmd(method, kv, callbackcmd, callbackargs):
    """调用酷Q接口，同时回调服务
    Args:
        method coolq接口
        kv 接口参数
        callbackcmd 回调回来的服务cmd
        callbackargs 回调额外参数 json
    """
    pushC().sendCqCallback(method, kv, callbackcmd, callbackargs)

if __name__ == '__main__':
    # groupids = [514661057,758120648,669361496,885984366,713688443,609633978,709804864]
    # msg = "【interbot通知消息】\nxxxxx"
    # pushGroupMsg(groupids, msg)
    pushKickCmd("619786604", "405622418")
