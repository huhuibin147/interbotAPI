# -*- coding:utf8 -*-
import json
import logging
import functools
from flask import request




# 接收参数,来自消息中心
def deco(**kw):
    # 控制位置

    def inner(func):

        @functools.wraps(func) 
        def _newfunc(*args, **kwargs):
            # 公用参数
            iargs = request.form.get("iargs")
            iargs = json.loads(iargs) if iargs else ''
            qq = request.form.get("qqid")
            groupid = request.form.get("groupid")
            logging.info('recive qqid:%s|groupid:%s|iargs:%s', qq, groupid, iargs)

            # 参数嵌入
            kwargs['iargs'] = iargs
            kwargs['qq'] = qq
            kwargs['groupid'] = groupid

            # 方法主体
            rs = func(*args, **kwargs)

            return rs

        return _newfunc
    return inner