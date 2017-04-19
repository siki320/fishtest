# -*- coding: GB18030 -*-
'''
Created on Nov 9, 2011

@author: caiyifeng<caiyifeng>

@summary: ��ͨ��ʽ��˳�򣩵���ִ��case
'''

import traceback

from frame.lib.controllib.suite import DtestSuite
from frame.lib.controllib.result import CaseResult

from frame.lib.commonlib.timer import Timer
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.safe_encode import safegb
from frame.tools.cov.func_cov import Cov_Global

class NormalSuite(DtestSuite):
    '''@summary: ��������case'''
    def __init__(self):
        super(NormalSuite, self).__init__()

        self.is_weak = False        # �Ƿ�һ����case fail���˳�

        # �����Զ���λ
        self.do_errlocate = False
        self.errlocate_result = None

    def set_weak(self, flag):
        self.is_weak = flag

    def set_error_locate(self, errlocate_result):
        self.do_errlocate = True
        self.errlocate_result = errlocate_result


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
            # ���module plugin
            plugin = acase.mp
            dlog.debug("Use Plugin : %s", type(plugin))

            # =================== STEP 1 ===================
            # ���ɻ�׼����
            try:
                plugin.benchmark_env()
            except Exception:
                # ��׼������ʧ��
                dlog.critical("Benchmark Failed. Framework Quits", exc_info=True)
                result.case_result_dict["Framework_Environment"] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())

                # ֱ���˳�
                return


            # =================== STEP 2 ===================
            # ����case��setup_env����
            result.case_time_dict[acase.filepath].start()
            try:
                acase.setup_env()
            except Exception:
                # setup_env����
                dlog.error("Case Failed: %s", acase.get_relpath(), exc_info=True)
                result.case_result_dict[acase.filepath] = CaseResult(result.FAILED, "setup_env",
                                                                            caseobj=acase, exc_stack=traceback.format_exc())

                # ���is weak��ֱ���˳�
                if self.is_weak:
                    dlog.critical("I meet a failure, I'm weak, so I quit")
                    return

                # �������case
                continue
            finally:
                result.case_time_dict[acase.filepath].end()

            try:
                # =================== STEP 3 ===================
                # �������Ի���
                result.case_time_dict[acase.filepath].start()
                try:
                    plugin.clean_error()

                    plugin.startup_env()
                    plugin.common_check(acase)
                except Exception:
                    # ��������ʧ��
                    dlog.error("Startup Env Failed: %s", acase.get_relpath(), exc_info=True)
                    result.case_result_dict[acase.filepath] = CaseResult(result.FAILED, "StartupEnv",
                                                                                caseobj=acase, exc_stack=traceback.format_exc())

                    # ��������Ϣ
                    keyinfo = plugin.diagnose_error()
                    # ������󻷾�
                    plugin.bak_failed_env( acase.get_relpath()+".env" )

                    # �����Զ���λ
                    if self.do_errlocate:
                        if not keyinfo:
                            raise Exception, "Do Error Locate needs keyinfo returned by diagnose_error()"

                        keyinfo.cases.append(acase)
                        keyinfo.failed_step = 'START'
                        keyinfo.startException = safegb(traceback.format_exc())
                        self.errlocate_result.add_failed_info(keyinfo)

                    # ���is weak��ֱ���˳�
                    if self.is_weak:
                        dlog.critical("I meet a failure, I'm weak, so I quit")
                        return

                    # �������case
                    continue
                finally:
                    result.case_time_dict[acase.filepath].end()


                # =================== STEP 4 ===================
                # ����Case
                ret = self._run_one_case(acase, plugin, result)
                if not ret and self.is_weak:
                    # ���is weak��ֱ���˳�
                    dlog.critical("I meet a failure, I'm weak, so I quit")
                    return

            finally:
                # ��Step 3��ʼ������case����ȷִ���꣬���Ǵ����µ�return �� continue������ִ��finally
                # ֹͣ����
                try:
                    plugin.stop_env()
                except Exception:
                    # ֹͣ����ʧ��
                    dlog.critical("Stop Env Failed. Framework Quits", exc_info=True)
                    result.case_result_dict["Stop_Environment"] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())

                    # ֱ���˳�
                    return

    def _run_one_case(self, acase, plugin, result):
        #record the runtime log
        acase.start_log_record()

        # ����Case
        acase.log_start_line()
        result.case_time_dict[acase.filepath].start()

        try:
            acase.setup_testcase()
            testlist = self.testdict[acase]

            r = CaseResult(result.PASS, "", caseobj=acase)   # Ԥ������case�Ľ����pass
            result.case_result_dict[acase.filepath] = r

            test_idx = 0
            test_num = len(testlist)
            retry_count = 0 # ���Դ���
            while test_idx < test_num:
                # ����acase������test����
                atest = testlist[test_idx]
                test_idx += 1 #����ָ����һ��case
                try:
                    plugin.clean_error()
                    if Cov_Global.func_cov_mode:
                        plugin.init_cov()
                    atest()

                    plugin.common_check(acase)    # �������

                except Exception:
                    dlog.error("Test Failed: %s.%s", acase.get_relpath(), atest.__name__, exc_info=True)
                    if hasattr(plugin,"fail_retry") and plugin.fail_retry(retry_count,acase,atest):
                        retry_count += 1
                        dlog.info("Test Retry %d: %s.%s", retry_count, acase.get_relpath(), atest.__name__)
                        test_idx -= 1 #��������,case�����ָ��ɵ�ǰcase
                        continue

                    retry_count = 0 # ���Դ�����λ
                    r.result = result.FAILED                            # testʧ�ܣ�ֱ������case fail
                    r.add_failed_test(atest, traceback.format_exc())    # ����ʧ�ܵ�test

                    # ��������Ϣ
                    keyinfo = plugin.diagnose_error()
                    # ������󻷾�
                    plugin.bak_failed_env(acase.get_relpath() + ".evn/" + atest.__name__)

                    # �����Զ���λ
                    if self.do_errlocate:
                        if not keyinfo:
                            raise Exception, "Do Error Locate needs keyinfo returned by diagnose_error()"

                        keyinfo.cases.append(acase)
                        keyinfo.failed_step = atest.__name__
                        keyinfo.testException = safegb(traceback.format_exc())
                        self.errlocate_result.add_failed_info(keyinfo)

                    # ���is weak��ֱ�ӷ��ش���
                    if self.is_weak:
                        return False

                else:
                    if retry_count>0: #ͨ������ͨ����case
                        dlog.warning("After retry, %s.%s successed",acase.get_relpath(), atest.__name__)
                    if Cov_Global.func_cov_mode:
                        plugin.bak_cov(acase.get_relpath() + ":" + atest.__name__)
                    dlog.success("Test Succeeded: %s.%s", acase.get_relpath(), atest.__name__)
                    r.add_passed_test(atest)       # ���ӳɹ���test

        except Exception:
            dlog.error("Case Failed: %s", acase.get_relpath(), exc_info=True)
            result.case_result_dict[acase.filepath] = CaseResult(result.FAILED, "",
                                                                        caseobj=acase, exc_stack=traceback.format_exc())

            # ���ش���
            return False

        finally:
            result.case_time_dict[acase.filepath].end()
            acase.log_end_line()
            acase.stop_log_record()
            result.case_result_dict[acase.filepath].add_log_record(acase.log_stream.getvalue())

        # ������ȷ
        return True


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
