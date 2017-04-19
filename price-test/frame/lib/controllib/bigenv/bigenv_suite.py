# -*- coding: GB18030 -*-
'''
Created on Nov 11, 2011

@author: caiyifeng<caiyifeng>

@summary: ��ⷽʽ����ִ��case
'''

import os
import traceback

from frame.lib.controllib.suite import DtestSuite

from frame.lib.commonlib.timer import Timer
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.safe_encode import safegb
from frame.lib.controllib.result import CaseResult
from frame.lib.commonlib import vgutils, coverutils
from frame.tools.cov.func_cov import Cov_Global

class BigenvSuite(DtestSuite):
    '''@summary: �������case'''
    def __init__(self):
        super(BigenvSuite, self).__init__()

        self.is_weak = False        # �Ƿ�һ����case fail���˳�
        self.is_single = False      # case�Ƿ񵥶�����

        self.case_dispatch = []     # caseִ�еĵ��ȡ�ÿ��Ԫ����list��list�е�case��������
        self.row_num = 0            # case������
        self.is_iter_case = False   # �Ƿ������������

        # �����Զ���λ
        self.do_errlocate = False
        self.errlocate_result = None

    def setIterCase(self,flag):
        self.is_iter_case = flag

    def set_weak(self, flag):
        self.is_weak = flag

    def set_single(self, flag):
        self.is_single = flag

    def set_error_locate(self, errlocate_result):
        self.do_errlocate = True
        self.errlocate_result = errlocate_result


    def run_suite(self, result):
        '''@param result: DResult����'''
        # ִ��ÿ��plugin��ȫ�ֳ�ʼ��
        self._do_global_init(result)

        # ��ʼ������case��time�ֵ�
        self._init_case_time(result)

        # ��ʼ��caseִ��˳��
        self._init_case_dispatch()

        # ִ������case
        self._run_cases(result)

        # ׷�Ӹ���result���
        result.add_property('bigenv_row_number', self.row_num)

        # ִ��ÿ��plugin��ȫ��destroy
        self._do_global_destroy(result)

    def _init_case_time(self, result):
        '''@summary: ��ʼ������case��time�ֵ�'''
        for acase in self.caselist:
            result.case_time_dict[acase.get_relpath()] = Timer()

    def _init_case_dispatch(self):
        '''@summary: ��ʼ��caseִ��˳��'''
        isall_cases = []     # isallΪTrue��case
        separate_cases = []  # isallΪFalse��case
        for acase in self.caselist:
            if acase.isall:
                isall_cases.append(acase)
            else:
                separate_cases.append(acase)

        # ����isall_cases
        if self.is_single:
            # ���suite��--singleģʽ, �򵥶�����
            self.case_dispatch.extend([[acase] for acase in isall_cases])
        else:
            # ���suite����--singleģʽ����(dir, casetype)����

            # �½�dir_case_dict
            dir_case_dict = {}
            dir_case_list = []  # ����case dir��˳��
            for acase in isall_cases:
                # key: caseĿ¼ + case����suite name + case�����б�
                casedir = os.path.dirname(acase.filepath)
                key = (casedir, acase.attached_suite_name) + acase.get_case_type()

                if key not in dir_case_dict:
                    dir_case_dict[key] = []
                    dir_case_list.append(key)

                dir_case_dict[key].append(acase)

            # ��dir����
            self.case_dispatch.extend([dir_case_dict[key] for key in dir_case_list])

        # ��seperate_cases��������
        self.case_dispatch.extend([[acase] for acase in separate_cases])

    def _run_cases(self, result):
        '''@summary: �����������е�case'''
        for case_serial in self.case_dispatch:
            # ����ÿһ��case_serial
            caseNum = len(case_serial)
            caseIdx = 0

            while caseIdx < caseNum:
                # ��������case_serial

                # ���module plugin
                plugin = case_serial[0].mp_cls()
                dlog.debug("Use Plugin : %s", type(plugin))

                result.plugin_bench_timer.start()
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
                finally:
                    result.plugin_bench_timer.end()


                # =================== STEP 2 ===================
                # �ҵ�һ��case��������
                # ��������case��setup_env������ֱ��Generator�þ�
                run_case_list = []
                while caseIdx < caseNum:
                    acase = case_serial[caseIdx]
                    #bigenv caseҲ���Ի�ȡ�������
                    acase.mp = plugin
                    result.case_time_dict[acase.get_relpath()].start()
                    try:
                        acase.setup_env()

                        # setup_env�ɹ�
                        run_case_list.append(acase)
                        caseIdx += 1    # �����±�

                    except StopIteration:
                        # Generator�þ�������
                        if run_case_list:
                            # ǰ���Ѿ�������case�ˣ�˵����ǰcaseδ�س����������±�
                            dlog.info("Case '%s' Out of Generator", acase.get_relpath(), exc_info=True)
                        else:
                            # ��һ��case���þ���Generator�����case����
                            dlog.error("Case '%s' Failed: Run out of Generator", acase.get_relpath(), exc_info=True)
                            result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "Out_of_Generator",
                                                                                        caseobj=acase, exc_stack=traceback.format_exc())

                            # ���is weak��ֱ���˳�
                            if self.is_weak:
                                dlog.critical("I meet a failure, I'm weak, so I quit")
                                return

                            caseIdx += 1    # �����±꣬���������case

                        break

                    except Exception:
                        # setup_env��������
                        dlog.error("Case Failed: %s", acase.get_relpath(), exc_info=True)
                        result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "setup_env",
                                                                                    caseobj=acase, exc_stack=traceback.format_exc())

                        # ���is weak��ֱ���˳�
                        if self.is_weak:
                            dlog.critical("I meet a failure, I'm weak, so I quit")
                            return

                        caseIdx += 1    # �����±꣬���������case
                        break

                    finally:
                        result.case_time_dict[acase.get_relpath()].end()

                        if vgutils.is_running_valgrind():
                            vgutils.record_case_rel([acase.get_relpath() for acase in run_case_list])

                if run_case_list:
                    # ѡ����һ��case
                    dlog.info("Run cases in a row:\n%s", "\n".join([acase.get_relpath() for acase in run_case_list]) )
                    plugin.caselist = run_case_list
                else:
                    # û��ѡ��case
                    dlog.warning("No case in a row, continue")
                    continue

                try:
                    # =================== STEP 3 ===================
                    # �������Ի���
                    self.row_num += 1
                    result.plugin_startup_timer.start()
                    try:
                        plugin.clean_error()

                        plugin.startup_env()
                        plugin.common_check(run_case_list)
                    except Exception:
                        # ��������ʧ��
                        dlog.error("Startup Env Failed", exc_info=True)

                        # ��������Ϣ
                        keyinfo = plugin.diagnose_error()

                        # �����Զ���λ
                        if self.do_errlocate:
                            if not keyinfo:
                                raise Exception, "Do Error Locate needs keyinfo returned by diagnose_error()"

                            keyinfo.cases.extend([acase.filepath for acase in run_case_list])
                            keyinfo.failed_step = 'START'
                            keyinfo.startException = safegb(traceback.format_exc())
                            self.errlocate_result.add_failed_info(keyinfo)

                        # row�е�����case��Ϊfail
                        for i, acase in enumerate(run_case_list):
                            dlog.error("Set Case '%s' Failed", acase.get_relpath())
                            if i == 0:
                                result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "StartupEnv_Head",
                                                                                            caseobj=acase, exc_stack=traceback.format_exc())

                                # ������󻷾�
                                plugin.bak_failed_env( acase.get_relpath()+".env" )
                            else:
                                result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "StartupEnv",
                                                                                            caseobj=acase)

                        # ���is weak��ֱ���˳�
                        if self.is_weak:
                            dlog.critical("I meet a failure, I'm weak, so I quit")
                            return

                        # ��������case
                        continue
                    finally:
                        result.plugin_startup_timer.end()

                        # ��startup��ʱ��ƽ̯������case��
                        average_case_time = result.plugin_startup_timer.interval / len(run_case_list)
                        # ��bench��ʱ��ƽ̯������case��
                        average_case_time += result.plugin_bench_timer.interval / len(run_case_list)
                        for acase in run_case_list:
                            result.case_time_dict[acase.get_relpath()].totaltime += average_case_time

                        if vgutils.is_running_valgrind():
                            vgutils.record_case_rel([acase.get_relpath() for acase in run_case_list])

                    # =================== STEP 3.1 ===================
                    # ��������case��extraPrepare
                    candidate_list = []
                    for acase in run_case_list:
                        result.case_time_dict[acase.get_relpath()].start()
                        try:
                            acase.extraPrepare()
                            candidate_list.append(acase)
                        except Exception:
                            # setUpEnv��������
                            dlog.error("Case Failed: %s", acase.get_relpath(), exc_info = True)
                            result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "ExtraPrepare", \
                                    caseobj=acase, exc_stack=traceback.format_exc())

                            # ������󻷾�
                            plugin.bak_failed_env(acase.get_relpath() + ".env")

                            # ���is weak��ֱ���˳�
                            if self.is_weak:
                                dlog.critical("I meet a failure, I'm weak, so I quit")
                                return

                            break
                        finally:
                            result.case_time_dict[acase.get_relpath()].end()

                    run_case_list = candidate_list

                    # =================== STEP 3.2 ===================
                    # testplugin����extra_prepare
                    if not run_case_list:
                        continue

                    result.plugin_startup_timer.start()
                    try:
                        plugin.extra_prepare()
                    except Exception:
                        # ��������ʧ��
                        dlog.error("extra_prepare Failed", exc_info=True)

                        # row�е�����case��Ϊfail
                        for i, acase in enumerate(run_case_list):
                            dlog.error("Set Case '%s' Failed", acase.get_relpath())
                            result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "PluginExtraPrepare", \
                                        caseobj=acase, exc_stack=traceback.format_exc())

                            # ������󻷾�
                            plugin.bak_failed_env(acase.get_relpath() + ".env")

                        # ���is weak��ֱ���˳�
                        if self.is_weak:
                            dlog.critical("I meet a failure, I'm weak, so I quit")
                            return

                        # ��������case
                        continue
                    finally:
                        result.plugin_startup_timer.end()

                        # ��startup��ʱ��ƽ̯������case��
                        average_case_time = result.plugin_startup_timer.interval / len(run_case_list)
                        for acase in run_case_list:
                            result.case_time_dict[acase.get_relpath()].totaltime += average_case_time

                    # =================== STEP 4 ===================
                    # ��������case
                    for acase in run_case_list:
                        plugin.runcase = acase
                        result.case_time_dict[acase.get_relpath()].start()
                        ret = self._run_one_case(acase, plugin, result)
                        result.case_time_dict[acase.get_relpath()].end()
                        if not ret and self.is_weak:
                            # ���is weak��ֱ���˳�
                            dlog.critical("I meet a failure, I'm weak, so I quit")
                            return

                        coverutils.save_covinfo(acase.get_relpath())
                finally:
                    # ��Step 3��ʼ������case����ȷִ���꣬���Ǵ����µ�return �� continue������ִ��finally
                    # ֹͣ����
                    try:
                        plugin.stop_env()
                    except Exception:
                        # ֹͣ����ʧ��
                        dlog.critical("Stop Env Failed. Framework Quits", exc_info=True)
                        result.case_result_dict["Stop_Environment"] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())
                        plugin.bak_failed_env(acase.get_relpath() + ".env")

                        # ֱ���˳�
                        return

    def _run_one_case(self, acase, plugin, result):
        #record the runtime log
        acase.start_log_record()

        # ����Case
        acase.log_start_line()

        try:
            acase.setup_testcase()
            testlist = self.testdict[acase]

            r = CaseResult(result.PASS, "", caseobj=acase)   # Ԥ������case�Ľ����pass
            result.case_result_dict[acase.get_relpath()] = r

            test_idx = 0
            test_num = len(testlist)
            retry_count = 0 #���Դ���
            while test_idx < test_num:
                # ����acase������test����
                atest = testlist[test_idx]
                test_idx += 1 # ����ָ����һ��case
                try:
                    plugin.clean_error()
                    if Cov_Global.func_cov_mode:
                        plugin.init_cov()
                    atest()
                    plugin.common_check([acase])    # �������

                except Exception:
                    dlog.error("Test Failed: %s.%s", acase.get_relpath(), atest.__name__, exc_info=True)
                    if hasattr(plugin,"fail_retry") and plugin.fail_retry(retry_count,acase,atest):
                        retry_count += 1
                        dlog.info("Test Retry %d: %s.%s", retry_count, acase.get_relpath(), atest.__name__)
                        test_idx -= 1 #case����,�����ָ��ɵ�ǰcase
                        continue

                    retry_count = 0 #���Դ�����λ

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

                        keyinfo.cases.append(acase.filepath)
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
                    retry_count = 0 #���Դ�����λ

        except Exception:
            dlog.error("Case Failed: %s", acase.get_relpath(), exc_info=True)
            result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "",
                                                caseobj=acase, exc_stack=traceback.format_exc())
            # ��������Ϣ
            keyinfo = plugin.diagnose_error()
            # ������󻷾�
            plugin.bak_failed_env(acase.get_relpath() + ".env/")

            # ���ش���
            return False

        finally:
            try:
                acase.teardown_testcase()
            except:
                result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "", caseobj=acase, exc_stack=traceback.format_exc())
                dlog.error("TearDown testcase Failed", exc_info=True)
            finally:
                acase.log_end_line()
                if vgutils.is_running_valgrind():
                    vgutils.record_case_rel([acase.get_relpath()])

            acase.stop_log_record()
            result.case_result_dict[acase.get_relpath()].add_log_record(acase.log_stream.getvalue())
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
            mp_type = acase.mp_cls

            if mp_type not in plugin_case_dict:
                clist = []
                plugin_case_dict[mp_type] = clist
                plugin_case_list.append( (mp_type, clist) )

            plugin_case_dict[mp_type].append(acase)

        return plugin_case_list

    def _init_case_mt(self,result):
        for case_serial in self.case_dispatch: #ȡ��ͬһ�����е�case����
            self.mt_case_list = []
            for acase in case_serial :

                # ���caseû��mtFactory����, ˵��ʹ��д����������������,�˳�!
                if not hasattr(acase, 'mtFactory') :
                    continue

                # ���õ�һ��case���е���������
                acase.mtFactory.setMtIdx(0)

                if self.is_iter_case == False: #���û�������������, �˳�!
                    continue

                # �������Ĭ����������,��ʹ��Ĭ�������������м���,�˳�!
                if len(acase.mtFactory.mtlist) <= 1:
                    continue

                # ȡ����������ͼ�����һ��
                for i in range(1,len(acase.mtFactory.mtlist)):
                    xcase = acase.__class__() # �����������case��һ��ʵ��
                    xcase.set_filepath(acase.filepath)
                    xcase.mtFactory.setMtIdx(i)# �ı�����������
                    result.case_time_dict[xcase.get_relpath()] = Timer()
                    self.mt_case_list.append(xcase)

                    # �õ�case������testXXX����
                    f_tests = []
                    atestlist = self.testdict[acase]
                    for atest in atestlist: # ��õ�һ��ʵ����test�����б�
                        testStr = atest.__name__ # ��÷����ַ�����
                        xtest = getattr(xcase,testStr) # ���������ʵ����test����
                        f_tests.append(xtest)
                    # ��case��Ӧ��test��������suite
                    self.testdict[xcase] = f_tests
            case_serial.extend(self.mt_case_list) # �����Ƶ�����case����������

