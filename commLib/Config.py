# -*- coding: utf-8 -*-

# 超级权限
SUPER_QQ = 405622418

# 语音模板
audioTmp = '[CQ:record,file=http://interbot.cn/itbaudio/%s]'

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
    "XINRENQUN": 885984366 # osu新人群
}