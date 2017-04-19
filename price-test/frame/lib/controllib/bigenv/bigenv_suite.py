# -*- coding: GB18030 -*-
'''
Created on Nov 11, 2011

@author: caiyifeng<caiyifeng>

@summary: 大库方式调度执行case
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
    '''@summary: 大库运行case'''
    def __init__(self):
        super(BigenvSuite, self).__init__()

        self.is_weak = False        # 是否一遇到case fail就退出
        self.is_single = False      # case是否单独运行

        self.case_dispatch = []     # case执行的调度。每个元素是list，list中的case并发运行
        self.row_num = 0            # case的批次
        self.is_iter_case = False   # 是否穷举物料运行

        # 错误自动定位
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
        '''@param result: DResult对象'''
        # 执行每种plugin的全局初始化
        self._do_global_init(result)

        # 初始化所有case的time字典
        self._init_case_time(result)

        # 初始化case执行顺序
        self._init_case_dispatch()

        # 执行所有case
        self._run_cases(result)

        # 追加个性result结果
        result.add_property('bigenv_row_number', self.row_num)

        # 执行每种plugin的全局destroy
        self._do_global_destroy(result)

    def _init_case_time(self, result):
        '''@summary: 初始化所有case的time字典'''
        for acase in self.caselist:
            result.case_time_dict[acase.get_relpath()] = Timer()

    def _init_case_dispatch(self):
        '''@summary: 初始化case执行顺序'''
        isall_cases = []     # isall为True的case
        separate_cases = []  # isall为False的case
        for acase in self.caselist:
            if acase.isall:
                isall_cases.append(acase)
            else:
                separate_cases.append(acase)

        # 处理isall_cases
        if self.is_single:
            # 如果suite是--single模式, 则单独加入
            self.case_dispatch.extend([[acase] for acase in isall_cases])
        else:
            # 如果suite不是--single模式，则按(dir, casetype)加入

            # 新建dir_case_dict
            dir_case_dict = {}
            dir_case_list = []  # 保持case dir的顺序
            for acase in isall_cases:
                # key: case目录 + case隶属suite name + case基类列表
                casedir = os.path.dirname(acase.filepath)
                key = (casedir, acase.attached_suite_name) + acase.get_case_type()

                if key not in dir_case_dict:
                    dir_case_dict[key] = []
                    dir_case_list.append(key)

                dir_case_dict[key].append(acase)

            # 按dir加入
            self.case_dispatch.extend([dir_case_dict[key] for key in dir_case_list])

        # 将seperate_cases单独加入
        self.case_dispatch.extend([[acase] for acase in separate_cases])

    def _run_cases(self, result):
        '''@summary: 分批运行所有的case'''
        for case_serial in self.case_dispatch:
            # 运行每一个case_serial
            caseNum = len(case_serial)
            caseIdx = 0

            while caseIdx < caseNum:
                # 分批运行case_serial

                # 获得module plugin
                plugin = case_serial[0].mp_cls()
                dlog.debug("Use Plugin : %s", type(plugin))

                result.plugin_bench_timer.start()
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
                finally:
                    result.plugin_bench_timer.end()


                # =================== STEP 2 ===================
                # 找到一批case，方法：
                # 挨个运行case的setup_env方法，直到Generator用尽
                run_case_list = []
                while caseIdx < caseNum:
                    acase = case_serial[caseIdx]
                    #bigenv case也可以获取插件对象
                    acase.mp = plugin
                    result.case_time_dict[acase.get_relpath()].start()
                    try:
                        acase.setup_env()

                        # setup_env成功
                        run_case_list.append(acase)
                        caseIdx += 1    # 增加下标

                    except StopIteration:
                        # Generator用尽，跳出
                        if run_case_list:
                            # 前面已经有其他case了，说明当前case未必出错。不增加下标
                            dlog.info("Case '%s' Out of Generator", acase.get_relpath(), exc_info=True)
                        else:
                            # 第一个case就用尽了Generator，标记case错误
                            dlog.error("Case '%s' Failed: Run out of Generator", acase.get_relpath(), exc_info=True)
                            result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "Out_of_Generator",
                                                                                        caseobj=acase, exc_stack=traceback.format_exc())

                            # 如果is weak，直接退出
                            if self.is_weak:
                                dlog.critical("I meet a failure, I'm weak, so I quit")
                                return

                            caseIdx += 1    # 增加下标，跳过出错的case

                        break

                    except Exception:
                        # setup_env出错，跳出
                        dlog.error("Case Failed: %s", acase.get_relpath(), exc_info=True)
                        result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "setup_env",
                                                                                    caseobj=acase, exc_stack=traceback.format_exc())

                        # 如果is weak，直接退出
                        if self.is_weak:
                            dlog.critical("I meet a failure, I'm weak, so I quit")
                            return

                        caseIdx += 1    # 增加下标，跳过出错的case
                        break

                    finally:
                        result.case_time_dict[acase.get_relpath()].end()

                        if vgutils.is_running_valgrind():
                            vgutils.record_case_rel([acase.get_relpath() for acase in run_case_list])

                if run_case_list:
                    # 选出了一批case
                    dlog.info("Run cases in a row:\n%s", "\n".join([acase.get_relpath() for acase in run_case_list]) )
                    plugin.caselist = run_case_list
                else:
                    # 没有选出case
                    dlog.warning("No case in a row, continue")
                    continue

                try:
                    # =================== STEP 3 ===================
                    # 启动测试环境
                    self.row_num += 1
                    result.plugin_startup_timer.start()
                    try:
                        plugin.clean_error()

                        plugin.startup_env()
                        plugin.common_check(run_case_list)
                    except Exception:
                        # 启动环境失败
                        dlog.error("Startup Env Failed", exc_info=True)

                        # 输出诊断信息
                        keyinfo = plugin.diagnose_error()

                        # 错误自动定位
                        if self.do_errlocate:
                            if not keyinfo:
                                raise Exception, "Do Error Locate needs keyinfo returned by diagnose_error()"

                            keyinfo.cases.extend([acase.filepath for acase in run_case_list])
                            keyinfo.failed_step = 'START'
                            keyinfo.startException = safegb(traceback.format_exc())
                            self.errlocate_result.add_failed_info(keyinfo)

                        # row中的所有case置为fail
                        for i, acase in enumerate(run_case_list):
                            dlog.error("Set Case '%s' Failed", acase.get_relpath())
                            if i == 0:
                                result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "StartupEnv_Head",
                                                                                            caseobj=acase, exc_stack=traceback.format_exc())

                                # 保存错误环境
                                plugin.bak_failed_env( acase.get_relpath()+".env" )
                            else:
                                result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "StartupEnv",
                                                                                            caseobj=acase)

                        # 如果is weak，直接退出
                        if self.is_weak:
                            dlog.critical("I meet a failure, I'm weak, so I quit")
                            return

                        # 跳过这批case
                        continue
                    finally:
                        result.plugin_startup_timer.end()

                        # 将startup的时间平摊到所有case上
                        average_case_time = result.plugin_startup_timer.interval / len(run_case_list)
                        # 将bench的时间平摊到所有case上
                        average_case_time += result.plugin_bench_timer.interval / len(run_case_list)
                        for acase in run_case_list:
                            result.case_time_dict[acase.get_relpath()].totaltime += average_case_time

                        if vgutils.is_running_valgrind():
                            vgutils.record_case_rel([acase.get_relpath() for acase in run_case_list])

                    # =================== STEP 3.1 ===================
                    # 运行这批case的extraPrepare
                    candidate_list = []
                    for acase in run_case_list:
                        result.case_time_dict[acase.get_relpath()].start()
                        try:
                            acase.extraPrepare()
                            candidate_list.append(acase)
                        except Exception:
                            # setUpEnv出错，跳出
                            dlog.error("Case Failed: %s", acase.get_relpath(), exc_info = True)
                            result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "ExtraPrepare", \
                                    caseobj=acase, exc_stack=traceback.format_exc())

                            # 保存错误环境
                            plugin.bak_failed_env(acase.get_relpath() + ".env")

                            # 如果is weak，直接退出
                            if self.is_weak:
                                dlog.critical("I meet a failure, I'm weak, so I quit")
                                return

                            break
                        finally:
                            result.case_time_dict[acase.get_relpath()].end()

                    run_case_list = candidate_list

                    # =================== STEP 3.2 ===================
                    # testplugin运行extra_prepare
                    if not run_case_list:
                        continue

                    result.plugin_startup_timer.start()
                    try:
                        plugin.extra_prepare()
                    except Exception:
                        # 启动环境失败
                        dlog.error("extra_prepare Failed", exc_info=True)

                        # row中的所有case置为fail
                        for i, acase in enumerate(run_case_list):
                            dlog.error("Set Case '%s' Failed", acase.get_relpath())
                            result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "PluginExtraPrepare", \
                                        caseobj=acase, exc_stack=traceback.format_exc())

                            # 保存错误环境
                            plugin.bak_failed_env(acase.get_relpath() + ".env")

                        # 如果is weak，直接退出
                        if self.is_weak:
                            dlog.critical("I meet a failure, I'm weak, so I quit")
                            return

                        # 跳过这批case
                        continue
                    finally:
                        result.plugin_startup_timer.end()

                        # 将startup的时间平摊到所有case上
                        average_case_time = result.plugin_startup_timer.interval / len(run_case_list)
                        for acase in run_case_list:
                            result.case_time_dict[acase.get_relpath()].totaltime += average_case_time

                    # =================== STEP 4 ===================
                    # 运行这批case
                    for acase in run_case_list:
                        plugin.runcase = acase
                        result.case_time_dict[acase.get_relpath()].start()
                        ret = self._run_one_case(acase, plugin, result)
                        result.case_time_dict[acase.get_relpath()].end()
                        if not ret and self.is_weak:
                            # 如果is weak，直接退出
                            dlog.critical("I meet a failure, I'm weak, so I quit")
                            return

                        coverutils.save_covinfo(acase.get_relpath())
                finally:
                    # 从Step 3开始，无论case是正确执行完，还是错误导致的return 或 continue，都会执行finally
                    # 停止环境
                    try:
                        plugin.stop_env()
                    except Exception:
                        # 停止环境失败
                        dlog.critical("Stop Env Failed. Framework Quits", exc_info=True)
                        result.case_result_dict["Stop_Environment"] = CaseResult(result.FAILED, "", exc_stack=traceback.format_exc())
                        plugin.bak_failed_env(acase.get_relpath() + ".env")

                        # 直接退出
                        return

    def _run_one_case(self, acase, plugin, result):
        #record the runtime log
        acase.start_log_record()

        # 运行Case
        acase.log_start_line()

        try:
            acase.setup_testcase()
            testlist = self.testdict[acase]

            r = CaseResult(result.PASS, "", caseobj=acase)   # 预先设置case的结果是pass
            result.case_result_dict[acase.get_relpath()] = r

            test_idx = 0
            test_num = len(testlist)
            retry_count = 0 #重试次数
            while test_idx < test_num:
                # 运行acase的所有test方法
                atest = testlist[test_idx]
                test_idx += 1 # 索引指向下一个case
                try:
                    plugin.clean_error()
                    if Cov_Global.func_cov_mode:
                        plugin.init_cov()
                    atest()
                    plugin.common_check([acase])    # 公共检查

                except Exception:
                    dlog.error("Test Failed: %s.%s", acase.get_relpath(), atest.__name__, exc_info=True)
                    if hasattr(plugin,"fail_retry") and plugin.fail_retry(retry_count,acase,atest):
                        retry_count += 1
                        dlog.info("Test Retry %d: %s.%s", retry_count, acase.get_relpath(), atest.__name__)
                        test_idx -= 1 #case重试,索引恢复成当前case
                        continue

                    retry_count = 0 #重试次数复位

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

                        keyinfo.cases.append(acase.filepath)
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
                    retry_count = 0 #重试次数复位

        except Exception:
            dlog.error("Case Failed: %s", acase.get_relpath(), exc_info=True)
            result.case_result_dict[acase.get_relpath()] = CaseResult(result.FAILED, "",
                                                caseobj=acase, exc_stack=traceback.format_exc())
            # 输出诊断信息
            keyinfo = plugin.diagnose_error()
            # 保存错误环境
            plugin.bak_failed_env(acase.get_relpath() + ".env/")

            # 返回错误
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
            mp_type = acase.mp_cls

            if mp_type not in plugin_case_dict:
                clist = []
                plugin_case_dict[mp_type] = clist
                plugin_case_list.append( (mp_type, clist) )

            plugin_case_dict[mp_type].append(acase)

        return plugin_case_list

    def _init_case_mt(self,result):
        for case_serial in self.case_dispatch: #取出同一次运行的case序列
            self.mt_case_list = []
            for acase in case_serial :

                # 如果case没有mtFactory属性, 说明使用写死的物料类型运行,退出!
                if not hasattr(acase, 'mtFactory') :
                    continue

                # 设置第一个case运行的物料类型
                acase.mtFactory.setMtIdx(0)

                if self.is_iter_case == False: #如果没有启动穷举运行, 退出!
                    continue

                # 如果仅有默认物料类型,则使用默认物料类型运行即可,退出!
                if len(acase.mtFactory.mtlist) <= 1:
                    continue

                # 取穷举物料类型集合中一个
                for i in range(1,len(acase.mtFactory.mtlist)):
                    xcase = acase.__class__() # 重新生成这个case的一个实例
                    xcase.set_filepath(acase.filepath)
                    xcase.mtFactory.setMtIdx(i)# 改变其物料类型
                    result.case_time_dict[xcase.get_relpath()] = Timer()
                    self.mt_case_list.append(xcase)

                    # 得到case的所有testXXX方法
                    f_tests = []
                    atestlist = self.testdict[acase]
                    for atest in atestlist: # 获得第一个实例的test方法列表
                        testStr = atest.__name__ # 获得方法字符串名
                        xtest = getattr(xcase,testStr) # 获得新生成实例的test方法
                        f_tests.append(xtest)
                    # 将case对应的test方法加入suite
                    self.testdict[xcase] = f_tests
            case_serial.extend(self.mt_case_list) # 将复制的所有case插入序列中

