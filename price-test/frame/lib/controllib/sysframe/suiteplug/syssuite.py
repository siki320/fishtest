# -*- coding: GBK -*-
"""
    @author     : yuanyi03
    @date       : Thu 21 Mar 2013 04:20:36 PM CST
    @last update: Thu 21 Mar 2013 04:20:36 PM CST
    @summary    : 
            System level suite class 
            all suite basic module 
    @modify     : liqiuhua
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

def enum(*seq, **kv):
    enum = dict(zip(seq, range(len(seq))),**kv)
    return type("Enum",(),enum)

DE_MODE = enum("FULL",
               "LIB",
               "CASE")

class SysSuite(object):

    def __init__(self):
        self.topo_cases={}
        # case which status not equal to READY 
        #   will be put into ignorelist 
        self.ignorelist = []
        self.modes = ["FULL","LIB","CASE"]
        self.deploymode = "FULL"
        self.is_weak = False
        self.is_xstp = False
        self.conf_file = ""

    def benchmark(self, topofile):
        pass

    def set_xstp(self, is_xstp):
        self.is_xstp = is_xstp

    def set_deploymode(self, mode):
        if mode not in self.modes:
            raise Exception, "mode:%s is not correct."%mode
        self.deploymode = mode

    def set_xstpmode(self, mode):
        self.is_xstp = mode

    def set_conf_file(self, conf_file):
        self.conf_file = conf_file

    def addcase(self,case):
        """
            add case,
        """
        #check case status first
        if case.status != Sys_Case.STATS.READY:
            self.ignorelist.append(case)
            return

        topo_file = case.get_envconf() 
        if topo_file not in self.topo_cases.keys():
            self.topo_cases[topo_file] = []
        self.topo_cases[topo_file].append(case)
        return 0

    def _gettestlist(self,acase):
        rs = []
        for test_name in dir(acase):
            if not test_name.startswith('test'):
                continue
            if not isinstance(getattr(acase,test_name), instancemethod):
                continue
            if getattr(acase,test_name).__doc__ == None:
                dlog.warning("test function doc miss : %s"%(test_name))
                continue
            rs.append(test_name)
        return rs

    def run_one_case(self,acase,result):
        """
            run one case
        """
        r = CaseResult(result.PASS, "", caseobj=acase)   # 预先设置case的结果是pass
        result.case_result_dict[acase.filepath] = r
        test_namelist = self._gettestlist(acase)    
        try:
            acase.setup_testcase()
        except Exception:
            acase.bak_failed_env(acase.__class__)
            return False

        for testname in test_namelist:
            try:
                acase.setup()
                atest = getattr(acase,testname)
                atest()
                test_doc = atest.__doc__
                if not test_doc:
                    test_doc = "unknow"
                test_doc = test_doc.replace('\n',' ').replace('\r','').strip()
                test_doc = ' '.join([word for word in test_doc.split(' ') if word !=''])
            except Exception:
                dlog.error("Test Failed: %s.%s", acase.get_relpath(), atest.__name__, exc_info=True)
                r.result = result.FAILED
                r.add_failed_test(atest, traceback.format_exc())
                acase.bak_failed_env(atest.__name__)
                if self.is_weak:
                    return False
            else:
                dlog.success("Test Succeeded: %s.%s [%s]", acase.get_relpath(), atest.__name__, test_doc)
                r.add_passed_test(atest)
            finally:
                try:
                    acase.teardown()
                except Exception:
                    dlog.error("teardown failed: %s.%s", acase.get_relpath(), atest.__name__, exc_info=True)
                    return False
        try:
            acase.teardown_testcase()
        except Exception:
            dlog.error("teardown_testcase Failed: %s", acase.get_relpath(), exc_info=True)
            result.case_time_dict[acase.filepath].end()

        if r.result == result.FAILED:
            return False
        return True


    def _init_case_time(self, result):
        '''@summary: 初始化所有case的time字典'''
        for topo_file in self.topo_cases.keys():
            for acase in self.topo_cases[topo_file]:
                result.case_time_dict[acase.filepath] = Timer()

    def run_cases(self,result):
        """
            run all case, without ignorelist 
        """
        self._init_case_time(result)

        for topo_file in self.topo_cases.keys():
            #each topo_file need a deploy
            de = SysEnv(dlog,True,True)
            de.set_conf_file(self.conf_file)
            de.set_topology_file(topo_file) 
            dlog.info("Deploy Env & Lib Start(%s) ...."%topo_file)
            deploy_flag = False

            if self.deploymode == "FULL":
                deploy_flag = True
                os.environ["xds_force_dispatch"] = "1"
            elif self.deploymode == "LIB":
                deploy_flag = False
                os.environ["xds_force_dispatch"] = "1"
            else:
                deploy_flag = False
                os.environ["xds_force_dispatch"] = "0"
            
            if self.is_xstp:
                de.set_hostinfo_file(topo_file+".xstp") 
            de.deploy(deploy_flag, self.is_xstp)

            plugin = None
            dlog.info("Deploy Env & Lib End.") 

            self.benchmark(topo_file)
            for acase in self.topo_cases[topo_file]:
                result.case_time_dict[acase.filepath].start()
                case_doc = acase.__doc__
                if not case_doc:
                    case_doc = "unknow"
                case_doc = case_doc.replace('\n',' ').replace('\r','').strip()
                case_doc = ' '.join([word for word in case_doc.split(' ') if word !=''])
                # =================== STEP 1 load libs ===================
                try:
                    acase.load_modules(de.module_base)
                except Exception:
                    dlog.error("Case Failed: %s", acase.get_relpath(), exc_info=True)
                    result.case_result_dict[acase.filepath] = CaseResult(result.FAILED, "load_modules", caseobj=acase, exc_stack=traceback.format_exc())
                    if self.is_weak:
                        dlog.critical("I meet a failure, I'm weak, so I quit")
                        return 
                    # 跳过这个case
                    continue

                try:
                    # =================== STEP 2 运行一个case===================
                    ret = self.run_one_case(acase,result)
                    if not ret: 
                        dlog.error("Case Failed: %s [%s]", acase.get_relpath(), case_doc, exc_info=True)
                        if self.is_weak:
                             # 如果is weak，直接退出
                             dlog.critical("I meet a failure, I'm weak, so I quit")
                             return 
                    else:
                        dlog.success("Case Passed: %s [%s]", acase.get_relpath(), case_doc)

                except Exception:
                    dlog.error("Case Failed: %s [%s]", acase.get_relpath(), case_doc, exc_info=True)
                    result.case_result_dict[acase.filepath] = CaseResult(result.FAILED, "case run", caseobj=acase, exc_stack=traceback.format_exc())
