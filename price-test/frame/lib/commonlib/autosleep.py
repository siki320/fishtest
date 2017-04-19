# -*- coding: GB18030 -*-
'''
Created on May 26, 2011

@author: caiyifeng

@summary: 自适应sleep
'''

import time
import os

from frame.lib.commonlib.timer import Timer2
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib import checker
from frame.lib.commonlib import vgutils

class AutosleepException(Exception):
    pass
def sleeptill_hasfile(dirpath, filename,  maxwait=10,r=False):
    '''
    @summary: 断言路径中含有文件
    @param filename: 可以含有扩展符号*, ?
    @param r: 是否递归查找。默认False
    '''
    t = Timer2()
    #不断寻找
    dlog.debug("Sleep until finding '%s' in '%s'", dirpath, filename)
    
    while t.end() < maxwait:
        if checker.check_path_contain(dirpath, filename,r):
            #找到
            dlog.debug("Sleep Ends")
            return 
        else:
            time.sleep(0.2)
    else:
        raise AutosleepException, "'%s' has no file '%s' during %s second(s)" % (dirpath, filename, maxwait)
   
def sleeptill_haslog(logreader, regstr, maxwait=10):
    '''
    @summary: 等待log中出现某个正则
    @param logreader: LogReader对象
    @param regstr: 正则字符串
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    # 开始计时
    t = Timer2()
    
    # 不断寻找
    dlog.debug("Sleep until finding '%s' in '%s'", regstr, logreader.logpath)
    
    while t.end() < maxwait:
        if checker.check_log_contain(logreader, regstr):
            # 找到
            dlog.debug("Sleep Ends")
            return
        else:
            # 没找到
            time.sleep(0.1)
            
    else:
        # 超过最大时间
        raise AutosleepException, "'%s' has no log pattern '%s' during %s second(s)" % (logreader.logpath, regstr, maxwait)


def sleeptill_has_either_log(logreader, regstr1, regstr2, maxwait=10):
    '''
    @summary: 等待log中出现某两个正则中的一个
    @param logreader: LogReader对象
    @param regstr: 正则字符串
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    # 开始计时
    t = Timer2()
    
    # 不断寻找
    dlog.debug("Sleep until finding '%s' or '%s' in '%s'", regstr1, regstr2, logreader.logpath)
    
    while t.end() < maxwait:
        if checker.check_log_contain(logreader, regstr1):
            # 找到
            dlog.debug("Sleep Ends")
            return
        elif checker.check_log_contain(logreader, regstr2):
            # 找到
            dlog.debug("Sleep Ends")
            return
        else:
            # 没找到
            time.sleep(0.1)
            
    else:
        # 超过最大时间
        raise AutosleepException, "'%s' has no log pattern '%s' or '%s' during %s second(s)" % (logreader.logpath, regstr1,regstr2, maxwait)


def sleeptill_hasprocess(processpath, maxwait=10):
    '''
    @summary: 等待C进程存在
    @param processpath: 进程的绝对路径
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Process '%s' exists", processpath)
    
    while t.end() <maxwait:
        # 判断进程是否存在
        if checker.check_process_exist(processpath):
            # 存在
            dlog.debug("Sleep Ends")
            return
        else:
            # 不存在
            time.sleep(0.1)
            
    else:
        #超过最大时间
        raise AutosleepException, "Process '%s' never exists during %s second(s)" % (processpath, maxwait)


def sleeptill_noprocess(processpath, maxwait=10):
    '''
    @summary: 等待C进程不存在
    @param processpath: 进程的绝对路径
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Process '%s' NOT Exists", processpath)
    
    while t.end() <maxwait:
        # 判断进程是否存在
        if checker.check_process_exist(processpath):
            # 存在
            time.sleep(0.1)
        else:
            # 不存在
            dlog.debug("Sleep Ends")
            return
            
    else:
        #超过最大时间
        raise AutosleepException, "Process '%s' always exists during %s second(s)" % (processpath, maxwait)


def sleeptill_hasport(port, maxwait=10):
    '''
    @summary: 等待端口被占用
    @param port: 端口号
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Port '%s' exists", port)
    
    while t.end() <maxwait:
        # 判断端口是否被占用
        if checker.check_port_exist(port):
            # 被占用
            dlog.debug("Sleep Ends")
            return
        else:
            # 被释放
            time.sleep(0.1)
            
    else:
        #超过最大时间
        raise AutosleepException, "Port '%s' never exists during %s second(s)" % (port, maxwait)


def sleeptill_process_hasport(processpath, port, maxwait=10):
    '''@summary: 对sleeptill_hasport的定制，任何时候发现进程不存在则直接异常退出
    @param processpath: 进程的绝对路径
    @param port: 端口号
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候'''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Port '%s' exists", port)
    
    while t.end() <maxwait:
        # 判断端口是否被占用
        if checker.check_port_exist(port):
            # 被占用
            dlog.debug("Sleep Ends")
            return
        else:
            # 被释放
            if checker.check_process_exist(processpath):
                time.sleep(0.1)
            else:
                raise AutosleepException, "Process '%s' not exist while waiting port '%s'" % (processpath, port)
            
    else:
        #超过最大时间
        raise AutosleepException, "Port '%s' never exists during %s second(s)" % (port, maxwait)


def sleeptill_process_has_either_port(processpath, port1, port2, maxwait=10):
    '''@summary: 对sleeptill_hasport的定制，任何时候发现进程不存在则直接异常退出
    @param processpath: 进程的绝对路径
    @param port: 端口号
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候'''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Port1 '%s' or Port2 '%s'  exists", port1, port2)
    
    while t.end() <maxwait:
        # 判断端口是否被占用
        if checker.check_port_exist(port1):
            # 被占用
            dlog.debug("Sleep Ends")
            return
        if checker.check_port_exist(port2):
            # 被占用
            dlog.debug("Sleep Ends")
            return
        else:
            # 被释放
            if checker.check_process_exist(processpath):
                time.sleep(0.1)
            else:
                raise AutosleepException, "Process '%s' not exist while waiting port1 '%s' or port2 '%s' " % (processpath, port1, port2)
            
    else:
        #超过最大时间
        raise AutosleepException, "Port1 '%s' or Port2 '%s' never exists during %s second(s)" % (port1, port2, maxwait)

def sleeptill_noport(port, maxwait=10):
    '''
    @summary: 等待端口被释放
    @param port: 端口号
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Port '%s' Free", port)
    
    while t.end() <maxwait:
        # 判断端口是否被占用
        if checker.check_port_exist(port):
            # 被占用
            time.sleep(0.1)
        else:
            # 被释放
            dlog.debug("Sleep Ends")
            return
            
    else:
        #超过最大时间
        raise AutosleepException, "Port '%s' always exists during %s second(s)" % (port, maxwait)
        

def sleeptill_startprocess(processpath, port, maxwait=10):
    '''@param port: 可以是一个int，也可以是一个int list'''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    sleeptill_hasprocess(processpath, maxwait)
    if isinstance(port, int):
        sleeptill_process_hasport(processpath, port, maxwait)
    else:
        for p in port:
            sleeptill_process_hasport(processpath, p, maxwait)
    
    
def sleeptill_killprocess(processpath, port, maxwait=10):
    '''@param port: 可以是一个int，也可以是一个int list'''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    sleeptill_noprocess(processpath, maxwait)
    if isinstance(port, int):
        sleeptill_noport(port, maxwait)
    else:
        for p in port:
            sleeptill_noport(p, maxwait)
    
