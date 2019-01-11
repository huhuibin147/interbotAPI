# -*- coding: utf-8 -*-
import re
import json
import logging
import requests
import threading
from commLib import interMysql
from commLib import pushTools

class msgHandler():

    def __init__(self, context):
        self.context = context
        self.isPrivate = 0

    def auto(self):
        """消息处理"""

        # 分发线程
        t = threading.Thread(target=self.msgTransmit, args=(self.context, ))
        t.start()

        # 兼容私聊
        if self.context['message_type'] == 'private':
            self.isPrivate = 1
            self.context['group_id'] = -1

        # 自动处理
        msg = self.context['message']
        msg = msg.replace('！', '!')
        if '!' in msg:
            return self.autoApi(msg)
        else:
            return self.autoReply(msg)

    def msgTransmit(self, context):
        """消息转发"""
        url = 'http://inter1.com/defindapp/defindmsg'
        requests.post(url, data={"context": json.dumps(context)})

    def checkPermission(self, cmd):
        """权限控制
        Type:
            ptype 1-无限制 2-白 3-黑
        Return:
            state, remark
            -1 限制
            1  通过
        """
        permissionRs = self.getPermission(cmd)
        if not permissionRs:
            logging.info('[%s]未设置权限,无法使用!', cmd)
            return -1, '' 

        for permission in permissionRs:
            ptype = permission['ptype']
            groupid = permission['groupid']
            gtype = permission['gtype']

            if ptype == 1:
                pass
            elif ptype == 2:
                s, r = self.checkWhitePermission(groupid, gtype)
                if s < 0:
                    return s, r
            elif ptype == 3:
                s, r =  self.checkBalckPermission(groupid, gtype)
                if s < 0:
                    return s, r
            else:
                logging.info('[%s]未知类型错误', cmd)
                return -1, ''

        return 1, '无限制'

    def autoApi(self, msg):
        """api检测，自动调用"""
        cmd = self.extractCmd(msg)
        res = self.getCmdRef(cmd)
        if not res:
            return ''

        # 权限控制
        s, r = self.checkPermission(cmd)
        if s < 0:
            return r

        # 帮助选项
        if '*h' in msg or not res['location']:
            return res['reply']

        apiUrl = '{location}{api}'.format(
                location = res['location'],
                api = res['url']
            )

        # 参数提取
        iargs = self.extractArgs(msg, cmd)
        # 选项提取
        opts = self.extractOptions(msg)
        atqq = self.extractAtqqid(msg)

        # 配置回复选项
        if res['at']:
            opts.append('*at')

        if res['toprivate']:
            opts.append('*toprivate')

        # 调用核心 
        res = requests.post(
            apiUrl, 
            data = {
                "iargs": json.dumps(iargs),
                "qqid": self.context['user_id'],
                "groupid": self.context['group_id'],
                "atqq": atqq
            }
        )
        if res.status_code == 200 and res.text:
            return self.returnHandler(res.text, opts, self.context)
        logging.info('调用[%s]异常' % apiUrl)
        return ''
        
    def extractAtqqid(self, msg):
        """at提取"""
        p = re.compile('\[CQ:at,qq=(\d+)\]')
        qqs = p.findall(msg)
        qq = ''
        if qqs:
            qq = qqs[0]
        logging.info('提取的Atqq:%s', qq)
        return qq


    def returnHandler(self, res, opts, context):
        """转发封装 带上选项"""
        returnstr = ''
        if '*at' in opts:
            qq = context['user_id']
            returnstr = ''
            returnstr += '[CQ:at,qq=%s] ' % (qq)
            if len(res) > 20:
                returnstr += '\n'
            returnstr += str(res)
        elif '*toprivate' in opts:
            context["message_type"] = "private"
            pushTools.pushMsgOnePrivate(context['user_id'], res)
        else:
            returnstr = res
        
        return returnstr

    def extractArgs(self, msg, cmd):
        """参数提取
        Retruns:
            x
        """
        args = []
        if '*r' not in msg:
            msgf = self.filterOptions(msg)
        else:
            msgf = msg.replace('*r', '')
        effmsg = msgf[msgf.find(cmd):]
        l = effmsg.split(' ')
        if len(l) > 1:
            args = l[1:]
        args = list(filter(lambda x: x != '', args))
        return args

    def extractOptions(self, msg):
        """选项提取"""
        p = re.compile('\*\w+')
        opts = p.findall(msg)
        logging.info('提取的opts:%s', opts)
        return opts

    def filterOptions(self, msg):
        """选项过滤"""
        return re.sub('\*\w+', '', msg)

    def autoReply(self, msg):
        """自动回复，非特殊指令性"""
        retmsg = ''
        fmsg = self.filterCN(msg)
        fmsg = fmsg.replace(' ', '')
        if len(msg) == len(fmsg):
            res = self.getCmdRef(fmsg)
            if res:
                state, remark = self.checkPermission(fmsg)
                if state > 0:
                    retmsg = res['reply']
                else:
                    retmsg = remark
        return retmsg

    def extractCmd(self, msg):
        """命令提取"""
        retcmd = None
        p = re.compile(r'!\w+')
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
            SELECT cmd, url, location, reply, at, toprivate
            FROM cmdRef WHERE cmd = %s
        '''
        res = db.query(sql, [cmd])
        if not res:
            return ''
        return res[0]

    def getPermission(self, cmd):
        """权限查询"""
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT ptype, cmd, groupid, gtype
            FROM permission WHERE cmd = %s
        '''
        res = db.query(sql, [cmd])
        if not res:
            return []
        return res

    def checkWhitePermission(self, groupid, gtype):
        """白名单处理 存在放行
        Type:
            1-用户 2-群
        """
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT gid, remark
            FROM pmsGroup WHERE gid = %s
            AND account = %s
        '''
        if gtype == 1:
            account = self.context['user_id']
        else:
            account = self.context['group_id']
        args = [groupid, account]
        res = db.query(sql, args)
        if not res:
            logging.info('[%s]不在白名单范围内', account)
            return -1, ''

        return 1, res[0]['remark']

    def checkBalckPermission(self, groupid, gtype):
        """黑名单处理 不存在放行
        Type:
            1-用户 2-群
        """
        db = interMysql.Connect('osu2')
        sql = '''
            SELECT gid, remark
            FROM pmsGroup WHERE gid = %s
            AND account = %s
        '''
        if gtype == 1:
            account = self.context['user_id']
        else:
            account = self.context['group_id']
        args = [groupid, account]
        res = db.query(sql, args)
        if not res:
            return 1, '不在黑名单范围内'

        logging.info('[%s]权限限制,在黑名单范围内', account)
        return -1, ''

    
