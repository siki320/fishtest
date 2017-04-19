# -*- coding: GB18030 -*-
'''
Created on Aug 17, 2011

@author: caiyifeng<caiyifeng>

@summary: 实用函数
'''

import os
import signal
import shutil
import re
import inspect
import time
from frame.lib.commonlib.dtssystem import dtssystem
from frame.lib.commonlib.dtssystem2 import dtssystem_out
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib import vgutils

def getpids(processpath):
    '''
    @summary: 获得C进程的id list(int list)
    @param processpath: 进程的绝对路径
    @return: 进程id list。没有该进程时，返回空list

    @attention: 不适用于以下场景
     - 进程是脚本，如.sh, .py。因为它们的进程是脚本解释器（bash, python）
     - valgrind托管进程
    '''
    res = []

    if vgutils.is_running_valgrind():
        res.extend(getvpid(processpath))

    processpath = os.path.abspath(processpath)
    processname = os.path.basename(processpath)

    # 获得processname对应的所有id
    cmd = "pgrep -u $USER -f '%s'" % processname
    idlist = dtssystem(cmd, output=True, errlevel="debug")[1].splitlines()

    # 查看这些id是否对应了processpath
    for id in idlist:
        cmd = "readlink /proc/%s/exe" % id
        idpath = dtssystem(cmd, output=True, errlevel="debug")[1].rstrip()
        if idpath == processpath or idpath == processpath+" (deleted)":
            # 找到了对应的程序path
            res.append(int(id))
    if res:
        dlog.debug('process %s has pid: %s' % (processpath, ','.join(['%s' % pid for pid in res])))
    return res

def getvpid(processpath):
    '''
    获得以valgrind方式运行的进程的pid
    '''
    retlist = [] 

    cmd = "ps -C memcheck-amd64-linux -o pid | grep -o -P '\d+'"
    idlist = dtssystem(cmd, output=True)[1].splitlines()
    
    processpath = os.path.abspath(processpath)
    # 查看这些id是否对应了processpath
    for id in idlist:
        #如若不是当前user的process，则continue
        cmd = "ps -u $USER -o pid | grep -o -P '\d+' | grep %s" % id
        if dtssystem(cmd, output=True)[1].strip('\n').strip(' ') == '':
            continue
        
        cmd = 'readlink /proc/%s/cwd' % id
        ret, stdout, stderr = dtssystem(cmd, output = True)
        if ret != 0:
            continue
        cwd = stdout.rstrip()
        if processpath.find(cwd) < 0:
            continue

        cmd = "cat /proc/%s/cmdline" % id
        ret, stdout, stderr = dtssystem(cmd, output = True)
        if ret != 0:
            continue
        tokens = stdout.strip().split('\0')
        i=0
        while i < len(tokens):
            if tokens[i].startswith('--log-file='): #note: this is a trap. valgrind command should end with last param --logfile. otherwise will fail.
                break
            i += 1
        if i >= len(tokens) - 1 :
            continue
        bin=tokens[i+1]
        
        idpath = os.path.abspath(os.path.join(cwd, bin))
        if idpath == processpath or idpath == processpath + " (deleted)":
            retlist.append(id)
    
    return retlist


def kill_process(processpath, sig=signal.SIGTERM):
    '''
    @summary: 杀死C进程
    @param processpath: 进程的绝对路径
    '''
    pids = getpids(processpath)
    for p in pids:
        try:
            os.kill(p, sig)
            
        except OSError, e:
            if e.strerror == "No such process":
                dlog.info("Pid '%s' not exist, ignore it", p, exc_info=True)
            else:
                # 未知异常，重新抛出
                raise


def rename_cores(path):
    '''@summary: 重命名path和path/bin/下的所有core'''
    # path
    cmd = "find %s -name 'core.*' -maxdepth 1" % path
    cores = dtssystem(cmd, output=True)[1].splitlines()
    for c in cores:
        dir_str, filename_str = os.path.split(c)        # 分开路径和文件名
        ext_str = os.path.splitext(filename_str)[1]     # 获得扩展名
        target_name = dir_str + "/" + "bug" + ext_str
        cmd = "mv %s %s" % (c, target_name)
        dtssystem(cmd, loglevel="debug", prompt="Rename Core")

    # path/bin/
    if not os.path.isdir("%s/bin" % path):
        return

    cmd = "find %s/bin -name 'core.*' -maxdepth 1" % path
    cores = dtssystem(cmd, output=True)[1].splitlines()
    for c in cores:
        dir_str, filename_str = os.path.split(c)        # 分开路径和文件名
        ext_str = os.path.splitext(filename_str)[1]     # 获得扩展名
        target_name = dir_str + "/" + "bug" + ext_str
        cmd = "mv %s %s" % (c, target_name)
        dtssystem(cmd, loglevel="debug", prompt="Rename Core")


def log_cores(path):
    '''@summary: 日志输出path和path/bin/下的所有core'''
    # path
    cmd = "find %s -name 'core.*' -maxdepth 1" % path
    cores = dtssystem(cmd, output=True)[1]
    if cores:
        dlog.diagnose("Find Cores in %s:\n%s", path, cores)

    # path/bin/
    if not os.path.isdir("%s/bin" % path):
        return

    cmd = "find %s/bin -name 'core.*' -maxdepth 1" % path
    cores = dtssystem(cmd, output=True)[1]
    if cores:
        dlog.diagnose("Find Cores in %s/bin/:\n%s", path, cores)


def bak_or_revert(path):
    '''
    @summary: 备份path为path.dtsbak；或者恢复path.dtsbak到path
    @param path: 需要备份或恢复的路径
    '''
    bak_path = os.path.abspath(path) + ".dtsbak"

    if os.path.isfile(path):
        # 原路径为file
        if os.path.isfile(bak_path):
            # 已经有备份文件了，需要恢复
            dlog.debug("Revert File: %s", bak_path)
            shutil.copy(bak_path, path)
        else:
            # 还没有备份文件，备份之
            dlog.debug("Bak File: %s", path)
            shutil.copy(path, bak_path)

    elif os.path.isdir(path):
        # 原路径为dir
        if os.path.isdir(bak_path):
            # 已经有备份目录了，需要恢复
            dlog.debug("Revert Dir: %s", bak_path)
            shutil.rmtree(path)     # 先删除原目录
            shutil.copytree(bak_path, path)
        else:
            # 还没有备份目录，备份之
            dlog.debug("Bak Dir: %s", path)
            shutil.copytree(path, bak_path)

    else:
        raise Exception, "Can't bak_or_revert '%s': Neither file nor dir" % path


def get_py_owner(py_path):
    '''
    @summary: 从py文件中获取owner
    @note:
     - 提取固定格式的author域，格式为 "@author: xxx"
     - 如果case中没有固定格式的author域，返回"unknown"
    @author: xuwei
    '''
    #如果传递的case_str有误，不是一个文件，容错处理
    if False == os.path.isfile(py_path):
        return "unknown"

    case_file = open(py_path, "r")
    content = case_file.read()

    author_re = re.compile("@author:(.*)\n")
    author_list = author_re.findall(content)

    if 0 == len(author_list):
        #文件中没有@author:字段
        case_file.close()
        return "unknown"
    else:
        author_str = author_list[0]

    #过滤掉多余的空格
    author_str = author_str.strip(" ")

    #过滤掉"<***>"部分，这个部分在html中无法识别
    index = author_str.find("<")
    if -1 == index:
        case_file.close()
        return author_str
    else:
        case_file.close()
        return author_str[:index]


def get_ejb_content(s):
    '''@summary: 获取字符串s中的ejb内容
    @attention: ejb内容以EJB:BEGIN开始，以EJB:END结束，返回结果中不包含这两行定位行'''
    m = re.search("EJB:BEGIN\n(.*?)EJB:END", s, flags=re.DOTALL)
    if not m:
        return ""
    else:
        return m.group(1).strip()


def get_abs_dir(path,exist=True):
    """Return absolute, normalized path to directory, if it exists; None
    otherwise.
    """
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.normpath(os.path.abspath(os.path.join(os.getcwd(),path)))
    if path is None or (not os.path.isdir(path) and exist == True):
        return None
    return path


def get_current_path():
    caller_file = inspect.stack()[1][1]
    return os.path.abspath(os.path.dirname(caller_file))


def _test_get_abs_dir():
    print get_abs_dir("~/aaa/bbb",exist=False)
    print get_abs_dir("./~/aaa/bbb",exist=False)
    print get_abs_dir("./aaa/bbb",exist=False)

def _test_get_py_owner():
    print get_py_owner(__file__)

def _test_get_ejb_content():
    '''
    EJB:BEGIN
    a line
    第二行
    EJB:END
    '''
    print get_ejb_content(_test_get_ejb_content.__doc__)
    print "shold be empty.", get_ejb_content("aabb\ncc")

def get_file_type(filename):
    if not os.path.exists(filename):
        return None
    ret, stdout, stderr = dtssystem_out('file %s' % filename)
    type = stdout.split(':')[1].strip().strip('\n')
    if type.find('data') >= 0:
        return 'data'
    elif type.find('text') >=0:
        return 'text'
    else:
        return 'other' 
def genTimestamp(day,type=0):
    if type==0:
        return time.time()-day*24*60*60
    else:
        return time.time()+day*24*60*60
if "__main__" == __name__:
    print "_test_get_abs_dir:"
    _test_get_abs_dir()

    print "\n_test_get_py_owner:"
    _test_get_py_owner()

    print "\n_test_get_ejb_content"
    _test_get_ejb_content()
