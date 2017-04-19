# -*- coding: GB18030 -*-
'''
Created on Aug 10, 2011

@author: caiyifeng<caiyifeng>

@attention: �ӿڲ����϶ࡣϣ������ӿڵģ�����ʹ��dtssystem2ģ��

@summary: 
 - Bash�����е���
 - �й������е��õ�������������־��ͻ
'''

import sys
import subprocess
import fcntl
import os
import select
from frame.lib.commonlib.dlog import dlog


def dtssystem(cmd, output=False, loglevel=None, errlevel="warning", prompt="Run cmd", pflag=False, logger=dlog):
    '''
    @summary: (����)����shell����cmd
    @attention: ���Ҫ��̨����������ʹ��dtssystem_async()
    
    @param output: 
     - ΪTrueʱ������cmd�� (return code, stdout output, stderr output)
     - ΪFalseʱ��ֻ����cmd��return code�������������ض���/dev/null
    
    @param loglevel: 
     - ����ΪNone, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - ��ΪNoneʱ��ִ�е�cmd��������־
    
    @param errlevel: 
     - ����ΪNone, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - ��ΪNoneʱ����cmd�����벻Ϊ0�����¼��־
    
    @param pflag: print flag��ΪTrueʱ��ӡcmd����Ļ���
    
    @param logger: log object��Ĭ��Ϊdlog
    
    @param prompt: ��־��ʾ��
    '''
    if loglevel:
        log_func = getattr(logger, loglevel)
        log_func("%s: %s", prompt, cmd)
        
    if errlevel:
        err_func = getattr(logger, errlevel)
    else:
        err_func = None
    
    if output:
        return _dtssystem_output(cmd, err_func, prompt, pflag)
    else:
        return _dtssystem_output(cmd, err_func, prompt, pflag)[0]
    
    
def dtssystem_async(cmd, loglevel=None, prompt="Run cmd", pflag=False, logger=dlog):
    '''
    @summary: ��̨����shell����cmd
    
    @param loglevel: 
     - ����ΪNone, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - ��ΪNoneʱ��ִ�е�cmd��������־
     
    @param prompt: ��־��ʾ��
    
    @param pflag: print flag��ΪTrueʱ��ӡcmd����Ļ���
    
    @param logger: log object��Ĭ��Ϊdlog
    
    @return: ����cmd��pid
    '''
    if loglevel:
        log_func = getattr(logger, loglevel)
        log_func("%s: %s", prompt, cmd)
        
    if pflag:
        dev = sys.stdout
    else:
        dev = open("/dev/null", "w")
    proc = subprocess.Popen(cmd, shell=True, stdout=dev, stderr=subprocess.STDOUT)
    return proc.pid
    
    
def _dtssystem_output(cmd, err_func, prompt, pflag):
    '''@return: ����(return code, stdout output, stderr output)'''
    outdata_l = []
    errdata_l = []
    
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    # stderr�����ǵ�����PIPE
    
    # ��proc��stdout��stderr����Ϊ������
    for f in [proc.stdout, proc.stderr]:
        flags = fcntl.fcntl(f, fcntl.F_GETFL)
        fcntl.fcntl(f, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    
    while True:
        # ��ѯ
        ret = proc.poll()
        r, w, x = select.select([proc.stdout, proc.stderr], [], [], 1)     # �������1s��EOFҲ��linux��Ϊ�����
        
        if proc.stdout in r:
            tmp_out = proc.stdout.read()
            outdata_l.append(tmp_out)
            if pflag:
                sys.stdout.write(tmp_out)
            
        if proc.stderr in r:
            tmp_err = proc.stderr.read()
            errdata_l.append(tmp_err)
            if pflag:
                sys.stdout.write(tmp_err)
        
        if ret is not None:
            # cmd����
            break
        
    outdata = "".join(outdata_l)
    errdata = "".join(errdata_l)
        
    if ret != 0 and err_func:
        # cmd�����벻Ϊ0
        if errdata:
            err_func("Return %d when %s: %s\nError message: %s", ret, prompt, cmd, errdata)
        else:
            err_func("Return %d when %s: %s", ret, prompt, cmd)
        
    return ret, outdata, errdata


def _test_dtssystem():
    ret = dtssystem("echo '12345' > a.txt", loglevel="debug")
    print "ret:", ret
    ret = dtssystem("rm a.txt b.txt", loglevel="debug", prompt="Remove files")
    print "ret:", ret
    ret = dtssystem("for ((i=0; i<8; i++)); do echo $i; sleep 0.5; done", loglevel="info", pflag=True)  # cmd����꣬���ret
    print "ret:", ret
    
def _test_dtssystem_output():
    ret = dtssystem("echo '12345' > a.txt", output=True, loglevel="debug")
    print "ret:", ret
    ret = dtssystem("rm a.txt b.txt", output=True, loglevel="debug", prompt="Remove files")
    print "ret:", ret
    ret = dtssystem("for ((i=0; i<8; i++)); do echo $i; echo 100$i >&2; sleep 0.5; done", output=True, loglevel="info", pflag=True)  # cmd����꣬���ret
    print "ret:", ret
    
def _test_dtssystem_async():
    ret = dtssystem_async("echo '12345' > a.txt", loglevel="debug")
    print "pid:", ret
    ret = dtssystem_async("rm a.txt b.txt", loglevel="debug", prompt="Remove files")
    print "pid:", ret
    ret = dtssystem_async("for ((i=0; i<8; i++)); do echo $i; sleep 0.5; done", loglevel="info", pflag=True)    # �����pid����cmd���
    print "pid:", ret

if __name__ == "__main__":
    dlog.set_sh_debug()
    
    print "="*4 + "test dtssystem" + "="*4
    _test_dtssystem()
    
    print
    print "="*4 + "test dtssystem_output" + "="*4
    _test_dtssystem_output()
    
    print
    print "="*4 + "test dtssystem_async" + "="*4
    _test_dtssystem_async()

