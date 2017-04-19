# -*- coding: GB18030 -*-
'''
Created on Nov 22, 2011

@author: caiyifeng<caiyifeng>

@summary: 总体框架的基类
'''

from frame.lib.commonlib.dlog import dlog

class FrameMain(object):
    def __init__(self, picker, suite, result, logdir):
        self.picker = picker
        self.suite = suite
        self.result = result
        self.logdir = logdir
        
    def execute(self, arg):
        '''
        @summary: 主运行方法
        @param arg: case路径，可以是文件名，也可以是目录
        @return: 
         - 正确时返回 0
         - 有错误时返回 255
        '''
        # 输出起始日志
        dlog.info("Start DTS")
        
        # 记录起始时间
        self.result.alltime.start()
        
        # 将args中的DtestCase加入suite
        self.picker.pickcases(arg, self.suite, self.result)
        
        # 执行suite
        self.suite.run_suite(self.result)
        
        # 记录结束时间
        self.result.alltime.end()
        
        # 得到结果
        self.result.log_case_summary(self.logdir+"/result.txt")
        
        # 返回码
        ret = self.result.get_total_result()
        if not ret:
            # 有case错误，返回错误码
            dlog.error("DTS return code 255")
            return 255
            
        dlog.success("DTS return code 0")
        return 0
