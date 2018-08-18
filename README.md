# interbotAPI<br>
## 1、简介
**基于微服务思想由API为核心的，基于python3+酷Q+httpAPI的QQBot**<br>


## 2、构成
* **main2cq** <br> 
处理消息的接收，分发，返回；分发往指定消息中心msgCenter，返回分http同步返回和异步websocket返回<br>
* **msgCenter** <br> 
消息处理中心：命令自动转发，对接相应的服务，内置权限控制，命令以及选项自动提取<br>
* **itb.sh** 《br>
用于启动服务的简易框架启动脚本

## 3、编写方法
* app+yaml，flask形式的服务
* 配置命令与路由，使用mariadb
* 新增节点需要做从库，用于自动路由

<br><br>
*开发群：863935563
