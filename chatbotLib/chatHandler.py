# -*- coding: utf-8 -*-
import sys
sys.path.append('./')

import re
import json
import random
import logging
import datetime
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

    def random_auotoreply_msg(self, pct=99):
        """概率随机
        触发则返回消息
        反之为空
        """
        if random.randint(0, 100) > pct:
            logging.info("触发自动回复！")
            return self.get_random_speak()
        return ""

    def check_whitelist(self, groupid, whites=[Config.XINRENQUN, Config.JINJIEQUN]):
        """白名单
        """
        if groupid in whites:
            return True
        return False
    
    def autoreply(self, groupid, qq, message, selfqq):
        """概率随机回复
        """
        # 白名单检测
        if not self.check_whitelist(groupid):
            return ""

        self.Chat2Redis(groupid, qq, message)
        # 防止重复
        if self.check_redis_is_selfchat(groupid, selfqq):
            return ""

        return self.random_auotoreply_msg(Config.AUTOREPLY_PCT)

    def msg2Mysql(self, groupid, qq, content):
        f_msg = re.sub('\[.*\]','',content)
        if not f_msg or f_msg == ' ' or len(f_msg) > 250:
            return
        self.Chat2DB(groupid, qq, f_msg)
        return

    def check_redis_is_selfchat(self, groupid, selfqq):
        """检测最后是不是自己消息
        """
        try:
            rds = interRedis.connect('osu2')
            key = 'chatlog_%s' % groupid
            chatlog = rds.get(key)
            chatlog = json.loads(chatlog) if chatlog else [{}]
            if int(chatlog[0].get('qq',0)) == selfqq:
                return True
        except:
            logging.exception("")
        return False

    def Chat2Redis(self, groupid, qq, message):
        try:
            rds = interRedis.connect('osu2')
            key = 'chatlog_%s' % groupid
            chatlog = rds.get(key)
            chatlog = json.loads(chatlog) if chatlog else []
            chat_msg = {'qq':qq, 'content':message, 
                        'time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            chatlog.insert(0, chat_msg)
            if len(chatlog) > 50:
                chatlog.pop()
            rds.set(key, json.dumps(chatlog))
        except:
            logging.exception("")
        return

    def Chat2DB(self, groupid, qq, content):
        try:
            conn = interMysql.Connect("osu")
            sql = '''
                INSERT INTO chat_logs (group_number,qq,content,create_time) 
                VALUES (%s, %s, %s, now())
            ''' 
            args = [groupid, qq, content]
            conn.execute(sql, args)  
            conn.commit() 
        except:
            conn.rollback()
            logging.exception("")
        return



if __name__ == "__main__":
    b = chatHandler()
    # b.collect_chat2redis()
    # b.random_chat()
    print(b.get_random_speak())
