#!/bin/bash




checkalive() {
    #echo $1
    lines=`ps axu|grep "python3 main.py $1"|grep -v grep|wc -l`
    if [ "1" -ne $lines ]; then
        #echo $lines
        sh itb.sh $1 restart
    fi
} 


checkalive $1
