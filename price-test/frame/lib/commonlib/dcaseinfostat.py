# -*- coding: GB18030 -*-
'''
Created on May 12, 2012

@author: liqiuhua

@summary: statistics dts case information
'''
import sys
import os
import re
from getopt import getopt, GetoptError
from frame.tools.lib.mysqldb import MySQLdb
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.dtssystem2 import dtssystem_out
from frame.lib.controllib.result import DResult
VERSION = "1.0.0"

class DtestInfoStat(object):
    """ stat dts case infomation """
    def __init__(self, host, port, user, passwd):
        self.host = host
        self.user = user
        self.port = port
        self.passwd = passwd
        self.__case_num = 0      # case num
        self.__test_num = 0      # test num 
        self.__func_cov_rate   = 0.0 # function coverage
        self.__branch_cov_rate = 0.0 # branch coverage
        self.__product_line = "" # production line name
        self.__module_name  = "" # production line name
        self.__dbname = "dts_info_stat"

    def set_moduleinfo(self, modulename, productline):
        """
        @summary: set module name and product line
        @param modulename: module name
        @param productline: product line 
        """
        self.__product_line = productline
        self.__module_name  = modulename

    def set_casetestnum(self, casenum, testnum):
        """
        @summary: set the case num
        @param casenum: case num
        @param testnum: test num
        """
        self.__case_num = casenum
        self.__test_num = testnum

    def set_coverage(self, func_cov_rate, branch_cov_rate):
        """
        @summary: set the coverage information
        @param casenum: set function coverate
        @param testnum: test num
        """
        self.__func_cov_rate = func_cov_rate
        self.__branch_cov_rate = branch_cov_rate

    def set_dts_info(self, product_line, module_name, casenum=0, testnum=0, func_cov_rate=0.0, branch_cov_rate=0.0, dtestresult=None, covfile=""):
        """
        @summary: set the dts case information
        """
        return #do not record the case runing record
        if covfile != "" and os.path.exists(covfile):
            ret=dtssystem_out("covsrc -f %s"%covfile)
            output = ret[1]
            ma = re.search("Total\s+\d+\s*/\s*\d+\s*=\s*(\d+)%\s+\d+\s*/\s*\d+\s*=\s*(\d+)%",output)
            if ma:
                func_cov_rate = float(ma.group(1))/100
                branch_cov_rate = float(ma.group(2))/100
            else:
                dlog.warning("cannot parse cov file:%s",covfile)
        if dtestresult != None:
            casenum = dtestresult.get_casenum()
            testnum = dtestresult._get_testnum()

        self.set_moduleinfo(module_name, product_line)
        self.set_casetestnum(casenum, testnum)
        self.set_coverage(func_cov_rate, branch_cov_rate)
        self.save()

    def save(self):
        """
        @summary: set the dts case information
        """
        if self.__product_line == "" or self.__module_name == "":
            raise Exception, "product line or module name is null"
        conn = MySQLdb.connect(host=self.host,user=self.user, port=self.port, passwd=self.passwd,db=self.__dbname)
        cursor = conn.cursor()
        dlog.info("upload data to dashboard. product_line:%s, module_name:%s, casenum:%d, testnum:%d, fun_cov:%0.2f%s, branch_cov:%0.2f%s",self.__product_line,self.__module_name,self.__case_num,self.__test_num,self.__func_cov_rate*100,"%",self.__branch_cov_rate*100,"%")
        ret=cursor.execute("INSERT INTO dts_info (product_line, module_name, casenum, testnum, func_cov, branch_cov) VALUES (\"%s\", \"%s\", %d, %d, %f,%f)"\
            %(self.__product_line,self.__module_name,self.__case_num,self.__test_num,self.__func_cov_rate,self.__branch_cov_rate))
        if ret==False:
            dlog.error("cannot upload data to dashboard. please contact liqiuhua")
        #cursor.execute("select * from dts_info")
        #print cursor.fetchall()
        cursor.close() 
        conn.close()
        #print conn

    def __init_database__(self):
        conn = MySQLdb.connect(host=self.host,user=self.user, port=self.port, passwd=self.passwd, db=self.__dbname) 
        cursor=conn.cursor()
        cursor.execute("create TABLE dts_info (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, product_line VARCHAR(100), module_name VARCHAR(50), casenum INT, testnum INT, func_cov FLOAT, branch_cov FLOAT, cur_timestamp TIMESTAMP(8))") 
        cursor.close() 
        conn.close()

dcaseinfostat = DtestInfoStat(host="10.237.2.72", user="root", port=3606, passwd="MhxzKhl")

def help():
    print "python dcaseinfostat.py [option]"
    print "record the dts case infomation into database"
    print "       -h, --help                    help"
    print "       -v, --version                 version"
    print "       --product_line=product        产品线名称"
    print "       --module_name=module          模块名称"
    print "       --casenum=casenum             case数量"
    print "       --testnum=totaltestnum        testfunction数量"
    print "       --func_cov=func_cov_rate      函数覆盖率"
    print "       --branch_cov=branch_cov_rate  分支覆盖率"
    print "       --covfile=test.cov            ccov覆盖率文件"

def version():
    print VERSION

if __name__=="__main__":

    # 读取命令行参数
    try:
        opts, args = getopt(sys.argv[1:],
                            "vh",
                            ["casenum=",
                             "testnum=",
                             "product_line=",
                             "module_name=",
                             "func_cov=",
                             "branch_cov=",
                             "covfile=",
                             "version",
                             "help"
                             ])
    except GetoptError:
        dlog.critical("Get options failed. Process suicide", exc_info=True)
        print
        help()
        sys.exit(-1)

    casenum=0
    testnum=0
    product_line=""
    module_name=""
    func_cov_rate=0.0
    branch_cov_rate=0.0
    covfile=""
    # 根据opts设置picker, suite, dlog属性
    for opt in opts:
        if opt[0] == "--casenum":
           casenum=int(opt[1]) 

        if opt[0] == "--testnum":
           testnum=int(opt[1])

        if opt[0] == "--product_line":
           product_line=opt[1]

        if opt[0] == "--module_name":
           module_name=opt[1]

        if opt[0] == "--func_cov":
           func_cov_rate=float(opt[1])

        if opt[0] == "--branch_cov":
           branch_cov_rate=float(opt[1])
    
        if opt[0] == "--covfile":
           covfile=opt[1]

        if opt[0] == "-h" or opt[0] == "--help":
           help()
           exit(0)

        if opt[0] == "-v" or opt[0] == "--version":
           version()
           exit(0)

    dcaseinfostat.set_dts_info(product_line,module_name, casenum, testnum, func_cov_rate, branch_cov_rate, dtestresult=None, covfile=covfile)
    dcaseinfostat.save()
