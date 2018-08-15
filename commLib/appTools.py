# -*- coding:utf8 -*-
import json
import time
import logging
import functools
from flask import request
from commLib import cmdRouter



# 接收参数,来自消息中心
def deco(**kw):
    # 控制位置
    autoOusInfoKey = kw.get('autoOusInfoKey')

    def inner(func):

        @functools.wraps(func) 
        def _newfunc(*args, **kwargs):
            st = time.time()

            # 参数嵌入
            kwargs.update(request.form.to_dict())
            if 'iargs' in kwargs:
                kwargs['iargs'] = json.loads(kwargs['iargs'])

            logging.info('recive kwargs:%s', kwargs)

            if autoOusInfoKey:
                kwargs['autoOusInfoKey'] = {}
                inputs = "" if not kwargs['iargs'] else ' '.join(kwargs['iargs'])
                autokeys = autoOusInfoKey.split(',')
                if not inputs:
                    qqid = kwargs['qqid'] if not kwargs.get('atqq') else kwargs['atqq']
                    osuinfo = getOsuInfo(qqid, kwargs['groupid'])
                    if not osuinfo:
                        return "你倒是绑定啊.jpg"
                    for k in autokeys:
                        kwargs['autoOusInfoKey'][k] = osuinfo[0][k]
                else:
                    for k in autokeys:
                        kwargs['autoOusInfoKey'][k] = inputs
                logging.info('autoOusInfoKey:%s,value:%s', autoOusInfoKey, kwargs['autoOusInfoKey'])

            # 方法主体
            rs = func(*args, **kwargs)

            logging.info('[%s]执行时间:%ss', func.__name__, round(time.time()-st, 2))
            return rs

        return _newfunc
    return inner


def getOsuInfo(qqid, groupid):
    """取osu用户绑定信息
    Args:
        qq/groupid
    """
    ret = cmdRouter.invoke(
        '!uinfo', {"qqid": qqid, "groupid": groupid}
    )
    return json.loads(ret)