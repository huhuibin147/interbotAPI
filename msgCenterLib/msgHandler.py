# -*- coding: utf-8 -*-
import re
import json
import logging
import requests
from commLib import interMysql

class msgHandler():

    def __init__(self, context):
        self.context = context

    def auto(self):
        msg = self.context['message']
        msg = msg.replace('！', '!')
        if '!' in msg:
            return self.autoApi(msg)
        else:
            return self.autoReply(msg)

    def autoApi(self, msg):
        """api检测，自动调用"""
        cmd = self.extractCmd(msg)
        res = self.getCmdRef(cmd)
        if not res:
            return ''

        # 帮助选项
        if '-h' in msg:
            return res['reply']

        apiUrl = '{location}{api}'.format(
                location = res['location'],
                api = res['url']
            )

        # 参数提取
        iargs = self.extractArgs(msg, cmd)
        # 选项提取
        opts = self.extractOptions(msg)

        # 调用核心 
        res = requests.post(
            apiUrl, 
            data = {
                "iargs": json.dumps(iargs),
                "qqid": self.context['user_id'],
                "groupid": self.context['group_id']
            }
        )
        if res.status_code == 200 and res.text:
            return self.returnHandler(res.text, opts, self.context)
        logging.info('调用[%s]异常' % apiUrl)
        return ''
        
    def returnHandler(self, res, opts, context):
        """转发封装 带上选项"""
        returnstr = ''
        if '-at' in opts:
            qq = context['user_id']
            returnstr = '[CQ:at,qq=%s] %s' % (qq, res)
        else:
            returnstr = res
        return returnstr

    def extractArgs(self, msg, cmd):
        """参数提取
        Retruns:
            x
        """
        args = []
        msgf = self.filterOptions(msg)
        effmsg = msgf[msgf.find(cmd):]
        l = effmsg.split(' ')
        if len(l) > 1:
            args = l[1:]
        args = list(filter(lambda x: x != '', args))
        return args

    def extractOptions(self, msg):
        """选项提取"""
        p = re.compile('-\w+')
        opts = p.findall(msg)
        logging.info('提取的opts:%s', opts)
        return opts

    def filterOptions(self, msg):
        """选项过滤"""
        return re.sub('-\w+', '', msg)

    def autoReply(self, msg):
        """自动回复，非特殊指令性"""
        retmsg = ''
        fmsg = self.filterCN(msg)
        fmsg = fmsg.replace(' ', '')
        if len(msg) == len(fmsg):
            res = self.getCmdRef(fmsg)
            if res:
                retmsg = res['reply']
        return retmsg

    def extractCmd(self, msg):
        """命令提取"""
        retcmd = None
        p = re.compile('!\w+')
        cmds = p.findall(msg)
        if cmds:
            retcmd = cmds[0]
        logging.info('提取的cmd[%s]', retcmd)
        return retcmd

    def filterCN(self, content):
        """过滤中文"""
        pat = re.compile('[\u4e00-\u9fa5]')
        ret = pat.sub('', content)
        return ret

    def getCmdRef(self, cmd):
        """映射"""
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT cmd, url, location, reply
            FROM cmdRef WHERE cmd = %s
        '''
        res = db.query(sql, [cmd])
        if not res:
            return ''
        return res[0]
