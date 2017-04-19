# -*- coding: gb2312 -*- 

DETECT_WORD = "测试 程序"
MAX_QUERYWORD_LEN = 256

ACCOUNT_NAME_LEN = 32
TEMPLATE_NAME_LEN = 32
STRATEGY_NAME_LEN = 64

SITE_NAME_LEN = 64
BEFORE_URL_LEN = 256

COOKIE_SIZE = 64
URL_LEN = 1024

MAX_RESULT_ITEM = 100
US_RES_COUNT = 100

MAX_DI3_SIZE = 640
MAX_DA_RESULT_NODE_NUM = 16;


BS_RTN_FILTER = -9
POLITICS_FILTER = -29
BS_RTN_PARSENULL = -10
RTN_GPSCHK_FILTER = -12
RTN_GPSCHK_OK = -13

BS_ABNORMAL = -1
DC_ABSTRACT_ERROR = -2
AC_ABNORMAL = -14
DI_ABNORMAL = -11

QUERY_SEX_MASK = 0x1000;
QUERY_POLICY_MASK = 0x2000;

#strategy int
RESULT_URL_MASK = 0x10;
RESULT_ZHIDA_MASK = 0x10000000;
RESULT_JIUCUO_MASK = 0x04000000;
RESULT_SITE_CLUSTER_MASK = 0x20000000;
RESULT_CONTENT_CLUSTER_MASK = 0x40000000;

#weight int
RESULT_SITE_DIR_MASK = 0x1000000;

WEIGHT_MASK = 0xFFFF;
MAX_WEIGHT = 15000;

AS_TITLE = 0 ;
AS_URL = 1; 
AS_LM = 2; 
AS_SIZE = 3; 
AS_CODE = 4; 
AS_DYNADJUST = 5; 
AS_SIGN = 6; 
AS_ABSTRACT = 7; 
AS_DI_FILD_NUM = 8;

MAX_DIINFO_SIZE = MAX_DI3_SIZE - 4*AS_DI_FILD_NUM;
#----------------------DICT-------------------#
AC_STATUS_STR_DICT = {
                 'BS_RTN_FILTER':-9,
                 'POLITICS_FILTER':-29,
                 'BS_RTN_PARSENULL':-10,
                 'RTN_GPSCHK_FILTER':-12,
                 'RTN_GPSCHK_OK':-13,
                 'BS_ABNORMAL':-1,
                 'DC_ABSTRACT_ERROR':-2,
                 'AC_ABNORMAL':-14,
                 'DI_ABNORMAL':-11,
                 'EMPTY':0
                 };

AC_STATUS_INT_DICT = {
                 -9:'BS_RTN_FILTER',
                 -29:'POLITICS_FILTER',
                 -10:'BS_RTN_PARSENULL',
                 -12:'RTN_GPSCHK_FILTER',
                 -13:'RTN_GPSCHK_OK',
                 -1:'BS_ABNORMAL',
                 -2:'DC_ABSTRACT_ERROR',
                 -14:'AC_ABNORMAL',
                 -11:'DI_ABNORMAL',
                 0  :'EMPTY'
                 };            

DA_COMMAND_INT_DICT = {
		 0x8:'DA_TIMERQT_COMMAND',
		 0x10:'DA_HILIGHT_COMMAND',
		 0x20:'DA_REQUIRE_COMMAND',
		 0x40:'DA_IP2LOCAL_COMMAND',
		 0x80:'DA_LOACA_EXTEND_COMMMAD',
		 0x8000000:'DA_TIMERQT_NEW_COMMAND'
		 };

DA_COMMAND_STR_DICT = {
		 'DA_TIMERQT_COMMAND':0x8,
		 'DA_HILIGHT_COMMAND':0x10,
		 'DA_REQUIRE_COMMAND':0x20,
		 'DA_IP2LOCAL_COMMAND':0x40,
		 'DA_LOACA_EXTEND_COMMMAD':0x80,
		 'DA_TIMERQT_NEW_COMMAND':0x8000000
		 };


SP_INT_DICT  = {
    1 : 'R_VDO',
    2 : 'MAP',
    3 : 'SP',
    4 : 'IMAGE',
    5 : 'SP',
    6 : 'C2C',
    7 : 'SP',
    8 : 'SP',
    9 : 'DICT',
    10: 'DICT',
    11: 'R_NEWS',
    12: 'KNOW'
};

AC_RESULT_FLAG = 1;
SP_RESULT_FLAG = 2;

US_ERROR_CODE_BEGIN = -99;

#----------------------OP --------------------#
AOS_OK=0;
AOS_ERR_FAILED_OPERATION=1;
AOS_ERR_STARTED=2;
AOS_ERR_NOT_STARTED=3;
AOS_ERR_TIMEOUT=4;
AOS_ERR_FILE_NOTFOUND=5;
AOS_ERR_ACCESS=6;
AOS_ERR_PARAMATER=7;
AOS_ERR_NOT_WORKING=8;

AOS_RETURN_CODE_LIST = [AOS_OK,
                        AOS_ERR_FAILED_OPERATION,
                        AOS_ERR_STARTED,
                        AOS_ERR_NOT_STARTED,
                        AOS_ERR_TIMEOUT,
                        AOS_ERR_FILE_NOTFOUND,
                        AOS_ERR_ACCESS,
                        AOS_ERR_PARAMATER,
                        AOS_ERR_NOT_WORKING];
                        
AOS_RETURN_CODE_DICT = {
    0 : 'AOS_OK',
    1 : 'AOS_ERR_FAILED_OPERATION',
    2 : 'AOS_ERR_STARTED',
    3 : 'AOS_ERR_NOT_STARTED',
    4 : 'AOS_ERR_TIMEOUT',
    5 : 'AOS_ERR_FILE_NOTFOUND',
    6 : 'AOS_ERR_ACCESS',
    7 : 'AOS_ERR_PAAMATER',
    8 : 'AOS_ERR_NOT_WORKING'
};


#----------------------DICT-------------------#     


#----------------------Other------------------#
