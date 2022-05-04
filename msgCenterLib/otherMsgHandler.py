# -*- coding: utf-8 -*-
import logging
from commLib import Config
from commLib import pushTools





class oMsgHandler():

    def __init__(self, context):
        self.context = context

    def main(self):
        rs = ""
        if self.context["post_type"] == "notice":
            self.noticeMsg()

        elif self.context["post_type"] == "request":
            self.requestMsg()

        return rs
    
    def noticeMsg(self):
        logging.info("noticenoticenoticenotice!!!!")
        # 群限制
        logging.info('self.context:%s', self.context)
        group_id = self.context["group_id"]
        if group_id not in list(Config.GROUPID.values()):
            return
        
        # 群员减少
        if self.context["notice_type"] == "group_decrease":
            self.group_decrease()

        # 群员增加
        elif self.context["notice_type"] == "group_increase":
            self.group_increase()

        return
    
    def requestMsg(self):
        logging.info("requestrequestrequestrequest!!!!")
        # 群限制
        logging.info('self.context:%s', self.context)
        group_id = self.context["group_id"]
        if group_id not in list(Config.GROUPID.values()):
            return
        # 加群处理
        if self.context.get("notice_type", "") == "request":
            if self.context["request_type"] == "group" and self.context["sub_type"] == "add":
                self.group_request()

        return

    def group_decrease(self):
        user_id = self.context["user_id"]
        sub_type = self.context["sub_type"]
        if sub_type == "leave":
            sub_c = "跑跑跑跑跑路了..."
        elif sub_type == "kick":
            sub_c = "被%s一脚踢飞了" % (self.context["operator_id"])

        msg = "%s%s" % (user_id, sub_c)
        pushTools.pushMsgOne(self.context["group_id"], msg)
    
    def group_increase(self):
        # 活动回流级别做提示
        msg = "欢迎！先仔细阅读公告！有问题找管理！"
        pushTools.pushMsgOne(self.context["group_id"], msg)

    def group_request(self):
        user_id = self.context["user_id"]
        flag = self.context["flag"]
        sub_type = self.context["sub_type"]
        approve = "true"
        if user_id in (405622418, ):
            pushTools.pushSetRequestCmd(flag, sub_type, approve)
