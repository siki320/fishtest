# -*- coding: GB18030 -*-
'''
Created on Aug 16, 2011

@author: caiyifeng<caiyifeng>

@summary: 判断函数集
'''

import os
import re
from frame.lib.commonlib.dtssystem import dtssystem
from frame.lib.commonlib.utils import getpids

def check_process_exist(processpath):
    '''
    @summary: 检查C进程存在
    @param processpath: 进程的绝对路径
    '''
    pids = getpids(processpath)
    
    if pids:
        return True
    else:
        return False

def check_process_available(processname=None):
    """
    @note: 检查进程是否存在
    @return: 存在返回 True or 不存在返回 False
    """
    if processname:
        proc_num = []
        cmd = "pgrep -u $USER -f '%s'" % processname
        idlist = dtssystem(cmd, output=True, errlevel="debug")[1].splitlines()
        
        # 查看这些id是否对应了processname
        for id in idlist:
            cmd = "readlink /proc/%s/exe" % id
            idpath = dtssystem(cmd, output=True, errlevel="debug")[1].rstrip()
            if os.path.basename(idpath) == processname:
            # 找到了对应的程序path
                proc_num.append(int(id))

        if proc_num:
            return True
        else:
            return False

    else:
        return False

def check_pid_exist(pid):
    '''
    @summary: 检查pid存在
    @param pid: 进程id，int型
    '''
    ret = dtssystem("ps -p %d" % pid, errlevel="debug")
    
    if ret == 0:
        return True
    else:
        return False

    
def check_port_exist(port):
    '''
    @summary: 检查端口被占用
    @param port: 端口号
    '''
    cmd="netstat -nl | grep ':%s '" % port
    output = dtssystem(cmd, output=True, errlevel="debug")[1]
    
    if output:
        return True
    else:
        return False
    
    
def check_process_started(processpath, *ports):
    '''
    @summary: 检查C进程启动
    @param processpath: 进程的绝对路径
    @param ports: 进程端口号列表
    '''
    if not check_process_exist(processpath):
        return False
    
    for p in ports:
        if not check_port_exist(p):
            return False
        
    return True
    
    
def check_str_contain(string, regex):
    '''@summary: 检查string中含有正则regex'''
    match = re.search(regex, string)
    if match:
        return True
    else:
        return False
    
    
def check_lines_contain(lines, regex, ignore_list=[]):
    '''
    @summary: 检查lines中的每一行，是否含有正则regex
    @param ignore_list: 忽略符合ignore regex的行
    '''
    # 选出所有未被忽略的行
    f_lines = []
    for l in lines:
        for ig in ignore_list:
            if check_str_contain(l, ig):
                # 被忽略
                break
        else:
            # 未被忽略
            f_lines.append(l)
            
    # 检查剩下的行，是否符合regex
    for l in f_lines:
        if check_str_contain(l, regex):
            return True
    else:
        return False
    
    
def check_log_contain(log_reader, regex, ignore_list=[]):
    '''
    @summary: 检查log_reader指定的日志，是否含有regex正则。以行为单位
    @param log_reader: LogReader对象
    @param ignore_list: 忽略符合ignore regex的行
    '''
    # 从log_reader中读取
    string = log_reader.read()
    lines = string.splitlines()
    
    return check_lines_contain(lines, regex, ignore_list)


def check_path_contain(dirpath, filename, r=False):
    '''
    @summary: 检查dirpath目录中，是否含有filename文件or目录
    @param filename: 可以含有扩展符号*, ?
    @param r: 是否递归查找。默认False
    '''
    cmd = "find %s -name '%s'" % (dirpath, filename)
    if not r:
        # 非递归
        cmd += " -maxdepth 1"
    
    output = dtssystem(cmd, output=True)[1]
    if output:
        return True
    else:
        return False
    

def _test_check_lines_contain():
    lines = ["line1, feature", "line2, hudson", "line3, nts", "line4, npat"]
    ignore_list = [",.*d", ", nts"]     # 忽略第2，3项
    
    print check_lines_contain(lines, "[mn]", ignore_list)   # expect: True
    print check_lines_contain(lines, "[sk]")                # expect: True
    print check_lines_contain(lines, "[sk]", ignore_list)   # expect: False
    
if __name__ == "__main__":
    _test_check_lines_contain()

