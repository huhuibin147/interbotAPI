# -*- coding:utf8 -*-
import re
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
    # 不用使用输入代替用户名查询绑定
    rawinput = kw.get('rawinput')
    autouseatqq = kw.get('autouseatqq', True)

    def inner(func):

        @functools.wraps(func) 
        def _newfunc(*args, **kwargs):
            st = time.time()

            # 参数嵌入
            req_type = "POST"
            post_args = request.form.to_dict()
            kwargs.update(post_args)
            get_args = request.args.to_dict()
            if get_args:
                req_type = "GET"
            kwargs['req_type'] = req_type

            kwargs.update(get_args)
            if 'iargs' in kwargs:
                if req_type == "GET":
                    kwargs["iargs"] = kwargs["iargs"].split(',')
                else:
                    kwargs['iargs'] = json.loads(kwargs['iargs'])
            else:
                kwargs['iargs'] = []
            kwargs['groupid'] = kwargs.get("groupid", -1)
            kwargs['qqid'] = kwargs.get("qqid", -1)
            qqid = kwargs['qqid']

            kwargs['autoOusInfoKey'] = {}
            if 'osuname' in kwargs:
                kwargs['autoOusInfoKey']['osuid'] = kwargs['osuname']
                kwargs['autoOusInfoKey']['osuname'] = kwargs['osuname']

            logging.info('recive kwargs:%s', kwargs)

            if autoOusInfoKey:
                inputs = "" if not kwargs['iargs'] else ' '.join(kwargs['iargs'])
                autokeys = autoOusInfoKey.split(',')
                if not inputs or rawinput:
                    if autouseatqq and kwargs.get('atqq'):
                        qqid = kwargs['atqq']

                    if qqid != -1:
                        osuinfo = getOsuInfo(qqid)
                        if not osuinfo:
                            # return "您未绑定bot，发送!oauth，然后点击链接登录账号进行绑定(友情提示不要点别人的"
                            return "您未绑定bot\n请使用命令!setid osu用户名"
                        for k in autokeys:
                            kwargs['autoOusInfoKey'][k] = osuinfo.get(k)

                else:
                    if qqid != -1:
                        for k in autokeys:
                            kwargs['autoOusInfoKey'][k] = inputs
                logging.info('autoOusInfoKey:%s,value:%s', autoOusInfoKey, kwargs['autoOusInfoKey'])

            # 方法主体
            rs = func(*args, **kwargs)
            
            # GET自动转义
            if req_type == "GET":
                rs = out_html(rs)

            logging.info('[%s]执行时间:%ss', func.__name__, round(time.time()-st, 2))
            return rs

        return _newfunc
    return inner


def getOsuInfo(qqid):
    """取osu用户绑定信息
    Args:
        qq/groupid
    """
    ret = cmdRouter.invoke(
        '!uinfo2', {"qqid": qqid}
    )
    return json.loads(ret)

def out_html(data):
    r = f'<pre>{data}</pre>'
    p = re.compile('\[CQ:image,cache=0,file=(.*?)\]')
    cqimg = p.findall(data)
    for img in cqimg:
        r = r.replace(f'[CQ:image,cache=0,file={img}]', f'<img src="{img}" />')
    return r

def rm_cq_image(s):
    p = re.compile('\[CQ:image,cache=0,file=(.*?)\]')
    cqimg = p.findall(s)
    for img in cqimg:
        s = s.replace(f'[CQ:image,cache=0,file={img}]', '')
    return s
