#!/bin/bash




checkalive() {
    #echo $1
    lines=`ps axu|grep "python3 main.py $1"|wc -l`
    if [ "2" -ne $lines ]; then
        #echo $lines
        sh itb.sh $1 restart
    fi
} 


checkalive $1
