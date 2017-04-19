#!/bin/bash
# Created on: Mar 15, 2012
# Author: caiyifeng@baidu.com

#-------------------------------------------------------------------------------
#	建立对方对自己的信任关系
#	$0 [--force] host username passwd
#
#   建立信任关系成功返回0，不成功返回1
#   --force时，不成功后会删除原有信任关系并重建
#-------------------------------------------------------------------------------

function get_authorized_keys(){
	# 获取对方机器上的authorized_keys文件
	$sshpass -p $passwd scp $username@$host:.ssh/authorized_keys .
	
	# 如果获取失败，创建authorized_keys文件
	if [ $? -ne 0 ]; then
		touch authorized_keys
	fi
	
	# 将对方原来对自己的信任关系删除
	sed -i "/$USER@$HOSTNAME/ d" authorized_keys
}

function check_dsa_key(){
	# 当以下情况发生时，删除id_dsa（随后重建id_dsa）
	# 1. id_dsa.pub不存在
	# 2. id_dsa有密码，且密码未知
	
	if [ ! -s ~/.ssh/id_dsa ]; then
		return
	fi
	
	if [ ! -s ~/.ssh/id_dsa.pub ]; then
		echo "[Info] id_dsa.pub not exist. so REMOVE id_dsa"
		rm -f ~/.ssh/id_dsa
		return
	fi
		
	ssh-keygen -p -P "" -N "" -f ~/.ssh/id_dsa
	if [ $? -ne 0 ]; then
		echo "[Info] Unknown id_dsa passphrase, REMOVE it"
		rm -f ~/.ssh/id_dsa
		return
	fi
}

function send_back(){
	# 将公钥写入authorized_keys文件
	cat ~/.ssh/id_dsa.pub >> authorized_keys
	
	# 将authorized_keys文件传回对方机器
	$sshpass -p $passwd ssh $username@$host "mkdir -p .ssh"
	$sshpass -p $passwd scp authorized_keys $username@$host:.ssh
	
	# 修改远程文件夹权限
	# 原因见：http://recursive-design.com/blog/2010/09/14/ssh-authentication-refused/
	$sshpass -p $passwd ssh $username@$host "
chmod g-w .
chmod 700 .ssh
chmod 600 .ssh/authorized_keys"
	
	# 删除authorized_keys文件
	rm authorized_keys
}

function main(){
	# 得到一个干净的authorized_keys
	get_authorized_keys
	
	# 检查id_dsa的合法性
	check_dsa_key
	
	# 创建密钥对（只在id_dsa不存在时重建）
	echo "n" | ssh-keygen -t dsa -f ~/.ssh/id_dsa -N ''
	echo
	
	# 将公钥写回
	send_back
}

function test_trust(){
	# 检查ssh权限是否建立成功
	# 同时更新known_hosts
	ssh -o BatchMode=yes -o StrictHostKeyChecking=no $username@$host "true"
	return $?
}


# ========= 脚本开始 =========

# 定位sshpass命令
sshpass="$(dirname "$0")"/sshpass

# validate args
if [ "$1" == "--force" ]; then
	force=1
	shift
else
	force=0
fi

if [ $# -ne 3 ]; then
	echo "[Error] argument count invalid"
	echo "$0 [--force] host username passwd"
	echo "caiyifeng@baidu.com"
	exit 1
fi

host=$1
username=$2
passwd=$3

# check current folder
if [ -e authorized_keys ]; then
	rm authorized_keys
	echo "[Warning] current folder mustn't have authorized_keys, rm it!!"
fi


# 检查是否已经有信任关系了
test_trust
if [ $? -eq 0 ]; then
	echo "[Succeed] Already has ssh authority. Quit"
	exit 0
fi

# 主逻辑
main

# 检查是否建立成功
test_trust
if [ $? -eq 0 ]; then
	echo "[Succeed] Create ssh authority done"
	exit 0
elif [ $force -eq 0 ]; then
	# 不暴力重试
	echo "[Error] Failed to create ssh authority"
	exit 1
fi

# 没有成功，而且需要暴力重试
echo "[Warning] Create ssh authority failed, force to REMOVE id_dsa and retry"
rm -f ~/.ssh/id_dsa
	
main
	
# 最后检查是否成功
test_trust
if [ $? -eq 0 ]; then
	echo "[Succeed] Create ssh authority done"
	exit 0
else
	echo "[Error] Failed to create ssh authority"
	exit 1
fi

