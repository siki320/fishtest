#coding=gb18030
'''
created on Apr 17, 2012
@author : maqi (maqi)
'''

from frame.lib.commonlib.dtssystem import dtssystem,dtssystem_async

class XDSystem(object):
    '''
    @note:封装命令行执行
    '''
    def __init__(self,log):
        '''
        @note:从外面得到一个log对象
        '''
        self.log = log

    def xd_system(self, cmd, output=False, loglevel='info', pflag=False):
        return dtssystem(cmd=cmd, output=output, loglevel=loglevel, pflag=pflag, logger=self.log)

    def xd_system_async(self, cmd, loglevel='info', pflag=False):
        return dtssystem_async(cmd=cmd, loglevel=loglevel, pflag=pflag, logger=self.log)
