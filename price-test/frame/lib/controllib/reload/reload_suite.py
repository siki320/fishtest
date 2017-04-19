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
    '''@summary: 挨个运行case'''
    def __init__(self):
        super(ReloadSuite, self).__init__()

        self.is_weak = False        # 是否一遇到case fail就退出

    def set_weak(self, flag):
        self.is_weak = flag


    def run_suite(self, result):
        '''@param result: DResult对象'''

        # 执行每种plugin的全局初始化
        self._do_global_init(result)

        # 初始化所有case的time字典
        self._init_case_time(result)

        # 执行所有case
        self._run_cases(result)

        # 执行每种plugin的全局destroy
        self._do_global_destroy(result)

    def _init_case_time(self, result):
        '''@summary: 初始化所有case的time字典'''
        for acase in self.caselist:
            result.case_time_dict[acase.filepath] = Timer()

    def _run_cases(self, result):
        for acase in self.caselist:
            # 运行Case
            #acase.log_start_line()
            result.case_time_dict[acase.filepath].start()
            result.case_result_dict[acase.filepath] = acase      #result为case对象
            acase.start_log_record()
            ret = acase.run()
            acase.stop_log_record()
            result.case_time_dict[acase.filepath].end()
            #acase.log_end_line()
            if not ret and self.is_weak:
                dlog.critical("I meet a failure, I'm weak, so I quit")
                # 如果is weak，直接退出
                return False

    def _do_global_init(self, result):
        '''@summary: 执行每种plugin的全局初始化
        @param result: DResult对象
        @attention: 当某一种类型的plugin do init失败时，将所有这类case从case_list中去除'''
        # 1. 归并相同plugin的case
        plugin_case_list = self._merge_plugin_case()

        # 2. 对每种plugin，执行global_init
        # 同时记录成功的case list
        new_case_list = []
        for mp_type, clist in plugin_case_list:
            try:
                mp_type().global_init()
            except Exception:
                dlog.error("Module Plugin %s global_init failed. Ignore all related cases", mp_type, exc_info=True)
                result.case_result_dict["%s_Global_Init" % mp_type.__name__] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())
            else:
                new_case_list.extend(clist)

        # 3. 更新case_list
        self.caselist = new_case_list

    def _do_global_destroy(self, result):
        '''@summary: 执行每种plugin的全局destroy
        @param result: DResult对象'''
        # 1. 归并相同plugin的case
        plugin_case_list = self._merge_plugin_case()

        # 2. 对每种case类型，执行global_destroy
        for mp_type, _ in plugin_case_list:
            try:
                mp_type().global_destroy()
            except Exception:
                dlog.error("Module Plugin %s global_destroy failed", mp_type, exc_info=True)
                result.case_result_dict["%s_Global_Destroy" % mp_type.__name__] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())

    def _merge_plugin_case(self):
        '''@summary: 归并相同plugin的case
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
