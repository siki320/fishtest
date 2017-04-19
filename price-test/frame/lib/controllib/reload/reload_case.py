# -*- coding: GB18030 -*-
'''
Created on Nov 29, 2011

@author: liqiuhua<liqiuhua>
'''
import time
import shutil
from new import instancemethod
from frame.lib.controllib.case import DtestCase
from frame.lib.controllib.result import DResult

from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.dtssystem import dtssystem
from frame.lib.commonlib.timer import Timer

class ReloadCase(DtestCase):
    def __new__(cls):
        '''@summary: 先于__init__被调用, 生成所有属性'''
        obj = DtestCase.__new__(cls)
        
        # --- 具体case相关的成员 ---
        obj.fatal_ignore_list = []  # fatal白名单
        
        # --- case框架开发者需要修改的 ---
        obj.mp = ReloadPlugin()     # module plugin
        obj.tests_list = []      # test func的结果，以test func作为key
        obj.pass_tests_list = [] # fail test func name array
        obj.fail_tests_list = [] # fail test func name array
        obj.tests_time_dict = {}   # test func的时间，以test func作为key
        obj.tests_result_dict = {}
        obj.result = DResult.PASS #默认结果为pass
    
        
        return obj
    
    # --- 具体case相关的函数 ---
    def setup_testcase(self):
        '''@summary: 所有test之前运行的函数'''
        pass
    
    def SetUpTestCase(self):
        '''@summary: 所有test之前运行的函数'''
        pass

    def TearDownTestCase(self):
        '''@summary: 所有test运行结束后调用的函数'''
        pass 

    def SetUp(self):
        '''@summary: 每个test运行之前都会调用的函数'''
        pass

    def TearDown(self):
        '''@summary: 每个test运行之后都会调用的函数'''
        pass
    
    def sleeptill_reload(self):
        '''@summary: 等待发生reload，一般判断发生了两次reload比较保险''' 
        dlog.debug("TODO: sleeptill_reload()")
        pass

    def has_sendrequest(self):
        '''@summary: 判断test中是否已经发送了请求'''
        dlog.debug("TODO: has_sendrequest()")
        pass

    def _get_testlist(self):
        '''@summary: 获取test func name list''' 
        for attr_name in dir(self): 
            if not attr_name.startswith('test'): # begin with test
                continue
            tmp_func = getattr(self,attr_name)
            if not isinstance(tmp_func, instancemethod): # must be a method
                continue
            self.tests_list.append(tmp_func)
            self.tests_result_dict[tmp_func] = DResult.PASS
            self.tests_time_dict[tmp_func] = Timer() # init tests time
    
    def _run_tests(self):
        '''@summary: 运行所有的test函数'''
        try:
            self.SetUpTestCase()
            for test_func in self.tests_list:
                try:
                    self.tests_time_dict[test_func].start()
                    self.SetUp()
                    self.sleeptill_reload()
                    test_func()  # 执行test function
                    self.mp.common_check(self)
                    self.TearDown()
                except Exception: 
                    dlog.error("Test Failed: %s.%s", self.get_relpath(), \
                                test_func.__name__, exc_info=True)
                    self.result = DResult.FAILED #整体 fail
                    self.tests_result_dict[test_func] = DResult.FAILED # test fail
                    self.fail_tests_list.append(test_func.__name__)

                    # 输出诊断信息
                    self.mp.diagnose_error()
                    # 保存错误环境
                    self.mp.bak_failed_env(self.get_relpath() + ".evn/" + \
                                            test_func.__name__)
                self.tests_time_dict[test_func].end()
            self.TearDownTestCase()
            self.pass_tests_list.append(test_func.__name__)
            dlog.info("Test Pass: %s.%s", self.get_relpath(),\
                        test_func.__name__) 
                     
        except Exception:
            dlog.error("Case Failed: %s", self.get_relpath(), exc_info=True)
            return False
        return True

    def run(self):
        self._get_testlist() 
        ret = self._run_tests()
        if ret==False or len(self.fail_tests_list) > 0:
            self.result = DResult.FAILED
            return False
        return True
        
    # --- 子类无关函数 ---
    def get_passed_testnum(self):
        return len(self.pass_tests_list)

    def get_failed_testnum(self):
        return len(self.fail_tests_list)

    def get_testnum(self):
        return len(self.tests_list)

    def get_failed_tests(self):
        return self.fail_tests_list

    def get_failed_testsname(self):
        failed_name = ""
        for testf in self.fail_tests_list:
            failed_name += testf.__name__
        return failed_name

    
    def get_passed_tests(self):
        return self.pass_tests_list
        
    def __str__(self):
        r'''
        @summary: 输出单个case结果
        @author: caiyifeng
        @return: "result \t detail(为空) \t failed_test_list", 其中failed_test_list用逗号分隔
        '''
        return "\t".join([DResult.lit_dict[self.result], "", ",".join(self.fail_tests_list)])

    def log_start_line(self):
        '''@summary: 输出起始信息行'''
        logstr = "+"*8 + "    Start Case : " + self.get_relpath() + "    " + "+"*8
        
        dlog.info("")
        dlog.info("+" * len(logstr))
        dlog.info(logstr)
        dlog.info("+" * len(logstr))
        
    def log_end_line(self):
        '''@summary: 输出结束信息行'''
        logstr = "-"*8 + "    End Case : " + self.get_relpath() + "    " + "-"*8
        
        dlog.info("-" * len(logstr))
        dlog.info(logstr)
        dlog.info("-" * len(logstr))
        dlog.info("")


class ReloadPlugin(object):
    '''
    @summary: 针对不同的测试模块，提供相应的环境操作方法
    '''
    def benchmark_env(self):
        '''@summary: 生成基准环境数据'''
        pass
    
    def clean_error(self):
        '''@summary: common_check和/或diagnose_error 之前调用，确保它们不受历史错误影响'''
        pass
    
    def common_check(self, acase):
        '''
        @summary: 通用检查
        @param acase: ReloadCase对象
        '''
        pass
    
    def diagnose_error(self):
        '''@summary: 输出错误的诊断信息'''
        # 进程信息
        string = dtssystem("pstree $USER | grep -v ^$ | grep -v sendmail", output=True)[1]
        dlog.diagnose("Running Processes:\n%s", string)
        
        # 机器信息
        hostip = dtssystem("hostname -i", output=True)[1]
        hostip = hostip.rstrip("\n")
        
        # 端口信息
        string = dtssystem("netstat -an | egrep ':6[2-5][0-9]{3} .*:'", output=True)[1]
        dlog.diagnose("Using Ports: (Host Ip is %s)\n%s", hostip, string)
    
    def bak_failed_env(self, relpath):
        '''
        @summary: 保存fail环境
        @param relpath: 相对路径
        '''
        pass

    def global_init(self):
        '''@summary: 初始化测试环境
        @note: 在所有case执行之前运行1次'''
        pass

    def global_destroy(self):
        '''@summary: 析构测试环境
        @note: 在所有case运行完成后执行'''
        pass 

    def init_cov(self):
        '''@summary: 初始化覆盖率文件
        @note: 在运行每个test之前运行'''
        cov_init_file = os.environ["COV_INIT_FILE"]
        cov_file = os.environ["COVFILE"]
        shutil.copy(cov_init_file, cov_file)
        time.sleep(1)
        self._cov_restart()

    def bak_cov(self, case_name):
        '''@summary: 备份每个test的覆盖率文件
        @note: 在运行每个test之后运行'''
        cov_file = os.environ["COVFILE"]
        cov_bake_path = os.environ["COV_BAKE_PATH"]
        time.sleep(1)
        case_name2 = case_name.replace("/", "--")
        shutil.move(cov_file, cov_bake_path +"/output/cov1/"+case_name2)

    def _cov_restart(self):
        '''@summary: 重启整个case环境
        @note: 在init_cov中调用'''
        self.startup_env()
        pass
