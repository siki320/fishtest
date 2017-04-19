# -*- coding: GB18030 -*-
'''
Created on Nov 22, 2011

@author: caiyifeng<caiyifeng>

@summary: �����ܵĻ���
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
        
        # ��args�е�DtestCase����suite
        self.picker.pickcases(arg, self.suite, self.result)
        
        # ִ��suite
        self.suite.run_suite(self.result)
        
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
