# -*- coding: GB18030 -*-
'''
Created on june 12, 2012

@author: liqiuhua<liqiuhua>

@summary: 合并dts结果文件
'''
import re
import os
import sys

from frame.lib.commonlib.timer import Timer
from frame.lib.controllib.result import DResult
from frame.lib.controllib.report import DtestReport
from frame.lib.commonlib.dtssystem import dtssystem
from frame.lib.commonlib.relpath import get_relpath


class MergeResult(object):
    def __init__(self):
        self.report = DtestReport()
        self.result = DResult(report=self.report)
        pass

    def read_casedir(self, casedir):
        """
        @summary 读取result目录文件，合并结果
        """
        files = os.listdir(casedir)
        casedir = casedir.rstrip('/')
        for f in files:
            if(os.path.isdir(casedir + '/' + f)):
                if (f[0]== '.' or f=='..'):
                    continue
                else:
                    self.read_casedir(casedir + '/' + f)
            if(os.path.isfile(casedir + '/' + f)):
                if f == "result.txt":
                    self.read_result(casedir + '/' + f)

    def read_result(self, resultfile):
        rf = file(resultfile)
        for line in rf:
            line = line.rstrip()
            ma = re.match("(.*?case.*?\.py)\t(\w+)\t.*?\t(\d+)",line)
            if ma:
                cr = DResult.CaseResult(DResult.PASS,"","")
                if ma.group(2) == "P":
                    cr.result = DResult.PASS 
                elif ma.group(2) == "Failed":
                    cr.result = DResult.FAILED
                else:
                    cr.result = DResult.SKIP
                case_name = ma.group(1).split('case/')[1]
                self.result.case_result_dict[case_name] = cr
                t = Timer()
                t.totaltime = float(ma.group(3))/1000
                self.result.case_time_dict[case_name] = t
                continue
            ma = re.match("(.*?test\S+)\t(\w+)", line)
            if ma:
                tr = DResult.TestResult(None, DResult.PASS)
                if ma.group(2) == "P":
                    tr.result = DResult.PASS
                elif ma.group(2) == "Failed":
                    tr.result = DResult.FAILED
                else:
                    tr.result = DResult.SKIP
                cr.test_result_dict[ma.group(1)] = tr
        rf.close()

    def merge_screen(self, casedir, screen_file):
        pass

    def merge_log(self, casedir, log_path):
        log = file(log_path+"/im_cts.log","w")
        logwf = file(log_path+"/im_cts.log.wf","a")
        files = os.listdir(casedir)
        casedir = casedir.rstrip('/')
        for f in files:
            if(os.path.isdir(casedir + '/' + f)):
                if (f[0]== '.' or f=='..'):
                    continue
                else:
                    self.merge_log(casedir + '/' + f, log_path)
            if(os.path.isfile(casedir + '/' + f)):
                if f == "im_cts.log":
                    tf = file(casedir + '/' + f)
                    log.write(tf.read())
                    tf.close
                if f == "im_cts.log.wf":
                    tf = file(casedir + '/' + f)
                    logwf.write(tf.read())
                    tf.close
        log.flush()
        logwf.flush()
        log.close()
        logwf.close()

    def gen_failcase(self):
        dtssystem("rm -rf fail_case")
        if self.result.get_total_result() == True:
            return
        dtssystem("mkdir -p fail_case")
        for case in self.result.case_result_dict:
            cr = self.result.case_result_dict[case]
            if cr.result==DResult.FAILED:
                rel_path = get_relpath(case)
                dirpath = os.path.dirname(rel_path)
                dirpath = re.sub("^case/","",dirpath)
                dtssystem("mkdir -p fail_case/%s"%dirpath)
                dtssystem("cp %s fail_case/%s"%(case,dirpath))
            
                    
if __name__ == "__main__":
    me = MergeResult()
    #group = sys.argv[1]
    #module = sys.argv[2]
    me.read_casedir("result/stdout/case")
    me.result.log_case_summary("log/result.txt")
    #data_request = data_opera.gen_timedata('log/result.txt', group, module)
    #data_opera.write_data(data_request)
    me.result.gen_mail_report("log/report_FT.html","test")
    os.system("echo >log/im_cts.log")
    os.system("echo >log/im_cts.log.wf")
    me.merge_log("result/stdout/AllCases_Execution_Logs","log")
    me.gen_failcase()
    if me.result.get_total_result() == False:
        exit(1)
