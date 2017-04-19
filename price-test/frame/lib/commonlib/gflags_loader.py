# -*- coding: GB18030 -*-
'''
Created on Dec 5, 2011

@author: caiyifeng<caiyifeng>

@summary: ����gflags
'''

import os
import re
import sys

# ����gflags��pythonpath
gflags_path = os.path.join(os.path.dirname(__file__), "../thirdlib/gflags")
gflags_path = os.path.abspath(gflags_path)
if gflags_path not in sys.path:
    sys.path.append(gflags_path)

import gflags


def load_gflags(filepath):
    '''
    @summary: load and define gflags from filepath
    @param filepath: gflags filepath
    @return: FlagValues object
    '''
    # ����ֵ
    ret = gflags.FlagValues()
    
    # define���е�flag
    f = open(filepath)
    for line in f:
        if line.strip() == "":
            continue

        # ������flag��
        flag_name, flag_value = re.match("--(.*)=(.*)", line).groups()
        flag_name = flag_name.strip()
        flag_value = flag_value.strip()
        
        # define �� flag
        if flag_value == "true" or flag_value == "false":
            gflags.DEFINE_boolean(flag_name, False, flag_name, flag_values=ret)
        else:
            gflags.DEFINE_string(flag_name, "", flag_name, flag_values=ret)
    f.close()
    
    # ����gflags
    # ��һ�������ǳ��������������ã�ֱ��ȡ��ֵ
    argv = ["", "--flagfile=%s" % filepath]
    ret(argv)

    return ret


def _test_load_gflags():
    filepath = raw_input("Enter gflags filepath: ")
    flag = load_gflags(filepath)
    
    for f in flag:
        print "--%s=%s <%s>" % (f, flag[f].value, flag[f].Type())


if __name__ == "__main__":
    _test_load_gflags()
