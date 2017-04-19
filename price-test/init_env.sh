#!/bin/bash
export WORK_PATH=`pwd`
#CONF_LOG_FILE="$WORK_PATH/_build_dat.log"

LOG_FATAL=1
LOG_WARNING=2
LOG_NOTICE=4
LOG_TRACE=8
LOG_DEBUG=16
LOG_LEVEL_TEXT=(
    [1]="FATAL  "
    [2]="WARNING"
    [4]="NOTICE "
    [8]="TRACE  "
    [16]="DEBUG  "
)

TTY_MODE_TEXT=(
    [1]="[FATAL  ]"
    [2]="[WARNING]"
    [4]="[NOTICE ]"
    [8]="[TRACE  ]"
    [16]="[DEBUG  ]"
)

#0  OFF  
#1  ������ʾ  
#4  underline  
#5  ��˸  
#7  ������ʾ  
#8  ���ɼ� 

#30  40  ��ɫ
#31  41  ��ɫ  
#32  42  ��ɫ  
#33  43  ��ɫ  
#34  44  ��ɫ  
#35  45  �Ϻ�ɫ  
#36  46  ����ɫ  
#37  47  ��ɫ 
TTY_MODE_COLOR=(
    [1]="1;31"
    [2]="1;33"
    [4]="0;32"
    [8]="1;33"
    [16]="1;35"
)

#exec shell command
#usage: exec_shell "make -C make" for test aa
##! @TODO: exec shell command
##! @AUTHOR: 
##! @VERSION: 1.0
##! @IN[string]: shell content
##! @RETURN: 0 => sucess; 1 => failure
function execshell()
{
    $@
    local ret=$?
    [ $ret -ne 0 ] && {
        Print $LOG_FATAL "$@ʧ��:return ${ret}"
        exit 1
    }
    return 0
}

##! @TODO: print info to tty & log file
##! @AUTHOR: 
##! @VERSION: 1.0
##! @IN[int]: $1 => tty mode
##! @IN[string]: $2 => message
##! @RETURN: 0 => sucess; 1 => failure
function Print()
{
    local tty_mode=$1
    local message="$2"
    local time=`date "+%m-%d %H:%M:%S"`
    if [ ${tty_mode} -le ${LOG_WARNING} ]
    then
        echo -e "\e[${TTY_MODE_COLOR[$tty_mode]}m${TTY_MODE_TEXT[$tty_mode]} ${message}\e[m" >&2
        #echo "${LOG_LEVEL_TEXT[$tty_mode]}: $time: ${MODULE_NAME} * $$ $message" #>> ${CONF_LOG_FILE}.wf
    else
        echo -e "\e[${TTY_MODE_COLOR[$tty_mode]}m${TTY_MODE_TEXT[$tty_mode]} ${message}\e[m" >&1
        #echo "${LOG_LEVEL_TEXT[$tty_mode]}: $time: ${MODULE_NAME} * $$ $message" #>> ${CONF_LOG_FILE}
    fi
    return $?
}

function build_datenv()
{
	Print $LOG_NOTICE "init test env start"
	cd ${WORK_PATH}
	{
		cd ${WORK_PATH}/../
		PROJECT_WORKSPACE=`pwd`
		python_bin_file=${PROJECT_WORKSPACE}/price-test/frame/tools/python27/bin/python2.7
		python_lib_path=${PROJECT_WORKSPACE}/price-test/frame/tools/python27/lib/
		dat_main_file=${PROJECT_WORKSPACE}/price-test/mytest/control/main.py
		#����source_me.sh
		env_file_name="${PROJECT_WORKSPACE}/price-test/source_me.sh"
		echo "function dat()" > ${env_file_name}
		echo "{" >> ${env_file_name}
#		echo "	${PROJECT_WORKSPACE}/dat/frame/tools/python27/bin/python $dat_main_file \"\$@\"" >> ${env_file_name}
 		echo "	python $dat_main_file \"\$@\"" >> ${env_file_name}
 		echo "    echo \$?" >> ${env_file_name}


		echo "}" >> ${env_file_name}
		#echo "export PYTHONPATH=${PROJECT_WORKSPACE}/LbsTest/:${PROJECT_WORKSPACE}/LbsTest/frame/lib/thirdlib" >> ${env_file_name}
		echo "export PYTHONPATH=${PROJECT_WORKSPACE}/price-test/:${PROJECT_WORKSPACE}/DupsTest/mytest/lib/test_common" >> ${env_file_name}
#		echo "export PATH=${PROJECT_WORKSPACE}/dat/frame/tools/python27/bin/:\$PATH" >> ${env_file_name}
		echo "export LD_LIBRARY_PATH=/usr/lib:${PROJECT_WORKSPACE}/price-test/frame/tools/python27/lib:\$LD_LIBRARY_PATH" >> ${env_file_name}
		echo "export LANG=en_US" >> ${env_file_name}
		echo "export LC_ALL=en_US" >> ${env_file_name}
		source ${PROJECT_WORKSPACE}/price-test/source_me.sh
	}
	cd ${WORK_PATH}
	Print $LOG_NOTICE "init test env end."
}

Main() 
{
	execshell "build_datenv"
}
Main "$@"

