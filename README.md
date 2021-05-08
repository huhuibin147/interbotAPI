## interbotAPI  
#### python3+go-cqhttp+api模式的QQBot  
  

## 构成
#### main2cq

专门对接cqhttp，作为第一层转接点，做收发处理  
1. 同步处理: 将消息分发到msgCenter后同步返回结果，功能单一  
2. 异步处理: 提供额外cqapi的功能，由websocket封装，可外部主动发起  
   
#### msgCenter 

消息处理中心，专注消息本身  
由mariadb配置命令与路由，对接功能服务api  
内置功能: 
1. 命令抽取,路由转发
2. 权限控制,黑白名单处理
3. at与私聊自动格式转换
   
#### itb.sh 

用于启动服务的简易框架启动脚本  

## 开发方式
#### itb方式的flask服务 

此方式则需要遵循固定规则  
app目录下启动入口,xxx.py+xxx.yaml  
xxx需要同名,yaml做端口配置  

#### 自由接入方式

实现提供http接口的服务即可  

#### 配置命令

在mariadb中配置,cmdRef  

  
  

热寂的QQ群: 863935563  

