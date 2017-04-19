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
        '''@summary: ����__init__������, ������������'''
        obj = DtestCase.__new__(cls)
        
        # --- ����case��صĳ�Ա ---
        obj.fatal_ignore_list = []  # fatal������
        
        # --- case��ܿ�������Ҫ�޸ĵ� ---
        obj.mp = ReloadPlugin()     # module plugin
        obj.tests_list = []      # test func�Ľ������test func��Ϊkey
        obj.pass_tests_list = [] # fail test func name array
        obj.fail_tests_list = [] # fail test func name array
        obj.tests_time_dict = {}   # test func��ʱ�䣬��test func��Ϊkey
        obj.tests_result_dict = {}
        obj.result = DResult.PASS #Ĭ�Ͻ��Ϊpass
    
        
        return obj
    
    # --- ����case��صĺ��� ---
    def setup_testcase(self):
        '''@summary: ����test֮ǰ���еĺ���'''
        pass
    
    def SetUpTestCase(self):
        '''@summary: ����test֮ǰ���еĺ���'''
        pass

    def TearDownTestCase(self):
        '''@summary: ����test���н�������õĺ���'''
        pass 

    def SetUp(self):
        '''@summary: ÿ��test����֮ǰ������õĺ���'''
        pass

    def TearDown(self):
        '''@summary: ÿ��test����֮�󶼻���õĺ���'''
        pass
    
    def sleeptill_reload(self):
        '''@summary: �ȴ�����reload��һ���жϷ���������reload�Ƚϱ���''' 
        dlog.debug("TODO: sleeptill_reload()")
        pass

    def has_sendrequest(self):
        '''@summary: �ж�test���Ƿ��Ѿ�����������'''
        dlog.debug("TODO: has_sendrequest()")
        pass

    def _get_testlist(self):
        '''@summary: ��ȡtest func name list''' 
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
        '''@summary: �������е�test����'''
        try:
            self.SetUpTestCase()
            for test_func in self.tests_list:
                try:
                    self.tests_time_dict[test_func].start()
                    self.SetUp()
                    self.sleeptill_reload()
                    test_func()  # ִ��test function
                    self.mp.common_check(self)
                    self.TearDown()
                except Exception: 
                    dlog.error("Test Failed: %s.%s", self.get_relpath(), \
                                test_func.__name__, exc_info=True)
                    self.result = DResult.FAILED #���� fail
                    self.tests_result_dict[test_func] = DResult.FAILED # test fail
                    self.fail_tests_list.append(test_func.__name__)

                    # ��������Ϣ
                    self.mp.diagnose_error()
                    # ������󻷾�
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
        
    # --- �����޹غ��� ---
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
        @summary: �������case���
        @author: caiyifeng
        @return: "result \t detail(Ϊ��) \t failed_test_list", ����failed_test_list�ö��ŷָ�
        '''
        return "\t".join([DResult.lit_dict[self.result], "", ",".join(self.fail_tests_list)])

    def log_start_line(self):
        '''@summary: �����ʼ��Ϣ��'''
        logstr = "+"*8 + "    Start Case : " + self.get_relpath() + "    " + "+"*8
        
        dlog.info("")
        dlog.info("+" * len(logstr))
        dlog.info(logstr)
        dlog.info("+" * len(logstr))
        
    def log_end_line(self):
        '''@summary: ���������Ϣ��'''
        logstr = "-"*8 + "    End Case : " + self.get_relpath() + "    " + "-"*8
        
        dlog.info("-" * len(logstr))
        dlog.info(logstr)
        dlog.info("-" * len(logstr))
        dlog.info("")


class ReloadPlugin(object):
    '''
    @summary: ��Բ�ͬ�Ĳ���ģ�飬�ṩ��Ӧ�Ļ�����������
    '''
    def benchmark_env(self):
        '''@summary: ���ɻ�׼��������'''
        pass
    
    def clean_error(self):
        '''@summary: common_check��/��diagnose_error ֮ǰ���ã�ȷ�����ǲ�����ʷ����Ӱ��'''
        pass
    
    def common_check(self, acase):
        '''
        @summary: ͨ�ü��
        @param acase: ReloadCase����
        '''
        pass
    
    def diagnose_error(self):
        '''@summary: �������������Ϣ'''
        # ������Ϣ
        string = dtssystem("pstree $USER | grep -v ^$ | grep -v sendmail", output=True)[1]
        dlog.diagnose("Running Processes:\n%s", string)
        
        # ������Ϣ
        hostip = dtssystem("hostname -i", output=True)[1]
        hostip = hostip.rstrip("\n")
        
        # �˿���Ϣ
        string = dtssystem("netstat -an | egrep ':6[2-5][0-9]{3} .*:'", output=True)[1]
        dlog.diagnose("Using Ports: (Host Ip is %s)\n%s", hostip, string)
    
    def bak_failed_env(self, relpath):
        '''
        @summary: ����fail����
        @param relpath: ���·��
        '''
        pass

    def global_init(self):
        '''@summary: ��ʼ�����Ի���
        @note: ������caseִ��֮ǰ����1��'''
        pass

    def global_destroy(self):
        '''@summary: �������Ի���
        @note: ������case������ɺ�ִ��'''
        pass 

    def init_cov(self):
        '''@summary: ��ʼ���������ļ�
        @note: ������ÿ��test֮ǰ����'''
        cov_init_file = os.environ["COV_INIT_FILE"]
        cov_file = os.environ["COVFILE"]
        shutil.copy(cov_init_file, cov_file)
        time.sleep(1)
        self._cov_restart()

    def bak_cov(self, case_name):
        '''@summary: ����ÿ��test�ĸ������ļ�
        @note: ������ÿ��test֮������'''
        cov_file = os.environ["COVFILE"]
        cov_bake_path = os.environ["COV_BAKE_PATH"]
        time.sleep(1)
        case_name2 = case_name.replace("/", "--")
        shutil.move(cov_file, cov_bake_path +"/output/cov1/"+case_name2)

    def _cov_restart(self):
        '''@summary: ��������case����
        @note: ��init_cov�е���'''
        self.startup_env()
        pass
