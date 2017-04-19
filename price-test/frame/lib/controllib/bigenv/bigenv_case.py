# -*- coding: GB18030 -*-
'''
Created on Nov 11, 2011

@author: caiyifeng<caiyifeng>

@summary: ���case����
'''
import time
import shutil
from frame.lib.controllib.case import DtestCase

from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.dtssystem import dtssystem


class BigenvCase(DtestCase):
    def __new__(cls):
        '''@summary: ����__init__������, ������������'''
        obj = DtestCase.__new__(cls)
        
        # --- ����case�ɶ�/д�ĳ�Ա ---
        obj.isall = True                # �Ƿ�������
        obj.fatal_ignore_list = []      # fatal������
        obj.attached_suite_name = ""    # ������suite name, Ĭ��Ϊ��
        
        # --- case��ܿ�������Ҫ�޸ĵģ�����caseֻ�� ---
        obj.mp_cls = BigenvPlugin   # module plugin class
        
        return obj
    
    # --- ����case����д�ĺ��� ---
    def setup_env(self):
        '''@summary: �������ݵ�setup����'''
        pass
    
    def setup_testcase(self):
        '''@summary: ����test֮ǰ���еĺ���'''
        pass
   
    def teardown_testcase(self):
        "Suite�����teardown����"
        pass
 
    # --- �����޹غ��� ---
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

    def extraPrepare(self):
        '''
        @Suite�����prepare����
        '''
        pass
        
    def get_case_type(self):
        '''
        @summary: ����case�Ļ���Ԫ��
        '''
        return type(self).__bases__


class BigenvPlugin(object):
    '''
    @summary: ��Բ�ͬ�Ĳ���ģ�飬�ṩ��Ӧ�Ļ�����������
    '''
    def __init__(self):
        self.caselist = []      # ������е�case�б�
        self.runcase = None     # ��ǰ���е�case����
    
    def benchmark_env(self):
        '''
        @summary: ���ɻ�׼��������
        @note����һ�����case��setup_env֮ǰ����
        '''
        pass
    
    def extra_prepare(self):
        '''
        ��suite�����extraPrepare֮�����
        '''
        pass

    def startup_env(self):
        '''
        @summary: �������Ի���
        @note����һ�����case��setup_env֮�����
        '''
        pass
    
    def stop_env(self):
        '''
        @summary: ֹͣ���Ի���
        @note����һ�����case������testִ����ɺ����
        '''
        pass
    
    def clean_error(self):
        '''
        @summary: �����������ʷ����
        @note: 
         - ��case��ÿ��test֮ǰ���ã�ȷ��common_check��diagnose_error������ʷ����Ӱ��
         - ������ԭ�е�core�ļ�
         - ���¶�λ��������wf��־
        '''
        pass
    
    def common_check(self, acase):
        '''
        @summary: ͨ�ü��
        @param acase: NormalCase����
        @note: 
         - ��case��ÿ��test֮�����
         - ����Ƿ���core�ļ�
         - ��鱻������wf��־���Ƿ���FATAL
        '''
        pass
    
    def diagnose_error(self):
        '''
        @summary: �������������Ϣ
        @note: 
         - ��test fail֮�����
         - �����ǰ������Ϣ
         - ��������е�core�ļ�
         - �����������notice��wf��־
        '''
        # ������Ϣ
        string = dtssystem("pstree $USER | grep -v ^$ | grep -v sendmail", output=True)[1]
        dlog.diagnose("Running Processes:\n%s", string)
        
        # ������Ϣ
        hostip = dtssystem("hostname -i", output=True)[1]
        hostip = hostip.rstrip("\n")
        
        # �˿���Ϣ
        string = dtssystem("netstat -an | egrep ':6[2-5][0-9]{3} .*:'", output=True, errlevel="debug")[1]
        dlog.diagnose("Using Ports: (Host Ip is %s)\n%s", hostip, string)
    
    def bak_failed_env(self, relpath):
        '''
        @summary: ����ѡ������fail����
        @param relpath: ���·��
        @note:
         - ��test fail֮����� 
         - �ļ����汻������notice��wf��־
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
