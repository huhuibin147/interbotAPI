# -*- coding: utf-8 -*-

# 超级权限
SUPER_QQ = 405622418

# 语音模板
audioTmp = '[CQ:record,file=http://interbot.cn/itbaudio/%s]'
bg_thumb = '[CQ:image,cache=0,file=https://b.ppy.sh/thumb/{sid}l.jpg]'

# token权限
TOKEN_PERMISSION = {
    '0': "仅自己可用",
    '1': "仅供对比功能使用",
    '2': "开放给其他人查询"
}


TOKEN_PERMISSION_SELF = 0
TOKEN_PERMISSION_HALF = 1
TOKEN_PERMISSION_ALL = 2

# 命令步数KEY
CMDSTEP_KEY = 'CMDSTEP-{func}-{qq}-{groupid}'
CMDSTEP_KEY_EXPIRE_TIME = 86400

# 交互式命令集
FUNC_ACTIVE_KEY = 'FUNC-ACTIVE-{qq}-{groupid}'

# ppy-tools path
PP_TOOLS_PATH = '/root/code/netcoreapp2.0'

GROUPID = {
    "XINRENQUN": 712603531, # osu新人群
    "JINJIEQUN": 758120648, # osu进阶群
    "test": 619786604
}

# 群ID
GROUP_IRC = {'1':614892339,'2':514661057,'3':641236878,'4':758120648}