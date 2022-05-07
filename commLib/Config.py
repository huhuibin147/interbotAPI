# -*- coding: utf-8 -*-

# 超级权限
SUPER_QQ = 405622418
BOT_QQ = 2680306741

# 语音模板
audioTmp = '[CQ:record,file=http://interbot.cn/itbaudio/%s]'
bg_thumb = '[CQ:image,cache=0,file=https://b.ppy.sh/thumb/{sid}l.jpg]'
ImgTmp = '[CQ:image,cache=0,file=http://interbot.cn/itbimage/%s]'

sayo_down_api = 'https://dl.sayobot.cn/beatmaps/download/novideo/{sid}'

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
PP_TOOLS_PATH = '/root/code/osu-tools/PerformanceCalculator/bin/Debug/net5.0'

XINRENQUN = 712603531 # osu新人群
JINJIEQUN = 928936255 # osu进阶群
HOUHUAYUAN = 514661057 # osu后花园

GROUPID = {
    "XINRENQUN": XINRENQUN,
    "JINJIEQUN": JINJIEQUN,
    "test": 619786604
}

# 群ID
GROUP_IRC = {'1':614892339,'2':514661057,'3':641236878,'4':758120648}

# ChatCache
CHAT_RANDOM_KEY = "CHAT_RANDOM_KEY"

# 回复概率数 0~100
AUTOREPLY_PCT = 99
# 自动触发speak概率数 0~100
AUTOSPEAK_PCT = 99
# 复读概率数 0~100
AUTOREPEAT_PCT = 99

USERLIST_FILE = "botappLib/userlist.json"
MATCHLIST_FILE = "botappLib/matchlist.json"

#oauth cache
OAUTH_CACHE_KEY = "oauth_verify_{qq}_{gid}"
