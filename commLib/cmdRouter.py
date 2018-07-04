# -*- coding: utf-8 -*-
import logging
import requests
from commLib import interMysql


def invoke(cmd, args):
    """远程调用
    Args:
        args 自行封装好传进来
    """
    res = getCmdRef(cmd)
    apiUrl = '{location}{api}'.format(
            location = res['location'],
            api = res['url']
        )

    # 调用核心 
    res = requests.post(
        apiUrl, 
        data = args
    )
    if res.status_code == 200:
        return res.text
    else:
        logging.info('调用[%s]异常' % apiUrl)

    return ''



def getCmdRef(cmd):
    """映射"""
    db = interMysql.Connect('osu2')
    sql = '''
        SELECT cmd, url, location
        FROM cmdRef WHERE cmd = %s
    '''
    res = db.query(sql, [cmd])
    if not res:
        return ''
    return res[0]