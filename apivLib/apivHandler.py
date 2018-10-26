# -*- coding: utf-8 -*-
import logging
import traceback
import requests
import json
from commLib import interMysql

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
