# -*- coding: utf-8 -*-
import logging
import random
from commLib import Config
from commLib import pushTools


def entry(context):
    """语音姬
    """
    # 已被提供者收回！
    return

    if context['message_type'] != 'group':
        return

    msg = context['message']
    msg = msg.replace('！', '!')
    qq = context['user_id']
    groupid = context['group_id']

    audioFile = None
    pushMsg = None

    if msg == '!语音姬':
        pushMsg = audio_help()

    elif msg == '快卖萌':
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
        elif msg == 'interbot快叫醒她':
            audioFile = 'exclusive_inter.wav'

    # dalou彩蛋
    elif qq == 1061566571:
        if '穷' in msg or '钱' in msg:
            audioFile = 'daloumoneyjp.mp3'

    if audioFile:
        pushMsg = Config.audioTmp % audioFile

    if pushMsg:
        pushTools.pushMsgOne(groupid, pushMsg)


def audio_help():
    msg = 'interbot 语音姬v1.1\n'
    msg += '目前支持指令:\n'
    msg += '---------------------\n'
    msg += '1.一抹多(4)\n'
    msg += '2.¡sleep(2)\n'
    msg += '3.快卖萌(7)\n'
    msg += '4.早安(1)\n'
    msg += '5.隐藏彩蛋\n'
    msg += '6.rctpp部分评价\n'
    msg += '*新增个人专属彩蛋\n'
    msg += '---------------------\n'
    msg += '(音源提供者:- Se Tsu Nya -)'
    return msg
