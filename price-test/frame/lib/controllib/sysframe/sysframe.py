# -*- coding: GB18030 -*-
'''
Created on Mar 26, 2013

@author: liqiuhua<liqiuhua>

@summary: �����ܵĻ���
'''

from frame.lib.commonlib.dlog import dlog
from frame.lib.controllib.sysframe.syspickcase import SysCasePicker
from frame.lib.controllib.sysframe.syssuitefactory import SysSuiteFactory

class SysFrameMain(object):
    def __init__(self, result, logdir):
        self.suiteplug_path = None # ʹ��ϵͳĬ�ϵ�path sysframe/suiteplug
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
        @summary: �����з���
        @param arg: case·�����������ļ�����Ҳ������Ŀ¼
        @return: 
         - ��ȷʱ���� 0
         - �д���ʱ���� 255
        '''
        # �����ʼ��־
        dlog.info("Start DTS")
        # ��¼��ʼʱ��
        self.result.alltime.start()

        # ����picker����
        self.picker = SysCasePicker()

        # ����suite Factory
        self.suite_factory = SysSuiteFactory(self.suiteplug_path)

        # ��args�е�DtestCase����suite
        self.picker.pickcases(args, self.suite_factory, self.result)

        # ִ��suite
        self.suite_factory.run_suites(self.result, self.conf_file, self.deploy_mode, self.xstp_mode)

        # ��¼����ʱ��
        self.result.alltime.end()

        # �õ����
        self.result.log_case_summary(self.logdir+"/result.txt")

        # ������
        ret = self.result.get_total_result()
        if not ret:
            # ��case���󣬷��ش�����
            dlog.error("DTS return code 255")
            return 255

        dlog.success("DTS return code 0")
        return 0
