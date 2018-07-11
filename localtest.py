#coding:utf8
import sys
import json
import requests


centerURL = 'http://127.0.0.1:10003/'

cmd = 'bp'

if len(sys.argv) > 1:
    msg = sys.argv[1]

data = {"qqid": "405622418","groupid":"614892339","osuid":"interbot"}
res = requests.post(centerURL+cmd, data=data)

print(res.text)
