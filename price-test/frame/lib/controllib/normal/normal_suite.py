# -*- coding: GB18030 -*-
'''
Created on Nov 9, 2011

@author: caiyifeng<caiyifeng>

@summary: 普通方式（顺序）调度执行case
'''

import traceback

from frame.lib.controllib.suite import DtestSuite
from frame.lib.controllib.result import CaseResult

from frame.lib.commonlib.timer import Timer
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.safe_encode import safegb
from frame.tools.cov.func_cov import Cov_Global

class NormalSuite(DtestSuite):
    '''@summary: 挨个运行case'''
    def __init__(self):
        super(NormalSuite, self).__init__()

        self.is_weak = False        # 是否一遇到case fail就退出

        # 错误自动定位
        self.do_errlocate = False
        self.errlocate_result = None

    def set_weak(self, flag):
        self.is_weak = flag

    def set_error_locate(self, errlocate_result):
        self.do_errlocate = True
        self.errlocate_result = errlocate_result


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
            # 获得module plugin
            plugin = acase.mp
            dlog.debug("Use Plugin : %s", type(plugin))

            # =================== STEP 1 ===================
            # 生成基准环境
            try:
                plugin.benchmark_env()
            except Exception:
                # 基准化环境失败
                dlog.critical("Benchmark Failed. Framework Quits", exc_info=True)
                result.case_result_dict["Framework_Environment"] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())

                # 直接退出
                return


            # =================== STEP 2 ===================
            # 运行case的setup_env方法
            result.case_time_dict[acase.filepath].start()
            try:
                acase.setup_env()
            except Exception:
                # setup_env出错
                dlog.error("Case Failed: %s", acase.get_relpath(), exc_info=True)
                result.case_result_dict[acase.filepath] = CaseResult(result.FAILED, "setup_env",
                                                                            caseobj=acase, exc_stack=traceback.format_exc())

                # 如果is weak，直接退出
                if self.is_weak:
                    dlog.critical("I meet a failure, I'm weak, so I quit")
                    return

                # 跳过这个case
                continue
            finally:
                result.case_time_dict[acase.filepath].end()

            try:
                # =================== STEP 3 ===================
                # 启动测试环境
                result.case_time_dict[acase.filepath].start()
                try:
                    plugin.clean_error()

                    plugin.startup_env()
                    plugin.common_check(acase)
                except Exception:
                    # 启动环境失败
                    dlog.error("Startup Env Failed: %s", acase.get_relpath(), exc_info=True)
                    result.case_result_dict[acase.filepath] = CaseResult(result.FAILED, "StartupEnv",
                                                                                caseobj=acase, exc_stack=traceback.format_exc())

                    # 输出诊断信息
                    keyinfo = plugin.diagnose_error()
                    # 保存错误环境
                    plugin.bak_failed_env( acase.get_relpath()+".env" )

                    # 错误自动定位
                    if self.do_errlocate:
                        if not keyinfo:
                            raise Exception, "Do Error Locate needs keyinfo returned by diagnose_error()"

                        keyinfo.cases.append(acase)
                        keyinfo.failed_step = 'START'
                        keyinfo.startException = safegb(traceback.format_exc())
                        self.errlocate_result.add_failed_info(keyinfo)

                    # 如果is weak，直接退出
                    if self.is_weak:
                        dlog.critical("I meet a failure, I'm weak, so I quit")
                        return

                    # 跳过这个case
                    continue
                finally:
                    result.case_time_dict[acase.filepath].end()


                # =================== STEP 4 ===================
                # 运行Case
                ret = self._run_one_case(acase, plugin, result)
                if not ret and self.is_weak:
                    # 如果is weak，直接退出
                    dlog.critical("I meet a failure, I'm weak, so I quit")
                    return

            finally:
                # 从Step 3开始，无论case是正确执行完，还是错误导致的return 或 continue，都会执行finally
                # 停止环境
                try:
                    plugin.stop_env()
                except Exception:
                    # 停止环境失败
                    dlog.critical("Stop Env Failed. Framework Quits", exc_info=True)
                    result.case_result_dict["Stop_Environment"] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())

                    # 直接退出
                    return

    def _run_one_case(self, acase, plugin, result):
        #record the runtime log
        acase.start_log_record()

        # 运行Case
        acase.log_start_line()
        result.case_time_dict[acase.filepath].start()

        try:
            acase.setup_testcase()
            testlist = self.testdict[acase]

            r = CaseResult(result.PASS, "", caseobj=acase)   # 预先设置case的结果是pass
            result.case_result_dict[acase.filepath] = r

            test_idx = 0
            test_num = len(testlist)
            retry_count = 0 # 重试次数
            while test_idx < test_num:
                # 运行acase的所有test方法
                atest = testlist[test_idx]
                test_idx += 1 #索引指向下一个case
                try:
                    plugin.clean_error()
                    if Cov_Global.func_cov_mode:
                        plugin.init_cov()
                    atest()

                    plugin.common_check(acase)    # 公共检查

                except Exception:
                    dlog.error("Test Failed: %s.%s", acase.get_relpath(), atest.__name__, exc_info=True)
                    if hasattr(plugin,"fail_retry") and plugin.fail_retry(retry_count,acase,atest):
                        retry_count += 1
                        dlog.info("Test Retry %d: %s.%s", retry_count, acase.get_relpath(), atest.__name__)
                        test_idx -= 1 #进行重试,case索引恢复成当前case
                        continue

                    retry_count = 0 # 重试次数复位
                    r.result = result.FAILED                            # test失败，直接设置case fail
                    r.add_failed_test(atest, traceback.format_exc())    # 增加失败的test

                    # 输出诊断信息
                    keyinfo = plugin.diagnose_error()
                    # 保存错误环境
                    plugin.bak_failed_env(acase.get_relpath() + ".evn/" + atest.__name__)

                    # 错误自动定位
                    if self.do_errlocate:
                        if not keyinfo:
                            raise Exception, "Do Error Locate needs keyinfo returned by diagnose_error()"

                        keyinfo.cases.append(acase)
                        keyinfo.failed_step = atest.__name__
                        keyinfo.testException = safegb(traceback.format_exc())
                        self.errlocate_result.add_failed_info(keyinfo)

                    # 如果is weak，直接返回错误
                    if self.is_weak:
                        return False

                else:
                    if retry_count>0: #通过重试通过的case
                        dlog.warning("After retry, %s.%s successed",acase.get_relpath(), atest.__name__)
                    if Cov_Global.func_cov_mode:
                        plugin.bak_cov(acase.get_relpath() + ":" + atest.__name__)
                    dlog.success("Test Succeeded: %s.%s", acase.get_relpath(), atest.__name__)
                    r.add_passed_test(atest)       # 增加成功的test

        except Exception:
            dlog.error("Case Failed: %s", acase.get_relpath(), exc_info=True)
            result.case_result_dict[acase.filepath] = CaseResult(result.FAILED, "",
                                                                        caseobj=acase, exc_stack=traceback.format_exc())

            # 返回错误
            return False

        finally:
            result.case_time_dict[acase.filepath].end()
            acase.log_end_line()
            acase.stop_log_record()
            result.case_result_dict[acase.filepath].add_log_record(acase.log_stream.getvalue())

        # 返回正确
        return True


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
