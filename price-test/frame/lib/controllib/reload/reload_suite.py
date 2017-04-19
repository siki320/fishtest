# -*- coding: GB18030 -*-
'''
Created on Nov 30, 2011

@author: liqiuhua<liqiuhua>
'''
import traceback
from frame.lib.controllib.suite import DtestSuite
from frame.lib.controllib.result import CaseResult

from frame.lib.commonlib.timer import Timer
from frame.lib.commonlib.dlog import dlog


class ReloadSuite(DtestSuite):
    '''@summary: ��������case'''
    def __init__(self):
        super(ReloadSuite, self).__init__()

        self.is_weak = False        # �Ƿ�һ����case fail���˳�

    def set_weak(self, flag):
        self.is_weak = flag


    def run_suite(self, result):
        '''@param result: DResult����'''

        # ִ��ÿ��plugin��ȫ�ֳ�ʼ��
        self._do_global_init(result)

        # ��ʼ������case��time�ֵ�
        self._init_case_time(result)

        # ִ������case
        self._run_cases(result)

        # ִ��ÿ��plugin��ȫ��destroy
        self._do_global_destroy(result)

    def _init_case_time(self, result):
        '''@summary: ��ʼ������case��time�ֵ�'''
        for acase in self.caselist:
            result.case_time_dict[acase.filepath] = Timer()

    def _run_cases(self, result):
        for acase in self.caselist:
            # ����Case
            #acase.log_start_line()
            result.case_time_dict[acase.filepath].start()
            result.case_result_dict[acase.filepath] = acase      #resultΪcase����
            acase.start_log_record()
            ret = acase.run()
            acase.stop_log_record()
            result.case_time_dict[acase.filepath].end()
            #acase.log_end_line()
            if not ret and self.is_weak:
                dlog.critical("I meet a failure, I'm weak, so I quit")
                # ���is weak��ֱ���˳�
                return False

    def _do_global_init(self, result):
        '''@summary: ִ��ÿ��plugin��ȫ�ֳ�ʼ��
        @param result: DResult����
        @attention: ��ĳһ�����͵�plugin do initʧ��ʱ������������case��case_list��ȥ��'''
        # 1. �鲢��ͬplugin��case
        plugin_case_list = self._merge_plugin_case()

        # 2. ��ÿ��plugin��ִ��global_init
        # ͬʱ��¼�ɹ���case list
        new_case_list = []
        for mp_type, clist in plugin_case_list:
            try:
                mp_type().global_init()
            except Exception:
                dlog.error("Module Plugin %s global_init failed. Ignore all related cases", mp_type, exc_info=True)
                result.case_result_dict["%s_Global_Init" % mp_type.__name__] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())
            else:
                new_case_list.extend(clist)

        # 3. ����case_list
        self.caselist = new_case_list

    def _do_global_destroy(self, result):
        '''@summary: ִ��ÿ��plugin��ȫ��destroy
        @param result: DResult����'''
        # 1. �鲢��ͬplugin��case
        plugin_case_list = self._merge_plugin_case()

        # 2. ��ÿ��case���ͣ�ִ��global_destroy
        for mp_type, _ in plugin_case_list:
            try:
                mp_type().global_destroy()
            except Exception:
                dlog.error("Module Plugin %s global_destroy failed", mp_type, exc_info=True)
                result.case_result_dict["%s_Global_Destroy" % mp_type.__name__] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())

    def _merge_plugin_case(self):
        '''@summary: �鲢��ͬplugin��case
        @return: (plugin_type, case list) list'''
        plugin_case_dict = {}   # <plugin_type, case list> dict
        plugin_case_list = []   # (plugin_type, case list) list

        for acase in self.caselist:
            mp_type = acase.mp.__class__

            if mp_type not in plugin_case_dict:
                clist = []
                plugin_case_dict[mp_type] = clist
                plugin_case_list.append( (mp_type, clist) )

            plugin_case_dict[mp_type].append(acase)

        return plugin_case_list
