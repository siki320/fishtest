# -*- coding: GBK -*-
"""
    @author     : liqiuhua
    @date       : Thu 21 Mar 2013 04:20:36 PM CST
    @last update: Thu 21 Mar 2013 04:20:36 PM CST
    @summary    : 
            sys suite for remora
    @version    : 1.0.0.0
"""

import traceback
import os
from new import instancemethod
from frame.lib.commonlib.timer import Timer
from frame.lib.commonlib.dlog import dlog
from frame.lib.controllib.result import CaseResult
from frame.lib.controllib.sysframe.sysenv import SysEnv
from frame.lib.controllib.sysframe.caseplug.sys_case import *
from frame.lib.controllib.sysframe.suiteplug.syssuite import SysSuite

class RemoraSysSuite(SysSuite):

    def __init__(self):
        super(RemoraSysSuite, self).__init__()

    def run_one_case(self,acase,result):
        """
            run one case
        """
        r = CaseResult(result.PASS, "", caseobj=acase)   # 预先设置case的结果是pass
        result.case_result_dict[acase.filepath] = r
        test_namelist = self._gettestlist(acase)    
        try:
            acase.benchmark_env()
            acase.setup_testcase()
        except Exception:
            acase.bak_failed_env(acase.get_relpath() + ".evn/")
            dlog.error("%s:benchmark_env Failed or setup_testcase Failed", acase.get_relpath(), exc_info=True)
            r.result = result.FAILED
            return False

        try:
            acase.startup_env()
            acase.common_check()
        except Exception:
            acase.diagnose_error()
            acase.bak_failed_env(acase.get_relpath() + ".evn/")
            dlog.error("%s:startup_env Failed", acase.get_relpath(), exc_info=True)
            r.result = result.FAILED
            return False

        for testname in test_namelist:
            try:
                acase.setup()
                atest = getattr(acase,testname)
                atest()
                acase.common_check()
            except Exception:
                acase.diagnose_error()
                acase.bak_failed_env(acase.get_relpath() + ".evn/" + atest.__name__)
                dlog.error("Test Failed: %s.%s", acase.get_relpath(), atest.__name__, exc_info=True)
                r.result = result.FAILED
                r.add_failed_test(atest, traceback.format_exc())
                if self.is_weak:
                    return False
            else:
                dlog.success("Test Succeeded: %s.%s", acase.get_relpath(), atest.__name__)
                r.add_passed_test(atest)
            finally:
                try:
                    acase.teardown()
                except Exception:
                    dlog.error("teardown failed: %s.%s", acase.get_relpath(), atest.__name__, exc_info=True)
                    return False
        # final_check
        try:
            acase.final_check()
        except Exception:
            acase.bak_failed_env(acase.get_relpath() + ".env/")
            dlog.error("final_check Failed: %s", acase.get_relpath(), exc_info=True)
            r.result = result.FAILED

        try:
            acase.stop_env()
            acase.teardown_testcase()
        except Exception:
            acase.bak_failed_env(acase.get_relpath() + ".env/")
            dlog.error("stop_env or teardown_testcase Failed: %s", acase.get_relpath(), exc_info=True)
            result.case_time_dict[acase.filepath].end()

        if r.result == result.FAILED:
            return False
        return True

