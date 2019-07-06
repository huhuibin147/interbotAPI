#!/bin/bash




checkalive() {
    #echo $1
    lines=`tail "var/log/sitb.$1.log"|grep skipped|wc -l`
    if [ $lines -gt "0" ]; then
        # echo $lines
        sh sitb.sh $1 restart
    fi

    lines=`ps axu|grep "python3 job/jobCenter.py $1"|grep -v grep|wc -l`
    if [ "1" -ne $lines ]; then
        #echo $lines
        sh sitb.sh $1 restart
    fi
} 


checkalive $1

