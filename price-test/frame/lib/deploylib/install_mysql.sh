#!/bin/sh

DEST_PATH=$1
MYSQL_TAR_PATH=$2
TAR_FILE=$3
UNTAR_FILE=$4

if [ $# -ne 4 ]
then
	echo "Usage:" $0 "dest_path tar_path tar_file untar_file"
	exit 1
fi

if [ -d $MYSQL_TAR_PATH/$UNTAR_FILE ]
then
	if [ -d $DEST_PATH/bin ]
	then
		echo "mysql has been installed"
		exit 0
	fi
fi


if [ [-d $UNTAR_FILE ] -a  [ -d $DEST_PATH/bin ] ]
then
	echo "mysql has been installed"
	exit 0
fi

CURRENT_PWD=`pwd`

#拿到DEST_PATH的绝度路径，防止传入的是相对路径
cd $DEST_PATH && DEST_ABS_PATH=`pwd` && \
cd $CURRENT_PWD
if [ $? -ne 0 ]
then
	echo "get abs path of dest error" $0 " " $DEST_PATH " " $MYSQL_TAR_PATH " " $TAR_FILE " " $UNTAR_FILE
	exit 1
fi


#解压安装包
cd $MYSQL_TAR_PATH && tar -zvxf $TAR_FILE && \
cd $UNTAR_FILE && \
./configure '--prefix='$DEST_ABS_PATH '--with-unix-socket-path='$DEST_ABS_PATH'/var/mysql.sock' '--with-charset=gbk' '--with-extra-charsets=gb2312,utf8,binary,latin1' '--with-plugins=innodb_plugin,innobase' && \
make -j8 && make install
#
if [ $? -ne 0 ]
then
	echo "install mysql fail" $0 " " $DEST_PATH " " $MYSQL_TAR_PATH " " $TAR_FILE " " $UNTAR_FILE
	exit 1
fi

#进入安装完的数据库进行设置
cd $DEST_ABS_PATH && mkdir var && mkdir etc && \
cp share/mysql/my-medium.cnf etc/my.cnf && \
cp share/mysql/mysql.server ./ && \
./bin/mysql_install_db 
if [ $? -ne 0 ]
then
	echo "set mysql fail" $0 " " $DEST_PATH " " $MYSQL_TAR_PATH " " $TAR_FILE " " $UNTAR_FILE
	exit 1
fi

echo "install mysql successful"

cd $CURRENT_PWD

exit 0

