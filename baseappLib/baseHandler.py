# -*- coding: utf-8 -*-
import json
import logging
import requests

from commLib import cmdRouter
from commLib import interMysql
from commLib import interRedis
from chatbotLib import testc

class baseHandler():


    def __init__(self):
        pass

    def getUserBindInfo(self, kvWhere):
        """取用户绑定信息
        Args:
            kvWhere 条件  k-v形式
        Returns:
            xxx
        """
        db = interMysql.Connect('osu2')
        sql = '''SELECT id, qq, osuid,
                        groupid, osuname
                FROM user
                WHERE 1=1
            '''
        args = []
        for k,v in kvWhere.items():
            sql += 'and {0}={1}'.format(k, '%s')
            args.append(v)
        ret = db.query(sql, args)
        if not ret:
            return ret
        logging.info('触发用户绑定查询ret:%s', ret)
        return ret

    def bindOsuUser(self, osuid, qq, groupid):
        """用户绑定
        Args:
            osuid id/name
        Return:
            1  成功
            0  重复
            -1 异常
            -2 请求api异常
        """
        ret = cmdRouter.invoke('!osuerinfo', {"osuid": osuid})
        uinfo = json.loads(ret)
        if not uinfo:
            return -2
        r = self.user2DB(qq, uinfo[0]['user_id'], groupid, uinfo[0]['username'])
        return r
    
    def user2DB(self, qq, osuid, groupid, osuname, name=None):
        try:
            conn = interMysql.Connect('osu2')
            sql = '''
                insert into user
                    (qq, osuid, name, groupid, osuname) 
                values
                    (%s,%s,%s,%s,%s)
                on duplicate key update
                    osuid = %s, osuname = %s, name = %s
            '''
            args = [qq, osuid, name, groupid, osuname, osuid, osuname, name]
            ret = conn.execute(sql, args)
            logging.info('qq[%s],gid[%s],user2DB ret:%s', qq, groupid, ret)
            if ret:
                conn.commit()
            return ret
        except:
            logging.error('用户[%s]插入/更新失败', qq, traceback.print_exc())
            conn.rollback()
            return -1

    def recordRecMap(self, qqid, groupid):
        """开启记录推荐消息标记
        """
        rds = interRedis.connect('osu2')
        k = 'RECORD_MAP:{groupid}:{qqid}'.format(groupid=groupid, qqid=qqid)
        if rds.exists(k):
            return -1
        rds.setex(k, 1, 3600)
        return 1

    def stopRecordRecMap(self, qqid, groupid):
        """结束记录推荐消息标记，请求打包api
        """
        rds = interRedis.connect('osu2')
        k = 'RECORD_MAP:{groupid}:{qqid}'.format(groupid=groupid, qqid=qqid)
        k2 = 'RECORD_MAPLIST:{groupid}:{qqid}'.format(groupid=groupid, qqid=qqid)
        # 取图链拼装请求
        bids = rds.lrange(k2, 0, -1)
        if not bids:
            return -1
        args = ','.join(bids)
        rs = self.getMapTarDownLink(args)
        if rs:
            rds.delete(k)
            rds.delete(k2)
        
        return rs

    def recordRecMapList(self, qqid, groupid):
        """查询推荐列表
        """
        rds = interRedis.connect('osu2')
        k = 'RECORD_MAPLIST:{groupid}:{qqid}'.format(groupid=groupid, qqid=qqid)
        if not rds.exists(k):
            return -1
        r = rds.lrange(k, 0, -1)
        return r

    def getMapTarDownLink(self, args):
        """打包下载，返回链接
        """
        url = 'http://interbot.club/osu3/downmap?bids=%s' % args
        res = requests.get(url)
        if res.status_code == 200:
            return res.text
        else:
            logging.info('请求[%s]下载异常', url)
        return ''

    def chat2bot(self, inputs):
        """对话系统
        """
        ans = testc.getAnswer(inputs) 
        if ans.strip() == '':
            ans = '本bot还没学会怎么回答这鬼问题!'
        return ans