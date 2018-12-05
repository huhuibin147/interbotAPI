# -*- coding: utf-8 -*-
import logging
import random
from commLib import Config
from commLib import pushTools


def entry(context):
    """语音姬
    """
    if context['message_type'] != 'group':
        return

    msg = context['message']
    msg = msg.replace('！', '!')
    qq = context['user_id']
    groupid = context['group_id']

    audioFile = None
    if msg == '快卖萌':
        n = random.randint(1, 7)
        audioFile = 'maimen%s.wav' % n
    elif msg == '一抹多':
        n = random.randint(1, 4)
        audioFile = 'meikong%s.wav' % n
    elif msg == '!sleep':
        n = random.randint(1, 2)
        audioFile = 'wanan%s.wav' % n
    elif msg == '早安':
        audioFile = 'zaoan.wav'
    elif msg == '喵':
        audioFile = 'maimen1.wav'
    elif msg == 'wululu':
        audioFile = 'maimen2.wav'
    elif msg == 'kuma':
        audioFile = 'maimen3.wav'
    elif msg == 'inter在吗':
        audioFile = 'maimen4.wav'
    elif msg == '摸摸inter':
        audioFile = 'maimen5.wav'
    elif msg == 'inter唱歌':
        audioFile = 'maimen6.wav'
    elif msg == 'baka':
        audioFile = 'maimen7.wav'
    elif msg == 'dalou!':
        audioFile = 'daloumoneycn.mp3'

    elif qq == Config.SUPER_QQ:
        if msg == 'interbot快叫dalou还钱':
            audioFile = 'daloumoneyjp.mp3'

    # dalou彩蛋
    elif qq == 1061566571:
        if '穷' in msg or '钱' in msg:
            audioFile = 'daloumoneyjp.mp3'

    if audioFile:
        pushMsg = Config.audioTmp % audioFile
        pushTools.pushMsgOne(groupid, pushMsg)