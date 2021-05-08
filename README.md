# interbotAPI<br>
## 简介
python3+go-cqhttp+api模式的QQBot<br>

## 整体结构
* **main2cq** <br> 
　　专门对接cqhttp，作为第一层转接点，做收发处理<br>
　　　　同步处理<br>
　　　　　　将消息分发到msgCenter后同步返回结果，功能单一<br>
　　　　异步处理<br>
　　　　　　提供额外cqapi的功能，由websocket封装，可外部主动发起<br>
   
* **msgCenter** <br> 
　　消息处理中心，专注消息本身<br>
　　　　由mariadb配置命令与路由，对接功能服务api<br>
　　　　内置功能<br>
　　　　　　命令抽取,路由转发<br>
　　　　　　权限控制,黑白名单处理<br>
　　　　　　at与私聊自动格式转换<br>
   
* **itb.sh** <br>
　　用于启动服务的简易框架启动脚本<br>

## 开发方式
* itb方式的flask服务<br>
　　此方式则需要遵循固定规则<br>
　　app目录下启动入口,xxx.py+xxx.yaml<br>
　　xxx需要同名,yaml做端口配置<br>

* 自由接入方式<br>
　　实现提供http接口的服务即可<br>

* 配置命令<br>
　　在mariadb中配置,cmdRef <br>


------

热寂的QQ群: 863935563  <br>

