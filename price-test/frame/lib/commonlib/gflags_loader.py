# -*- coding: GB18030 -*-
'''
Created on Dec 5, 2011

@author: caiyifeng<caiyifeng>

@summary: 加载gflags
'''

import os
import re
import sys

# 增加gflags到pythonpath
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
    # 返回值
    ret = gflags.FlagValues()
    
    # define所有的flag
    f = open(filepath)
    for line in f:
        if line.strip() == "":
            continue

        # 解析出flag名
        flag_name, flag_value = re.match("--(.*)=(.*)", line).groups()
        flag_name = flag_name.strip()
        flag_value = flag_value.strip()
        
        # define 该 flag
        if flag_value == "true" or flag_value == "false":
            gflags.DEFINE_boolean(flag_name, False, flag_name, flag_values=ret)
        else:
            gflags.DEFINE_string(flag_name, "", flag_name, flag_values=ret)
    f.close()
    
    # 解析gflags
    # 第一个参数是程序名，这里无用，直接取空值
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
