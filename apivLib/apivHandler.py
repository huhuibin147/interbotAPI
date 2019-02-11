# -*- coding: utf-8 -*-
import logging
import traceback
import requests
import json
from commLib import interMysql
from ppyappLib import ppyHandler

class apivHandler():


    def __init__(self):
        self.client_secret = "46SmWQ2TyF5FMECwHrblTZ2oiYq4yyAbOH5BDDS7"
        self.client_id = "19"
    
    def userOauth(self, code, state):
        """转化code到token后绑定
        """
        access_token, refresh_token = self.getTokenByAuthCode(code)
        if access_token == -1:
            return -1
        qq, groupid = state.split('x')
        ret = self.udpateUserToken(qq, groupid, access_token, refresh_token)
        return ret
    
    def newUserOauth(self, code, state):
        """转化code到token后绑定，再做一次信息绑定
        Returns:
            -1 调用ppy异常
            -2 数据库操作异常
        """
        access_token, refresh_token = self.getTokenByAuthCode(code)
        if access_token == -1:
            return -1
        qq, groupid = state.split('x')
        rs = self.chenckAndudpateUserToken(qq, groupid, access_token, refresh_token)
        if rs == -1:
            return -2
        elif rs == -2:
            return -1
        return True

    def getTokenByAuthCode(self, code):
        """取得token
        """
        apiUrl = "https://osu.ppy.sh/oauth/token"
        params = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code
        }
        rs = requests.post(apiUrl, params)

        if rs.status_code == 200:
            logging.info('调用[%s]成功！' % (apiUrl))
            data = json.loads(rs.text)
            logging.info('api:https://osu.ppy.sh/oauth/token, data:%s', data)
            if data.get("error"):
                return -1, -1

            token_type = data.get('token_type')
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            return access_token, refresh_token

        else:
            logging.info('调用[%s]异常，rs:%s' % (apiUrl, rs.text))
            return -1, -1


    def udpateUserToken(self, qq, gourpid, access_token, refresh_token):
        """绑定token
        """
        db = interMysql.Connect('osu2')
        sql = '''
            UPDATE user 
            SET acesstoken = %s, refreshtoken = %s
            WHERE qq = %s and groupid = %s
        '''
        args = [access_token, refresh_token, qq, gourpid]
        ret = db.execute(sql, args)
        db.commit()
        return ret

    def chenckAndudpateUserToken(self, qq, groupid, access_token, refresh_token):
        """检查加绑定操作
        Returns:
            -1 数据库操作异常
            -2 v2信息获取失败
        """
        db = interMysql.Connect('osu2')
        checkSql = '''
            SELECT 1 FROM user WHERE qq=%s and groupid=%s
        '''
        checkArgs = [qq, groupid]
        checkRet = db.query(checkSql, checkArgs)
        if not checkRet:
            rs = self.insertUser(qq, groupid)
            if not rs:
                return -1

        # 取一次用户信息
        b = ppyHandler.ppyHandler()
        status, ret = b.autov2Req2(qq, groupid, "me", access_token, refresh_token)
        if status < 0:
            return -2

        osuid = ret["id"]
        osuname = ret["username"]

        # 批量更新操作
        upRet = self.udpateUsersInfo(qq, access_token, refresh_token, osuid, osuname)
        if upRet < 0:
            return -1
        return 1


    def insertUser(self, qq, groupid):
        """插入空记录
        """
        db = interMysql.Connect('osu2')
        sql = '''
            INSERT into user(qq, groupid) values(%s, %s)
        '''
        args = [qq, groupid]
        ret = db.execute(sql, args)
        db.commit()
        if ret < 1:
            return False
        else:
            return True


    def udpateUsersInfo(self, qq, access_token, refresh_token, osuid, osuname):
        """批量更新用户信息
        """
        db = interMysql.Connect('osu2')
        sql = '''
            UPDATE user 
            SET acesstoken = %s, refreshtoken = %s,
                osuid = %s, osuname = %s
            WHERE qq = %s
        '''
        args = [access_token, refresh_token, osuid, osuname, qq]
        ret = db.execute(sql, args)
        db.commit()
        return ret


