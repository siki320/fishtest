# -*- coding: GB18030 -*-
'''
Created on Nov 11, 2011

@author: caiyifeng<caiyifeng>

@summary: 大库case基类
'''
import time
import shutil
from frame.lib.controllib.case import DtestCase

from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.dtssystem import dtssystem


class BigenvCase(DtestCase):
    def __new__(cls):
        '''@summary: 先于__init__被调用, 生成所有属性'''
        obj = DtestCase.__new__(cls)
        
        # --- 具体case可读/写的成员 ---
        obj.isall = True                # 是否大库运行
        obj.fatal_ignore_list = []      # fatal白名单
        obj.attached_suite_name = ""    # 隶属于suite name, 默认为空
        
        # --- case框架开发者需要修改的，具体case只读 ---
        obj.mp_cls = BigenvPlugin   # module plugin class
        
        return obj
    
    # --- 具体case可重写的函数 ---
    def setup_env(self):
        '''@summary: 环境数据的setup方法'''
        pass
    
    def setup_testcase(self):
        '''@summary: 所有test之前运行的函数'''
        pass
   
    def teardown_testcase(self):
        "Suite级别的teardown方法"
        pass
 
    # --- 子类无关函数 ---
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

    def extraPrepare(self):
        '''
        @Suite级别的prepare方法
        '''
        pass
        
    def get_case_type(self):
        '''
        @summary: 返回case的基类元祖
        '''
        return type(self).__bases__


class BigenvPlugin(object):
    '''
    @summary: 针对不同的测试模块，提供相应的环境操作方法
    '''
    def __init__(self):
        self.caselist = []      # 大库运行的case列表
        self.runcase = None     # 当前运行的case对象
    
    def benchmark_env(self):
        '''
        @summary: 生成基准环境数据
        @note：在一批大库case的setup_env之前调用
        '''
        pass
    
    def extra_prepare(self):
        '''
        在suite级别的extraPrepare之后调用
        '''
        pass

    def startup_env(self):
        '''
        @summary: 启动测试环境
        @note：在一批大库case的setup_env之后调用
        '''
        pass
    
    def stop_env(self):
        '''
        @summary: 停止测试环境
        @note：在一批大库case的所有test执行完成后调用
        '''
        pass
    
    def clean_error(self):
        '''
        @summary: 清除环境中历史错误
        @note: 
         - 在case的每个test之前调用，确保common_check和diagnose_error不受历史错误影响
         - 重命名原有的core文件
         - 重新定位被测程序的wf日志
        '''
        pass
    
    def common_check(self, acase):
        '''
        @summary: 通用检查
        @param acase: NormalCase对象
        @note: 
         - 在case的每个test之后调用
         - 检查是否有core文件
         - 检查被测程序的wf日志中是否有FATAL
        '''
        pass
    
    def diagnose_error(self):
        '''
        @summary: 输出错误的诊断信息
        @note: 
         - 在test fail之后调用
         - 输出当前机器信息
         - 输出环境中的core文件
         - 输出被测程序的notice和wf日志
        '''
        # 进程信息
        string = dtssystem("pstree $USER | grep -v ^$ | grep -v sendmail", output=True)[1]
        dlog.diagnose("Running Processes:\n%s", string)
        
        # 机器信息
        hostip = dtssystem("hostname -i", output=True)[1]
        hostip = hostip.rstrip("\n")
        
        # 端口信息
        string = dtssystem("netstat -an | egrep ':6[2-5][0-9]{3} .*:'", output=True, errlevel="debug")[1]
        dlog.diagnose("Using Ports: (Host Ip is %s)\n%s", hostip, string)
    
    def bak_failed_env(self, relpath):
        '''
        @summary: （可选）保存fail环境
        @param relpath: 相对路径
        @note:
         - 在test fail之后调用 
         - 文件保存被测程序的notice和wf日志
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
