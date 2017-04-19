# -*- coding: GB18030 -*-
'''
Created on Apr 18, 2012

@author: caiyifeng<caiyifeng>

@summary: 
 - ������dtssystemģ��Ľӿ�
 - �ڲ�ʵ�ָ���dtssystemģ��
'''

from frame.lib.commonlib import dtssystem as xs
from frame.lib.commonlib.dlog import dlog


def dtssystem(cmd, errfunc=dlog.warning, pflag=False):
    '''@summary: ������������shell����
    @param errfunc: cmd����ֵ��Ϊ0ʱ�����msg�ĺ��� errfunc(msg)��ΪNoneʱ�����
    @param pflag: print flag��ΪTrueʱ��ӡcmd����Ļ���
    @return: cmd����ֵ'''
    return xs._dtssystem_output(cmd, errfunc, "Run cmd", pflag)[0]


def dtssystem_out(cmd, errfunc=dlog.warning, pflag=False):
    '''@summary: (����)����shell���������cmd����Ļ���
    @param errfunc: cmd����ֵ��Ϊ0ʱ�����msg�ĺ��� errfunc(msg)��ΪNoneʱ�����
    @param pflag: print flag��ΪTrueʱ��ӡcmd����Ļ���
    @return: ��Ԫ�飨cmd����ֵ��cmd stdout, cmd stderr��'''
    return xs._dtssystem_output(cmd, errfunc, "Run cmd", pflag)


def dtssystem_async(cmd, pflag=False):
    '''@summary: ��̨����shell����cmd
    @param pflag: print flag��ΪTrueʱ��ӡcmd����Ļ���
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
    ret = dtssystem(cmd, pflag=True)  # cmd����꣬���ret
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
    ret = dtssystem_out(cmd, pflag=True)  # cmd����꣬���ret
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
    ret = dtssystem_async(cmd, pflag=True)    # �����pid����cmd���
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
