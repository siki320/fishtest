#!/bin/bash
# Created on: Oct 29, 2012
# Author: geshijing@baidu.com

#-------------------------------------------------------------------------------
#	在已经建立好信任关系的机器之间同步文件夹
#	
#
#   建立信任关系成功返回0，不成功返回1
#   --force时，不成功后会删除原有信任关系并重建
#-------------------------------------------------------------------------------

function main(){
    echo "rsync -a -r  $force $src_path $dest_usr@$dest_host:$dest_path"
    rsync -a -r $force $src_path $dest_usr@$dest_host:$dest_path
    if [ $? -ne 0 ]; then
	    echo "[Failed] Failed to sync file"
	    exit 1
    fi
}

function test_trust(){
	# 检查ssh权限是否建立成功
	# 同时更新known_hosts
	ssh -o BatchMode=yes -o StrictHostKeyChecking=no $dest_usr@$dest_host "true"
	return $?
}


# ========= 脚本开始 =========

# 定位rsync命令,暂时默认所有机器都有装rsync

#rsync="$(dirname "$0")"/rsync
src_path='.'
dest_host='127.0.0.1'
dest_usr='work'
dest_path='~/tmp'
force=' '

while getopts "fs:d:u:r:h" arg #选项后面的冒号表示该选项需要参数
do
    case $arg in
        s)
            echo "src folder is $OPTARG"
            src_path=$OPTARG
            ;;
        
        d)
            echo "dest_host is $OPTARG "
            dest_host=$OPTARG
            ;;
        
        u)
            echo "user_name is $OPTARG "
            dest_usr=$OPTARG
            ;;
        
        r)
            echo "remote_path is $OPTARG "
            dest_path=$OPTARG
            ;;
        
        f)
            echo "force to delete remote files" #参数存在$OPTARG中
            force=' --delete '
            ;;
        
        h) 
            echo "$0 [-f ] -s src_paht -d dest_name -u user_name -r remote_path "
            exit 0
            ;;
        ?)  #当有不认识的选项的时候arg为?
            echo "unkonw argument"
            exit 1
            ;;
    esac
done

# 检查是否已经有信任关系了
test_trust
if [ $? -ne 0 ]; then
	echo "[Failed] You need to build trust before sync folder. Quit"
	exit 1
fi

# 主逻辑
main


