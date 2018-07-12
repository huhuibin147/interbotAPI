# -*- coding:utf8 -*-
import json
import time
import logging
import functools
from flask import request




# 接收参数,来自消息中心
def deco(**kw):
    # 控制位置

    def inner(func):

        @functools.wraps(func) 
        def _newfunc(*args, **kwargs):
            st = time.time()

            # 参数嵌入
            kwargs.update(request.form.to_dict())
            if 'iargs' in kwargs:
                kwargs['iargs'] = json.loads(kwargs['iargs'])

            logging.info('recive kwargs:%s', kwargs)

            # 方法主体
            rs = func(*args, **kwargs)

            logging.info('[%s]执行时间:%ss', func.__name__, round(time.time()-st, 2))
            return rs

        return _newfunc
    return inner