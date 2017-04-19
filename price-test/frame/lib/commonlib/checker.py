# -*- coding: GB18030 -*-
'''
Created on Aug 16, 2011

@author: caiyifeng<caiyifeng>

@summary: �жϺ�����
'''

import os
import re
from frame.lib.commonlib.dtssystem import dtssystem
from frame.lib.commonlib.utils import getpids

def check_process_exist(processpath):
    '''
    @summary: ���C���̴���
    @param processpath: ���̵ľ���·��
    '''
    pids = getpids(processpath)
    
    if pids:
        return True
    else:
        return False

def check_process_available(processname=None):
    """
    @note: �������Ƿ����
    @return: ���ڷ��� True or �����ڷ��� False
    """
    if processname:
        proc_num = []
        cmd = "pgrep -u $USER -f '%s'" % processname
        idlist = dtssystem(cmd, output=True, errlevel="debug")[1].splitlines()
        
        # �鿴��Щid�Ƿ��Ӧ��processname
        for id in idlist:
            cmd = "readlink /proc/%s/exe" % id
            idpath = dtssystem(cmd, output=True, errlevel="debug")[1].rstrip()
            if os.path.basename(idpath) == processname:
            # �ҵ��˶�Ӧ�ĳ���path
                proc_num.append(int(id))

        if proc_num:
            return True
        else:
            return False

    else:
        return False

def check_pid_exist(pid):
    '''
    @summary: ���pid����
    @param pid: ����id��int��
    '''
    ret = dtssystem("ps -p %d" % pid, errlevel="debug")
    
    if ret == 0:
        return True
    else:
        return False

    
def check_port_exist(port):
    '''
    @summary: ���˿ڱ�ռ��
    @param port: �˿ں�
    '''
    cmd="netstat -nl | grep ':%s '" % port
    output = dtssystem(cmd, output=True, errlevel="debug")[1]
    
    if output:
        return True
    else:
        return False
    
    
def check_process_started(processpath, *ports):
    '''
    @summary: ���C��������
    @param processpath: ���̵ľ���·��
    @param ports: ���̶˿ں��б�
    '''
    if not check_process_exist(processpath):
        return False
    
    for p in ports:
        if not check_port_exist(p):
            return False
        
    return True
    
    
def check_str_contain(string, regex):
    '''@summary: ���string�к�������regex'''
    match = re.search(regex, string)
    if match:
        return True
    else:
        return False
    
    
def check_lines_contain(lines, regex, ignore_list=[]):
    '''
    @summary: ���lines�е�ÿһ�У��Ƿ�������regex
    @param ignore_list: ���Է���ignore regex����
    '''
    # ѡ������δ�����Ե���
    f_lines = []
    for l in lines:
        for ig in ignore_list:
            if check_str_contain(l, ig):
                # ������
                break
        else:
            # δ������
            f_lines.append(l)
            
    # ���ʣ�µ��У��Ƿ����regex
    for l in f_lines:
        if check_str_contain(l, regex):
            return True
    else:
        return False
    
    
def check_log_contain(log_reader, regex, ignore_list=[]):
    '''
    @summary: ���log_readerָ������־���Ƿ���regex��������Ϊ��λ
    @param log_reader: LogReader����
    @param ignore_list: ���Է���ignore regex����
    '''
    # ��log_reader�ж�ȡ
    string = log_reader.read()
    lines = string.splitlines()
    
    return check_lines_contain(lines, regex, ignore_list)


def check_path_contain(dirpath, filename, r=False):
    '''
    @summary: ���dirpathĿ¼�У��Ƿ���filename�ļ�orĿ¼
    @param filename: ���Ժ�����չ����*, ?
    @param r: �Ƿ�ݹ���ҡ�Ĭ��False
    '''
    cmd = "find %s -name '%s'" % (dirpath, filename)
    if not r:
        # �ǵݹ�
        cmd += " -maxdepth 1"
    
    output = dtssystem(cmd, output=True)[1]
    if output:
        return True
    else:
        return False
    

def _test_check_lines_contain():
    lines = ["line1, feature", "line2, hudson", "line3, nts", "line4, npat"]
    ignore_list = [",.*d", ", nts"]     # ���Ե�2��3��
    
    print check_lines_contain(lines, "[mn]", ignore_list)   # expect: True
    print check_lines_contain(lines, "[sk]")                # expect: True
    print check_lines_contain(lines, "[sk]", ignore_list)   # expect: False
    
if __name__ == "__main__":
    _test_check_lines_contain()

