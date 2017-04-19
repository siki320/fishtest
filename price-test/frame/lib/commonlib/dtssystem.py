# -*- coding: GB18030 -*-
'''
Created on Aug 10, 2011

@author: caiyifeng<caiyifeng>

@attention: 接口参数较多。希望精简接口的，建议使用dtssystem2模块

@summary: 
 - Bash命令行调用
 - 托管命令行调用的输出，避免和日志冲突
'''

import sys
import subprocess
import fcntl
import os
import select
from frame.lib.commonlib.dlog import dlog


def dtssystem(cmd, output=False, loglevel=None, errlevel="warning", prompt="Run cmd", pflag=False, logger=dlog):
    '''
    @summary: (阻塞)调用shell命令cmd
    @attention: 如果要后台启动程序，请使用dtssystem_async()
    
    @param output: 
     - 为True时，返回cmd的 (return code, stdout output, stderr output)
     - 为False时，只返回cmd的return code。命令的输出被重定向到/dev/null
    
    @param loglevel: 
     - 可以为None, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - 不为None时，执行的cmd被记入日志
    
    @param errlevel: 
     - 可以为None, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - 不为None时，当cmd返回码不为0，则记录日志
    
    @param pflag: print flag。为True时打印cmd的屏幕输出
    
    @param logger: log object。默认为dlog
    
    @param prompt: 日志提示符
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
    @summary: 后台运行shell命令cmd
    
    @param loglevel: 
     - 可以为None, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - 不为None时，执行的cmd被记入日志
     
    @param prompt: 日志提示符
    
    @param pflag: print flag。为True时打印cmd的屏幕输出
    
    @param logger: log object。默认为dlog
    
    @return: 返回cmd的pid
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
    '''@return: 返回(return code, stdout output, stderr output)'''
    outdata_l = []
    errdata_l = []
    
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    # stderr必须是单独的PIPE
    
    # 将proc的stdout和stderr设置为非阻塞
    for f in [proc.stdout, proc.stderr]:
        flags = fcntl.fcntl(f, fcntl.F_GETFL)
        fcntl.fcntl(f, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    
    while True:
        # 轮询
        ret = proc.poll()
        r, w, x = select.select([proc.stdout, proc.stderr], [], [], 1)     # 阻塞最多1s。EOF也被linux认为有输出
        
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
            # cmd结束
            break
        
    outdata = "".join(outdata_l)
    errdata = "".join(errdata_l)
        
    if ret != 0 and err_func:
        # cmd返回码不为0
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
    ret = dtssystem("for ((i=0; i<8; i++)); do echo $i; sleep 0.5; done", loglevel="info", pflag=True)  # cmd输出完，输出ret
    print "ret:", ret
    
def _test_dtssystem_output():
    ret = dtssystem("echo '12345' > a.txt", output=True, loglevel="debug")
    print "ret:", ret
    ret = dtssystem("rm a.txt b.txt", output=True, loglevel="debug", prompt="Remove files")
    print "ret:", ret
    ret = dtssystem("for ((i=0; i<8; i++)); do echo $i; echo 100$i >&2; sleep 0.5; done", output=True, loglevel="info", pflag=True)  # cmd输出完，输出ret
    print "ret:", ret
    
def _test_dtssystem_async():
    ret = dtssystem_async("echo '12345' > a.txt", loglevel="debug")
    print "pid:", ret
    ret = dtssystem_async("rm a.txt b.txt", loglevel="debug", prompt="Remove files")
    print "pid:", ret
    ret = dtssystem_async("for ((i=0; i<8; i++)); do echo $i; sleep 0.5; done", loglevel="info", pflag=True)    # 先输出pid，后cmd输出
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

