#coding:utf8
import sys
import json
import requests


centerURL = 'http://inter1.com/center/msg'

msg = '!rank'

if len(sys.argv) > 1:
    msg = sys.argv[1]

context = {'anonymous': None, 'font': 75020424, 'group_id':641236878 , 'message': msg, 'message_id': 72849, 'message_type': 'group', 'post_type'
: 'message', 'raw_message': msg, 'self_id': 2680306741, 'sub_type': 'normal', 'time': 1530099122, 'user_id': 405622418}

res = requests.post(centerURL, data={"context": json.dumps(context)})

print(res.text)
