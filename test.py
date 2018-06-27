#coding:utf8
import json
import requests

centerURL = 'http://118.24.91.98/center/msg'

context = {'anonymous': None, 'font': 75020424, 'group_id': 514661057, 'message': '!args a b -at', 'message_id': 72849, 'message_type': 'group', 'post_type'
: 'message', 'raw_message': '!args a b -at', 'self_id': 2680306741, 'sub_type': 'normal', 'time': 1530099122, 'user_id': 405622418}

res = requests.post(centerURL, data={"context": json.dumps(context)})

print(res.text)
