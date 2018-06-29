# -*- coding: utf-8 -*-
import logging

from commLib import interMysql

class baseHandler():


    def __init__(self):
        pass

    def getUserBindInfo(self, kvWhere):
        """用户绑定
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



    