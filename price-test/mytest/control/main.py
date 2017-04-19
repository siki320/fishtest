# -*- coding: GB18030 -*-
'''
'''

import os
import sys
from getopt import getopt, GetoptError

from frame.lib.commonlib.dlog import dlog
from frame.lib.controllib.pickcase import CasePicker
from frame.lib.controllib.normal.normal_suite import NormalSuite
from frame.lib.controllib.result import DResult
from frame.lib.controllib.framemain import FrameMain
# from frame.lib.commonlib.dcaseinfostat import dcaseinfostat

#from sfserver.core.control.env_global import EnvGlobal

def main():
    # 初始化日志
    logdir = os.path.join(os.path.dirname(__file__), "../../_log/")
    dlog.init_logger(logdir+"/mycase.log")
    
    # 创建 Picker, Suite, Result 对象
    picker = CasePicker()
    suite = NormalSuite()
    result = DResult()
    
    # 读取命令行参数
    module_name=""
    covfile = ""
    try:
        opts, args = getopt(sys.argv[1:], 
                            "vhE", 
                            ["single", 
                             "ignore=", 
                             "weak", 
                             "tag=", 
                             "testname=", 
                             "module_name=",
                             "help"
                             ])
    except GetoptError:
        dlog.critical("Get options failed. Process suicide", exc_info=True)
        help()
        sys.exit(-1)
    # 根据opts设置picker, suite, dlog属性
    for opt in opts:
        if opt[0] == "--ignore":
            picker.read_ignore_list(opt[1])
            
        if opt[0] == "--weak":
            suite.set_weak(True)
            
        if opt[0] == "--tag":
            picker.parse_tag(opt[1])
            
        if opt[0] == "--testname":
            picker.set_testname(opt[1])
            
        if opt[0] == "--module_name":
            module_name = opt[1]
            
        if opt[0] == "-h" or opt[0] == "--help":
            help()
            sys.exit(0)
    
    # 创建 FrameMain 对象
    frame = FrameMain(picker, suite, result, logdir)
    
    # 执行框架，生成结果
    ret = frame.execute(args)

    # 生成html报告
    result.gen_mail_report(logdir+"report.html","test")

    # print "result: %d" % ret
    return ret


def help():
    print "Usage: main.sh [options] case_file_or_dir..."
    print
    print "Run cases, or cases in directories"
    print
    print "options"
    print "  --ignore=<file>:                  \t Ignore cases in <file>"
    print "  --weak:                           \t Quit when any case failed"
    print "  --tag=<feature>[,<feature>]...    \t Run cases which have (one of the) <feature>"
    print "                                    \t    Without this option, run ALL cases"
    print "                                    \t    Multiple --tag options means intersection"
    print "  --testname=<regex>                \t Run test whose name contains <regex>"
    print "  -h, --help:                       \t Show this help"

if __name__=='__main__':
    result = main()
    # print "rrrrr:%r" %result
    exit(result)


