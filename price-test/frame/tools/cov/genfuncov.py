#!/usr/bin/env python
#-*- encoding:utf-8 -*-
import os
import sys

from frame.tools.cov.func_cov import *
#from func_cov import *


def main():
    if 4 > len(sys.argv) or 0 == len(sys.argv[1]) or \
            0 == len(sys.argv[2]) or 0 == len(sys.argv[3]):
        print "args is not 3 number or arg is null"
        exit(1)

    if not os.path.exists(sys.argv[1]) or not os.path.exists(sys.argv[2]) or \
            not os.path.exists(sys.argv[3]):
        print "path is not exist"
        exit(1)
    
    func_cov_obj = Func_Cov()
    ret1 = func_cov_obj.analyse_cov(sys.argv[1], sys.argv[2])
    if 0 == ret1:
        ret2 = func_cov_obj.gen_zhengpai(sys.argv[2], sys.argv[3])
    if 0 == ret2:
        func_cov_obj.gen_all_casename(sys.argv[3]+"/zhengpai.txt", sys.argv[3]+"/case_name.txt")
        func_cov_obj.gen_repeat_case(sys.argv[2], sys.argv[3])

if __name__=='__main__':
    main()
