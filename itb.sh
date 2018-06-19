#!/bin/bash

appdir=`pwd`

start(){
    checklogdir
    #nohup python3 main.py $1 >/dev/null 2>itberror.log &
    nohup python3 main.py $1 >> $appdir/var/log/itb.$1.log 2>&1 &
    echo "$1 start..."
}

stop(){
    ps aux|grep python|grep $1|awk '{print $2}'|xargs kill
    echo "$1 stop..."
}

restart(){
    stop $1
    start $1
}

checklogdir(){
    if [ ! -d "$appdir/var/log" ];then
        mkdir -p $appdir/var/log
    fi
}



if [ $# = 2 ]
then
    case "$2" in 
        start)
            start $1
            ;;
        stop)
            stop $1
            ;;
        restart)
            restart $1
            ;;
    esac
else
    echo "Usage:"    
    echo " sh itb.sh <app> start|stop|restart"
fi