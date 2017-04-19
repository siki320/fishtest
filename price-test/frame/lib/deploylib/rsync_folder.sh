#!/bin/bash
# Created on: Oct 29, 2012
# Author: geshijing@baidu.com

#-------------------------------------------------------------------------------
#	���Ѿ����������ι�ϵ�Ļ���֮��ͬ���ļ���
#	
#
#   �������ι�ϵ�ɹ�����0�����ɹ�����1
#   --forceʱ�����ɹ����ɾ��ԭ�����ι�ϵ���ؽ�
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
	# ���sshȨ���Ƿ����ɹ�
	# ͬʱ����known_hosts
	ssh -o BatchMode=yes -o StrictHostKeyChecking=no $dest_usr@$dest_host "true"
	return $?
}


# ========= �ű���ʼ =========

# ��λrsync����,��ʱĬ�����л�������װrsync

#rsync="$(dirname "$0")"/rsync
src_path='.'
dest_host='127.0.0.1'
dest_usr='work'
dest_path='~/tmp'
force=' '

while getopts "fs:d:u:r:h" arg #ѡ������ð�ű�ʾ��ѡ����Ҫ����
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
            echo "force to delete remote files" #��������$OPTARG��
            force=' --delete '
            ;;
        
        h) 
            echo "$0 [-f ] -s src_paht -d dest_name -u user_name -r remote_path "
            exit 0
            ;;
        ?)  #���в���ʶ��ѡ���ʱ��argΪ?
            echo "unkonw argument"
            exit 1
            ;;
    esac
done

# ����Ƿ��Ѿ������ι�ϵ��
test_trust
if [ $? -ne 0 ]; then
	echo "[Failed] You need to build trust before sync folder. Quit"
	exit 1
fi

# ���߼�
main


