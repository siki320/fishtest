#!/bin/bash
PWD=`pwd`
workpath=$PWD
datafile="log"
test_path="/home/xiaoju/ENV/canal_test"
base_path="/home/xiaoju/ENV/canal_base"
canal_test_path="/home/xiaoju/ENV/diff_canal"
redis_path="/home/xiaoju/redis/"
redis0_file="/home/xiaoju/redis/redis6380.conf"
redis1_file="/home/xiaoju/redis/redis6381.conf"

if [ ! -d "$datafile" ];then
    mkdir $datafile
fi

if [ $# != 1 ];then
    echo "Usage: $0 [all|get_feature_count|get_range|get_discount|get_time_info]"
    exit 1
fi

function steplog(){
    echo "---------------------"
    echo " $1"
    echo "---------------------"
}

function init_env(){
    rm -f $test_path/log/*
    cd $test_path/conf/ && cp $1 canal.conf && cd -
    rm -f $base_path/log/*
    cd $base_path/conf/ && cp $1 canal.conf && cd -
}

function generate_report(){
    steplog "g_report"
}

function checkENV()
{
    if [ ! -d $redis_path ]
    then
        echo "wrong redis path,please move redis to path: $redis_path"
    else
        echo "redis_path checked"
    fi
    if [ ! -f $redis0_file ]
    then
        echo "redis conf file not exist,please make sure redis6380.conf under path: $redis_path"
    else
        echo "redis_port_6380 conf file checked"
    fi
    if [ ! -f $redis1_file ]
    then
        echo "redis conf file not exist,please make sure redis6381.conf under path: $redis_path"
    else
        echo "redis_port_6381 checked"
    fi
    if [ ! -d $base_path ]
    then
        echo "wrong code path,please move master code to path: $base_path"
    else
        echo "master path checked"
    fi
    if [ ! -d $test_path ]
    then
        echo "wrong code path,please move branch code to path: $test_path"
    else
        echo "branch path checked"
    fi

}
function checkRedis0()
{
    num=`netstat -tnpl |grep redis |grep 6380 | grep -v grep |wc -l`
    if [ $num -eq 0 ]
    then
        echo "redis is not running!"
         cd ${redis_path}
         nohup bin/redis-server redis6380.conf dev/null 2>&1 &
    fi
}

function checkRedis1()
{
    num=`netstat -tnpl |grep redis |grep 6381 | grep -v grep |wc -l`
    if [ $num -eq 0 ]
    then
        echo "redis is not running!"
         cd ${redis_path};
         nohup bin/redis-server redis6381.conf >>/dev/null 2>&1 &
    fi
}
function checkCanal(){
    num=`netstat -tnpl|grep canal -c`
    if [ $num -eq 0 ];then
        echo "stream-canal is not running"
        cd ${base_path}; nohup bin/canal >>/dev/null 2>&1 &
        cd ${test_path}; nohup bin/canal >>/dev/null 2>&1 &

    else
        stopCanal
        cd ${base_path}; nohup bin/canal >>/dev/null 2>&1 &
        cd ${test_path}; nohup bin/canal >>/dev/null 2>&1 &
    fi
}

function stopCanal(){
    PROCESS=`netstat -anlp| grep canal |awk '{print $7}'|awk -F '/' '{print $1}'`
    echo `ps -ef|grep canal|grep -v grep|grep -v PPID`
    for i in $PROCESS
    do
        kill -9 $i
    done
}

function diff_test(){
    checkENV
    init_env canal.conf.test
    nohup sh $canal_test_path/bin/updateconf.sh >std 2>err & 
    checkRedis0
    checkRedis1
    checkCanal
    sleep 5
    sh $canal_test_path/bin/Server_input.sh $1
}

case $1 in
        "get_feature_count" | "get_range" | "get_discount" | "get_time_info" | "all" )
        steplog "CANAL_CHECK_DIFF_START interface : $1"
        diff_test $1 
        steplog "CANAL_CHECK_DIFF_STOP interface ：$1"
        ;;
    *)
        echo "please input get_feature_count | get_range | get_discount | get_time_info | all"
        ;;
    esac
