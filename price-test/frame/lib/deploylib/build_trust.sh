#!/bin/bash
# Created on: Mar 15, 2012
# Author: caiyifeng@baidu.com

#-------------------------------------------------------------------------------
#	�����Է����Լ������ι�ϵ
#	$0 [--force] host username passwd
#
#   �������ι�ϵ�ɹ�����0�����ɹ�����1
#   --forceʱ�����ɹ����ɾ��ԭ�����ι�ϵ���ؽ�
#-------------------------------------------------------------------------------

function get_authorized_keys(){
	# ��ȡ�Է������ϵ�authorized_keys�ļ�
	$sshpass -p $passwd scp $username@$host:.ssh/authorized_keys .
	
	# �����ȡʧ�ܣ�����authorized_keys�ļ�
	if [ $? -ne 0 ]; then
		touch authorized_keys
	fi
	
	# ���Է�ԭ�����Լ������ι�ϵɾ��
	sed -i "/$USER@$HOSTNAME/ d" authorized_keys
}

function check_dsa_key(){
	# �������������ʱ��ɾ��id_dsa������ؽ�id_dsa��
	# 1. id_dsa.pub������
	# 2. id_dsa�����룬������δ֪
	
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
	# ����Կд��authorized_keys�ļ�
	cat ~/.ssh/id_dsa.pub >> authorized_keys
	
	# ��authorized_keys�ļ����ضԷ�����
	$sshpass -p $passwd ssh $username@$host "mkdir -p .ssh"
	$sshpass -p $passwd scp authorized_keys $username@$host:.ssh
	
	# �޸�Զ���ļ���Ȩ��
	# ԭ�����http://recursive-design.com/blog/2010/09/14/ssh-authentication-refused/
	$sshpass -p $passwd ssh $username@$host "
chmod g-w .
chmod 700 .ssh
chmod 600 .ssh/authorized_keys"
	
	# ɾ��authorized_keys�ļ�
	rm authorized_keys
}

function main(){
	# �õ�һ���ɾ���authorized_keys
	get_authorized_keys
	
	# ���id_dsa�ĺϷ���
	check_dsa_key
	
	# ������Կ�ԣ�ֻ��id_dsa������ʱ�ؽ���
	echo "n" | ssh-keygen -t dsa -f ~/.ssh/id_dsa -N ''
	echo
	
	# ����Կд��
	send_back
}

function test_trust(){
	# ���sshȨ���Ƿ����ɹ�
	# ͬʱ����known_hosts
	ssh -o BatchMode=yes -o StrictHostKeyChecking=no $username@$host "true"
	return $?
}


# ========= �ű���ʼ =========

# ��λsshpass����
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


# ����Ƿ��Ѿ������ι�ϵ��
test_trust
if [ $? -eq 0 ]; then
	echo "[Succeed] Already has ssh authority. Quit"
	exit 0
fi

# ���߼�
main

# ����Ƿ����ɹ�
test_trust
if [ $? -eq 0 ]; then
	echo "[Succeed] Create ssh authority done"
	exit 0
elif [ $force -eq 0 ]; then
	# ����������
	echo "[Error] Failed to create ssh authority"
	exit 1
fi

# û�гɹ���������Ҫ��������
echo "[Warning] Create ssh authority failed, force to REMOVE id_dsa and retry"
rm -f ~/.ssh/id_dsa
	
main
	
# ������Ƿ�ɹ�
test_trust
if [ $? -eq 0 ]; then
	echo "[Succeed] Create ssh authority done"
	exit 0
else
	echo "[Error] Failed to create ssh authority"
	exit 1
fi

