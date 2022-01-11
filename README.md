## interbotAPI  
#### python3+go-cqhttp+api的QQBot  
  

## 构成
#### main2cq.py
```
# 使用cqhttp-api的ip端口
bot = CQHttp(api_root='http://127.0.0.1:5700/')
# 消息转发地址
centerURL = 'http://inter1.com/center/msg'

# 接收cqhttp的ip端口
def wsgiMain():
    bot.run(host='0.0.0.0', port=8887)
    
# 独立实现的ws，提供额外功能
ser = websockets.serve(wsMain, '0.0.0.0', 12345)
```

专门对接cqhttp，作为第一层转接点，做收发处理
1. 同步处理: 将消息分发到msgCenter后同步返回结果，功能单一  
2. 异步处理: 提供额外cqapi的功能，由websocket封装，可外部主动发起  

   
#### itb.sh 

用于启动服务的简易框架启动脚本  
```
sh itb.sh msgCenter1 start|stop|restart
```

#### main.py  

flask服务启动入口，根据```itb.sh```参数传入解析```app/msgCenter.yaml```  
```
msgCenter1:
  name: msgCenterApi
  version: v0.1
  listen: 10001
  comment: 消息处理api
  model: msgCenter
```
model指定app/msgCenter.py，flask服务入口文件  

#### app/demo.py
```
from flask import Flask

@app.route('/test')
def test():
    return 'suc'

if __name__ == '__main__':
    app.run(threaded=True)
```

#### msgCenter 

消息处理中心，专注消息本身  
由mariadb配置命令与路由，对接功能服务api  

1. 命令抽取,路由转发
2. 权限控制,黑白名单处理
3. at与私聊自动格式转换
4. 交互式命令处理



## api与配置
#### 功能api 
- itb方式的flask服务 

  按照```main.py```的规则实现   

- 自由接入方式

  实现提供http接口的服务即可,cmdRef配置路由  

#### 配置命令

经过msgCenter的功能都需要在mariadb的osu2库```cmdRef```表配置  


| id | cmd | url | location | reply | at | level | toprivate |
| :-----| :----- | :----- | :----- | :----- | :----- | :----- | :----- |
| 1 | hello |  |  | hello | 1 | 1 |   |   |
| 2 | !rctpp | /xxxx | http://inter4.com/xxxx | 最近游戏记录,需要绑定  | 1 | 1 |   | 
| 3 | !setid | /xxxx | http://inter4.com/xxxx | 绑定 用法：!setid，链接认证  | 1 | 1 | 1 |  
| 4 | !mybp | /xxxx | http://inter4.com/xxxx | bp查询 用法：!mybp num  | 1 | 1 |   |   
| 5 | !bbp | /xxxx | http://inter4.com/xxxx | bp简化输出,需绑定  |   | 1 |   |   
| 6 | !test | /xxxx | http://inter4.com/xxxx | osu账号评分  |   | 1 |   |   
| 7 | !skill | /xxxx | http://inter4.com/xxxx | osuskill站点信息  |   | 1 |   |   
| 8 | !todaybp | /xxxx | http://inter4.com/xxxx | 今日更新bp  |   | 1 |   |   
| 9 | !mu | /xxxx | http://inter4.com/xxxx | 主页链接  |   | 1 |   |   
| 10 | !check | /xxxx | http://inter4.com/xxxx | 来自薛定谔的pp  |   | 1 |   |   
| 11 | !vssk | /xxxx | http://inter4.com/xxxx | skill pk  |   | 1 |   |   
| 12 | !oauth | /xxxx | http://inter4.com/xxxx | osu apiv2 绑定  |  1 | 1 |   |   
| 13 | !friends | /xxxx | http://inter4.com/xxxx | 好友列表  |  1 | 1 |   |   
| 14 | !nbp | /xxxx | http://inter4.com/xxxx | 输入bid得到bp几  |  1 | 1 |   |   
| 15 | !rl | /xxxx | http://inter1.com/xxxx | 排名变化曲线  |    | 1 |   |   
| 16 | !pc | /xxxx | http://inter1.com/xxxx | 游玩次数变化曲线  |    | 1 |   |   
| 17 | !rctpps | /xxxx | http://inter4.com/xxxx | 批量版rctpp   |  1  |  |   |   
| 18 | !stat | /xxxx | http://inter4.com/xxxx | 新版osu个人信息   |  1  |  |   |   
| 19 | !map | /xxxx | http://inter4.com/xxxx | 低端pp图推荐   |  1  |  |   |   
| 20 | !oldsetid | /xxxx | http://inter4.com/xxxx | 绑定osu信息   |  1  |  |   |   
| 21 | !days | /xxxx | http://inter4.com/xxxx | 增长数据查询   |     | 1 |   |   
| 22 | !bd | /xxxx | http://inter4.com/xxxx | 榜单查询 bd bid   |     | 1 |   |   
| 23 | !mt | /xxxx | http://inter4.com/xxxx | 随机摸图 mt 4 6 5(星数,星数,条数)   |     | 1 |   |   


| 字段 | 说明 | 备注 | 
| :-----| :----- | :----- |
| cmd | 命令，以!开头为功能命令，非!开头为普通命令 | 不支持中文 |
| url | 功能命令转发地址 location+url |  |
| location | 功能命令转发地址 location+url |  |
| reply | 非功能命令，直接返回reply |  |
| at | 自动拼接上@xxx  | 1-开启 |
| level | 自动构建到help指定列表 | 1-开启 |
| toprivate | 自动转私聊 | 1-开启 |
| interactive | 交互式命令标志 | 1-开启 |




## 其他  

热寂的QQ群: 863935563  

