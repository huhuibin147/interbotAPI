# -*- coding: utf-8 -*-
import sys
sys.path.append('./')

import json
import random
import logging
from commLib import Config
from commLib import interRedis
from commLib import interMysql



class chatHandler():


    def __init__(self) -> None:
        pass

    def get_random_db_chat(self, sel_cnt = 1000):
        try:
            conn = interMysql.Connect("osu")
            csql = 'SELECT count(1) c FROM chat_logs'
            num = conn.query(csql)[0]['c']

            sql = '''
                SELECT content FROM chat_logs
            '''
            
            sql += ' limit %s,%s' % (random.randint(0, int(num)-sel_cnt), sel_cnt)
            res = conn.query(sql)
            return res
        except:
            logging.exception("")

        return []
        
    def collect_chat2redis(self):
        chat_Lst = self.get_random_db_chat()
        chat_str = json.dumps(chat_Lst)
        rds = interRedis.connect('osu2')
        rs = rds.setex(Config.CHAT_RANDOM_KEY, chat_str, 3600)
        logging.info("chat set to redis rs:%s", rs)
        return rs

    def random_chat(self):
        try:
            rds = interRedis.connect('osu2')
            rs = rds.get(Config.CHAT_RANDOM_KEY)
            chat_lst = json.loads(rs)
            msg = random.choice(chat_lst)
            return msg
        except:
            logging.exception("")
        return None

    def get_random_speak(self):
        for _ in range(10):
            c = self.random_chat()
            if c is None:
                return ""

            msg = c.get("content", "")
            if len(msg) > 30:
                continue
            if msg.startswith("!") or msg.startswith("！"):
                continue

            return msg
            
        return ""



if __name__ == "__main__":
    b = chatHandler()
    # b.collect_chat2redis()
    # b.random_chat()
    print(b.get_random_speak())
