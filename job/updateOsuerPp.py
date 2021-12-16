# -*- coding: utf-8 -*-
import os
import sys
import logging


sys.path.append('./')
sys.path.append('./commLib')
sys.path.append('./botappLib')

from botappLib import botHandler

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)



def once_insert():
    """自动抓取
    条件 -- 数据库是否存在今天的记录
    存在记录时 -- 做捡漏处理
    """
    ins = botHandler.botHandler()
    if not ins.is_insert_today():
        logging.info('今天未插入，开始执行插入...')
        ins.insert_forday()
    else:
        logging.info('今天插入已完成')




if __name__ == "__main__":
    once_insert()
