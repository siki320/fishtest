# -*- coding: GB18030 -*-
'''
Created on Mar 26, 2013

@author: liqiuhua<liqiuhua>

@summary: 总体框架的基类
'''

from frame.lib.commonlib.dlog import dlog
from frame.lib.controllib.sysframe.syspickcase import SysCasePicker
from frame.lib.controllib.sysframe.syssuitefactory import SysSuiteFactory

class SysFrameMain(object):
    def __init__(self, result, logdir):
        self.suiteplug_path = None # 使用系统默认的path sysframe/suiteplug
        self.result = result
        self.logdir = logdir
        self.deploy_mode = "FULL"
        self.xstp_mode = False
        self.conf_file = ""

    def set_suiteplug_path(self, plug_path):
        self.suiteplug_path = plug_path

    def set_deploymode(self, mode):
        self.deploy_mode = mode

    def set_xstpmode(self, mode):
        self.xstp_mode = mode

    def set_conf_file(self, conf_file):
        self.conf_file = conf_file

    def execute(self, args):
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

        # 构造picker对象
        self.picker = SysCasePicker()

        # 构造suite Factory
        self.suite_factory = SysSuiteFactory(self.suiteplug_path)

        # 将args中的DtestCase加入suite
        self.picker.pickcases(args, self.suite_factory, self.result)

        # 执行suite
        self.suite_factory.run_suites(self.result, self.conf_file, self.deploy_mode, self.xstp_mode)

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
