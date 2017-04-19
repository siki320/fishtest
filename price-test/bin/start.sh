#!/bin/bash
#encoding=UTF-8
set -x
source /home/xiaoju/.bash_profile
FileRunPath=`dirname $0`
redis_path=/home/xiaoju/redis/
run_env_path=/home/xiaoju/ENV/dups_price
test_path=/home/xiaoju/ENV/dups_price/price_test
#检查redis
function checkRedis()
{
    num=`netstat -tnpl |grep redis |grep 6379 | grep -v grep |wc -l`
    if [ $num -eq 0 ]
    then
        echo "redis is not running!"
         ./$redis_path/redis-server ../redis6379.conf
        /home/xiaoju/redis/bin/redis-cli -p 6381 flushdb
    else
        /home/xiaoju/redis/bin/redis-cli -p 6379 flushdb
    fi
}
#检查rt
function checkRT()
{
    num=`netstat -tnpl |grep rt-simple |grep 11311 | grep -v grep |wc -l`
    if [ $num -eq 0 ]
    then
        echo "rt-simple is not running!"
       
    fi
}
#check price
function checkPrice(){
    num=`netstat -tnpl|grep price -c`

    if [ $num -eq 0 ];then
        echo "service price is not running"
        startPrice
    fi
}

function startPrice(){
    numhttp=`netstat -tnpl | grep price | grep 9002 -c `
    numthrift=`netstat -tnpl | grep price | grep 9000 -c `
    numcoupon=`netstat -tnpl | grep price | grep 9001 -c `
    if [ $numhttp -ne 0 ] || [ $numthrift -ne 0 ] || [numcoupon -ne 0];then
        echo "port occupied,9000 {status:$numthrift},9001 {status:$numcoupon},9002 {status:$numhttp}"
    else
	rm -rf $run_env_path/log/*
        nohup $run_env_path/bin/price >>/dev/null 2>&1 &
    fi
}

function stopPrice(){
    PROCESS=`netstat -anlp| grep  price | grep 9000 |awk '{print $7}'|awk -F '/' '{print $1}'`
    echo `ps -ef|grep price|grep -v grep|grep -v PPID`
    for i in $PROCESS
    do
        echo "Kill the price process [ $i ]"
        kill -9 $i
    done
}
function change_conf(){
    sed -i '/gomonitor/s/true/false/' $1
    sed -i 's/127.0.0.1:6379/127.0.0.1:6381/g' $1
}

cd ${test_path}
rm -rf _log/*
if [ $# -eq 2 ];then
    casepath=$1
    mode=$2
else
    casepath=`cat ${test_path}/dir.txt | awk -F = '{print $2}'`
fi
cd $test_path
\cp -r -f 6 {&run_env_path}/data/
checkRedis
checkRT
checkPrice

sh init_env.sh && source ./source_me.sh

result=`dat mytest/dups-price/Pricetest.py`

mv _log/result.txt _log/result.json

if [ "$result" != "0" ]; then
    exit 1
fi
exit 0
