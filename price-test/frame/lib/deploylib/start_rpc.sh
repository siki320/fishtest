#!/bin/bash

kill_rpyc_server()
{
    local rpyc_server_fd=`ps aux|grep -E "rpyc_classic.py|classic_server.py"|grep -v "grep"|awk '{print $2}'`
    rpyc_server_fd_array=($rpyc_server_fd)
    rpyc_fd_num=${#rpyc_server_fd_array[@]}
    max_idx=`expr $rpyc_fd_num - 1`
    if [ $max_idx -le -1 ];then
        echo "No RPyC server need to kill"
    else
        for i in `seq 0 $max_idx`
        do
            if [ ${rpyc_server_fd_array[$i]} ];then
                 kill -9 ${rpyc_server_fd_array[$i]}
                 sleep 2
            fi
         done
    fi
    local check_prc=`ps aux|grep -E "rpyc_classic.py | classic_server.py"|grep -v "grep"|awk '{print $2}'`
    if [ ${check_prc} ];then
         echo "WARNING, RPYC server kill failed! try again!"
         kill -9 ${check_prc}
    else
         echo "RPyC server killed sucessfully!"
    fi
}

DFT_PORT=60778
DFT_MOD=1
#rpyc3.2.1��classicĿ¼�仯��servers-->scripts
RPYC_SERVER_PATH=~/.XDS_CLIENT/frame/lib/thirdlib/rpyc/scripts

if [ $# -lt 1 ];then
    port=${DFT_PORT}
    mod=${DFT_MOD}
elif [ $# -lt 2 ];then
    port=$1
    mod=${DFT_MOD}
else
    port=$1
    mod=$2
    PYTHON_PATH=$3
    RPYC_SERVER_PATH=~/$PYTHON_PATH/frame/lib/thirdlib/rpyc/scripts
fi

#echo "Killing RPyC server..."
#kill_rpyc_server
#killall -9 wget
sleep 3
source ~/.bash_profile
#no need install python and rpyc
export PYTHONPATH=~/$PYTHON_PATH/frame/tools/python27/lib:~/$PYTHON_PATH/frame/lib/thirdlib:$PYTHONPATH
export PATH=~/$PYTHON_PATH/frame/tools/python27/bin:$PATH

echo "Starting RPyC server..."
#�ж�rpyc�Ƿ�������ͨ���˿��ж�
echo "First check if RPyC port ${DFT_PORT} is open ..."
echo q | telnet -eq localhost ${DFT_PORT} 1>/dev/null 2>/dev/null
if [ $? -eq 0 ]; then
    echo "RPyC server is already start!"
    exit 0
fi

if [ ${mod} -eq 1 ];then
    python ${RPYC_SERVER_PATH}/rpyc_classic.py -m forking -p ${DFT_PORT}
else
    #rpyc3.2.1������ʽ�仯��classic server���ļ����Ʊ仯��classic_server.py --> rypc_classic.py
    #�����仯��3.2.1Ĭ���Է�ע�᷽ʽ���������������ټӲ���--dont-register
    nohup python ${RPYC_SERVER_PATH}/rpyc_classic.py -m forking -p ${DFT_PORT} </dev/null &> /dev/null &
    #nohup python ${RPYC_SERVER_PATH}/classic_server.py -m forking --dont-register -p ${DFT_PORT} </dev/null &> /dev/null &
    
    #�ж�rpyc�Ƿ�������ͨ���˿��ж�
    echo q | telnet -eq localhost ${DFT_PORT} 1>/dev/null 2>/dev/null
    rpyc_started=$?
    timeout=0
    while [ $rpyc_started -ne 0 ]
    do
        sleep 1
        let timeout=$timeout+1
        #��ȴ�10s
        if [ $timeout -eq 10 ]; then
            echo "FATAL: RPyC server start failed!"
            exit 1
        fi
        echo q | telnet -eq localhost ${DFT_PORT} 1>/dev/null 2>/dev/null
        rpyc_started=$?
    done
    echo "RPyC server start successfully!"
    exit 0
fi
