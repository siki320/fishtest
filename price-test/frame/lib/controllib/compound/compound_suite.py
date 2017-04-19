# -*- coding: GB18030 -*-
'''
Created on Mar 14, 2012

@author: caiyifeng<caiyifeng>
Rewrite from maqi

@summary: ���Ϸ�ʽ����ִ��case
'''

from frame.lib.controllib.suite import DtestSuite
from frame.lib.commonlib.dlog import dlog
from frame.lib.controllib.result import CaseResult

from frame.lib.controllib.normal.normal_case import NormalCase
from frame.lib.controllib.normal.normal_suite import NormalSuite

from frame.lib.controllib.bigenv.bigenv_case import BigenvCase
from frame.lib.controllib.bigenv.bigenv_suite import BigenvSuite

from frame.lib.controllib.reload.reload_case import ReloadCase
from frame.lib.controllib.reload.reload_suite import ReloadSuite


class CompoundSuite(DtestSuite):
    def __init__(self):
        super(CompoundSuite, self).__init__()
        
        self.sub_suite_dispatch_dict = {}   # <suite_name_string, suite obj>�ֵ�
        self.sub_suite_list = []            # (suite_name_string, suite_obj)Ԫ���б�˳��ִ��
        self.is_weak=False

    def run_suite(self, result):
        '''
        @summary: ����compound suite
        @param result: DResult����
        '''
        # ��ʼ��sub suite���ȷ���
        dlog.info("Compound suite: init sub suite dispatch")
        self._init_sub_suite_dispatch(result)
        
        # ִ������sub suite
        for item in self.sub_suite_list:
            suite_name, suite_obj = item
            suite_obj.set_weak(self.is_weak)
            self.log_start_line(suite_name)
            suite_obj.run_suite(result)
            self.log_end_line(suite_name)

    def set_weak(self, flag):
        '''
        @summary: ����weak���з�ʽ
        @param flag: �Ƿ�weak����
        '''
        self.is_weak = flag
            
    def _init_sub_suite_dispatch(self, result):
        '''
        @summary: ��suite���ȷ������
        '''
        for acase in self.caselist:
            suite_class = self._get_suite_class(acase, result)
            if not suite_class:
                continue
            
            if suite_class.__name__ not in self.sub_suite_dispatch_dict:
                # ��û������suite������֮
                suite_obj = suite_class()
                self.sub_suite_dispatch_dict[suite_class.__name__] = suite_obj
                self.sub_suite_list.append((suite_class.__name__, suite_obj))
                
            # ����Ӧ��suite������case��test
            suite_obj = self.sub_suite_dispatch_dict[suite_class.__name__]
            suite_obj.addcase(acase)
            suite_obj.add_test_dict(acase, self.testdict[acase])

    def _get_suite_class(self, acase, result):
        '''
        @summary: ����case����, ����suite_class; ���case���ͷǷ�������None
        @param acase������ʵ��
        @param result: DResult����
        '''
        if isinstance(acase, NormalCase):
            return NormalSuite
        elif isinstance(acase, BigenvCase):
            return BigenvSuite
        elif isinstance(acase, ReloadCase):
            return ReloadSuite
        else:
            # ����Ԥ�ڵ�case���ͣ��Ǵ�
            dlog.error("Unknown case type '%s' for case: %s", type(acase).__mro__, acase.get_relpath())
            result.case_result_dict[acase.filepath] = CaseResult(result.FAILED, "Unknown_Type")
            return None
        
    
    def log_start_line(self, suite_name):
        '''
        @summary: �����ʼ��Ϣ��
        '''
        logstr = "#"*8 + "    Start Suite : " + suite_name + "    " + "#"*8

        dlog.info("")
        dlog.info("#" * len(logstr))
        dlog.info(logstr)
        dlog.info("#" * len(logstr))
        
    def log_end_line(self, suite_name):
        '''
        @summary: ���������Ϣ��
        '''
        logstr = "*"*8 + "    End Suite : " + suite_name + "    " + "*"*8
        
        dlog.info("*" * len(logstr))
        dlog.info(logstr)
        dlog.info("*" * len(logstr))
        dlog.info("")

