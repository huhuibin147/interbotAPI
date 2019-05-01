#!/bin/bash

appdir=`pwd`

start(){
    checklogdir
    nohup python3 main2cq.py  >> $appdir/var/log/main2cq.log 2>&1 &
    echo "main2cq start..."
}

stop(){
    ps aux|grep python|grep main2cq.py|awk '{print $2}'|xargs kill
    echo "main2cq stop..."
}

restart(){
    stop 
    start 
}

checklogdir(){
    if [ ! -d "$appdir/var/log" ];then
        mkdir -p $appdir/var/log
    fi
}



if [ $# = 1 ]
then
    case "$1" in 
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
    esac
else
    echo "Usage:"    
    echo " sh main2cq.sh start|stop|restart"
fi
