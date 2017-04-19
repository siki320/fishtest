# -*- coding: GB18030 -*-
'''
Created on Apr 18, 2012

@author: caiyifeng<caiyifeng>

@summary: 
 - 精简了dtssystem模块的接口
 - 内部实现复用dtssystem模块
'''

from frame.lib.commonlib import dtssystem as xs
from frame.lib.commonlib.dlog import dlog


def dtssystem(cmd, errfunc=dlog.warning, pflag=False):
    '''@summary: （阻塞）调用shell命令
    @param errfunc: cmd返回值不为0时，输出msg的函数 errfunc(msg)。为None时不输出
    @param pflag: print flag。为True时打印cmd的屏幕输出
    @return: cmd返回值'''
    return xs._dtssystem_output(cmd, errfunc, "Run cmd", pflag)[0]


def dtssystem_out(cmd, errfunc=dlog.warning, pflag=False):
    '''@summary: (阻塞)调用shell命令，并返回cmd的屏幕输出
    @param errfunc: cmd返回值不为0时，输出msg的函数 errfunc(msg)。为None时不输出
    @param pflag: print flag。为True时打印cmd的屏幕输出
    @return: 三元组（cmd返回值，cmd stdout, cmd stderr）'''
    return xs._dtssystem_output(cmd, errfunc, "Run cmd", pflag)


def dtssystem_async(cmd, pflag=False):
    '''@summary: 后台运行shell命令cmd
    @param pflag: print flag。为True时打印cmd的屏幕输出
    @return: cmd pid'''
    return xs.dtssystem_async(cmd, pflag=pflag)


def _test_dtssystem():
    cmd = "echo '12345' > a.txt"
    print cmd
    ret = dtssystem(cmd)
    print "ret:", ret
    
    print
    cmd = "rm a.txt b.txt"
    print cmd
    ret = dtssystem(cmd)
    print "ret:", ret
    
    print
    cmd = "for ((i=0; i<8; i++)); do echo $i; echo 100$i >&2; sleep 0.5; done"
    print cmd
    ret = dtssystem(cmd, pflag=True)  # cmd输出完，输出ret
    print "ret:", ret
    
def _test_dtssystem_out():
    cmd = "echo '12345' > a.txt"
    print cmd
    ret = dtssystem_out(cmd)
    print "ret:", ret
    
    print
    cmd = "rm a.txt b.txt"
    print cmd
    ret = dtssystem_out(cmd)
    print "ret:", ret
    
    print
    cmd = "for ((i=0; i<8; i++)); do echo $i; echo 100$i >&2; sleep 0.5; done"
    print cmd
    ret = dtssystem_out(cmd, pflag=True)  # cmd输出完，输出ret
    print "ret:", ret
    
def _test_dtssystem_async():
    cmd = "echo '12345' > a.txt"
    print cmd
    ret = dtssystem_async(cmd)
    print "pid:", ret
    
    print
    cmd = "rm a.txt b.txt"
    print cmd
    ret = dtssystem_async(cmd)
    print "pid:", ret
    
    print
    cmd = "for ((i=0; i<8; i++)); do echo $i; echo 100$i >&2; sleep 0.5; done"
    print cmd
    ret = dtssystem_async(cmd, pflag=True)    # 先输出pid，后cmd输出
    print "pid:", ret
    
if __name__ == "__main__":
    print "="*4 + "test dtssystem" + "="*4
    _test_dtssystem()
    
    print
    print "="*4 + "test dtssystem_out" + "="*4
    _test_dtssystem_out()
    
    print
    print "="*4 + "test dtssystem_async" + "="*4
    _test_dtssystem_async()
