# -*- coding: GB18030 -*-
'''
Created on May 26, 2011

@author: caiyifeng

@summary: ����Ӧsleep
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
    @summary: ����·���к����ļ�
    @param filename: ���Ժ�����չ����*, ?
    @param r: �Ƿ�ݹ���ҡ�Ĭ��False
    '''
    t = Timer2()
    #����Ѱ��
    dlog.debug("Sleep until finding '%s' in '%s'", dirpath, filename)
    
    while t.end() < maxwait:
        if checker.check_path_contain(dirpath, filename,r):
            #�ҵ�
            dlog.debug("Sleep Ends")
            return 
        else:
            time.sleep(0.2)
    else:
        raise AutosleepException, "'%s' has no file '%s' during %s second(s)" % (dirpath, filename, maxwait)
   
def sleeptill_haslog(logreader, regstr, maxwait=10):
    '''
    @summary: �ȴ�log�г���ĳ������
    @param logreader: LogReader����
    @param regstr: �����ַ���
    @param maxwait: ��ȴ�ʱ�䣬��λ��
    @raise AutosleepException: ������ȴ�ʱ��
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    # ��ʼ��ʱ
    t = Timer2()
    
    # ����Ѱ��
    dlog.debug("Sleep until finding '%s' in '%s'", regstr, logreader.logpath)
    
    while t.end() < maxwait:
        if checker.check_log_contain(logreader, regstr):
            # �ҵ�
            dlog.debug("Sleep Ends")
            return
        else:
            # û�ҵ�
            time.sleep(0.1)
            
    else:
        # �������ʱ��
        raise AutosleepException, "'%s' has no log pattern '%s' during %s second(s)" % (logreader.logpath, regstr, maxwait)


def sleeptill_has_either_log(logreader, regstr1, regstr2, maxwait=10):
    '''
    @summary: �ȴ�log�г���ĳ���������е�һ��
    @param logreader: LogReader����
    @param regstr: �����ַ���
    @param maxwait: ��ȴ�ʱ�䣬��λ��
    @raise AutosleepException: ������ȴ�ʱ��
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    # ��ʼ��ʱ
    t = Timer2()
    
    # ����Ѱ��
    dlog.debug("Sleep until finding '%s' or '%s' in '%s'", regstr1, regstr2, logreader.logpath)
    
    while t.end() < maxwait:
        if checker.check_log_contain(logreader, regstr1):
            # �ҵ�
            dlog.debug("Sleep Ends")
            return
        elif checker.check_log_contain(logreader, regstr2):
            # �ҵ�
            dlog.debug("Sleep Ends")
            return
        else:
            # û�ҵ�
            time.sleep(0.1)
            
    else:
        # �������ʱ��
        raise AutosleepException, "'%s' has no log pattern '%s' or '%s' during %s second(s)" % (logreader.logpath, regstr1,regstr2, maxwait)


def sleeptill_hasprocess(processpath, maxwait=10):
    '''
    @summary: �ȴ�C���̴���
    @param processpath: ���̵ľ���·��
    @param maxwait: ��ȴ�ʱ�䣬��λ��
    @raise AutosleepException: ������ȴ�ʱ��
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Process '%s' exists", processpath)
    
    while t.end() <maxwait:
        # �жϽ����Ƿ����
        if checker.check_process_exist(processpath):
            # ����
            dlog.debug("Sleep Ends")
            return
        else:
            # ������
            time.sleep(0.1)
            
    else:
        #�������ʱ��
        raise AutosleepException, "Process '%s' never exists during %s second(s)" % (processpath, maxwait)


def sleeptill_noprocess(processpath, maxwait=10):
    '''
    @summary: �ȴ�C���̲�����
    @param processpath: ���̵ľ���·��
    @param maxwait: ��ȴ�ʱ�䣬��λ��
    @raise AutosleepException: ������ȴ�ʱ��
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Process '%s' NOT Exists", processpath)
    
    while t.end() <maxwait:
        # �жϽ����Ƿ����
        if checker.check_process_exist(processpath):
            # ����
            time.sleep(0.1)
        else:
            # ������
            dlog.debug("Sleep Ends")
            return
            
    else:
        #�������ʱ��
        raise AutosleepException, "Process '%s' always exists during %s second(s)" % (processpath, maxwait)


def sleeptill_hasport(port, maxwait=10):
    '''
    @summary: �ȴ��˿ڱ�ռ��
    @param port: �˿ں�
    @param maxwait: ��ȴ�ʱ�䣬��λ��
    @raise AutosleepException: ������ȴ�ʱ��
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Port '%s' exists", port)
    
    while t.end() <maxwait:
        # �ж϶˿��Ƿ�ռ��
        if checker.check_port_exist(port):
            # ��ռ��
            dlog.debug("Sleep Ends")
            return
        else:
            # ���ͷ�
            time.sleep(0.1)
            
    else:
        #�������ʱ��
        raise AutosleepException, "Port '%s' never exists during %s second(s)" % (port, maxwait)


def sleeptill_process_hasport(processpath, port, maxwait=10):
    '''@summary: ��sleeptill_hasport�Ķ��ƣ��κ�ʱ���ֽ��̲�������ֱ���쳣�˳�
    @param processpath: ���̵ľ���·��
    @param port: �˿ں�
    @param maxwait: ��ȴ�ʱ�䣬��λ��
    @raise AutosleepException: ������ȴ�ʱ��'''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Port '%s' exists", port)
    
    while t.end() <maxwait:
        # �ж϶˿��Ƿ�ռ��
        if checker.check_port_exist(port):
            # ��ռ��
            dlog.debug("Sleep Ends")
            return
        else:
            # ���ͷ�
            if checker.check_process_exist(processpath):
                time.sleep(0.1)
            else:
                raise AutosleepException, "Process '%s' not exist while waiting port '%s'" % (processpath, port)
            
    else:
        #�������ʱ��
        raise AutosleepException, "Port '%s' never exists during %s second(s)" % (port, maxwait)


def sleeptill_process_has_either_port(processpath, port1, port2, maxwait=10):
    '''@summary: ��sleeptill_hasport�Ķ��ƣ��κ�ʱ���ֽ��̲�������ֱ���쳣�˳�
    @param processpath: ���̵ľ���·��
    @param port: �˿ں�
    @param maxwait: ��ȴ�ʱ�䣬��λ��
    @raise AutosleepException: ������ȴ�ʱ��'''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Port1 '%s' or Port2 '%s'  exists", port1, port2)
    
    while t.end() <maxwait:
        # �ж϶˿��Ƿ�ռ��
        if checker.check_port_exist(port1):
            # ��ռ��
            dlog.debug("Sleep Ends")
            return
        if checker.check_port_exist(port2):
            # ��ռ��
            dlog.debug("Sleep Ends")
            return
        else:
            # ���ͷ�
            if checker.check_process_exist(processpath):
                time.sleep(0.1)
            else:
                raise AutosleepException, "Process '%s' not exist while waiting port1 '%s' or port2 '%s' " % (processpath, port1, port2)
            
    else:
        #�������ʱ��
        raise AutosleepException, "Port1 '%s' or Port2 '%s' never exists during %s second(s)" % (port1, port2, maxwait)

def sleeptill_noport(port, maxwait=10):
    '''
    @summary: �ȴ��˿ڱ��ͷ�
    @param port: �˿ں�
    @param maxwait: ��ȴ�ʱ�䣬��λ��
    @raise AutosleepException: ������ȴ�ʱ��
    '''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    t = Timer2()
    
    dlog.debug("Sleep until Port '%s' Free", port)
    
    while t.end() <maxwait:
        # �ж϶˿��Ƿ�ռ��
        if checker.check_port_exist(port):
            # ��ռ��
            time.sleep(0.1)
        else:
            # ���ͷ�
            dlog.debug("Sleep Ends")
            return
            
    else:
        #�������ʱ��
        raise AutosleepException, "Port '%s' always exists during %s second(s)" % (port, maxwait)
        

def sleeptill_startprocess(processpath, port, maxwait=10):
    '''@param port: ������һ��int��Ҳ������һ��int list'''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    sleeptill_hasprocess(processpath, maxwait)
    if isinstance(port, int):
        sleeptill_process_hasport(processpath, port, maxwait)
    else:
        for p in port:
            sleeptill_process_hasport(processpath, p, maxwait)
    
    
def sleeptill_killprocess(processpath, port, maxwait=10):
    '''@param port: ������һ��int��Ҳ������һ��int list'''
    if vgutils.is_running_valgrind():
        maxwait *= 30

    sleeptill_noprocess(processpath, maxwait)
    if isinstance(port, int):
        sleeptill_noport(port, maxwait)
    else:
        for p in port:
            sleeptill_noport(p, maxwait)
    
