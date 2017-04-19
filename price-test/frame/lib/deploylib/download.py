# -*- coding: GB18030 -*-
"""
@author: guoan
@modified by: maqi
@date: July 28, 2011
@summary: download�Ļ���
@version: 1.0.0.0
"""
import os
os.sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../../")
import re
import time
import os.path
from datetime import datetime, timedelta

from frame.lib.commonlib.timer import Timer2

from frame.lib.deploylib.xdsystem import XDSystem
import frame.lib.deploylib.globalpath
#from frame.lib.deploylib.npatExit import npaterr
from frame.lib.deploylib.xderror import XDCommonError,XDDownloadError,\
                XDFileNotExistError,XDDirNotExistError,XDNoModInfoError,\
                XDHadoopError,XDCommandError

class BaseDownload(object):
    """
    @note: ����ģ��download�������ģ��
    """
    def __init__(self, log=None, host_info={"host":"127.0.0.1","user":"work","path":"./"}, retry=5):
        """
        @note: �����������࣬Ŀ���ǰ�wget��װ����,��ε���д
               1)ע�ⷵ��ֵ����
               2)�ѵ���д������������ع���ʼ��Ҳ������̫��ʱ��~~~~
        """
        self.basic_wget_options = "-r -nv -nH --level=0 --tries=20"
        self.limit_rate = "40m"
        self.retry_num = retry
        self.ignore_file_list=[]
        self.ignore_dir_list=[]

        self.log = log
        self.host_info = host_info
        self.sys = XDSystem(self.log)
        #�û��Զ����wget�������ݲ�������ȷ�Լ��
        self.custom_wget_args = ""

    def set_limit_rate(self, limit_rate):
        """
        @note: ����wget limit-rateѡ��
        @param limit_rate:������������
        @return: ���õ�����
        """
        self.limit_rate = str(limit_rate)
        return self.limit_rate

    def set_custom_wget_args(self, wget_args):
        """
        @note: �����Զ����wget������ÿ�����ö��Ḳ����ǰ������
        @param wget_args: �������ݣ��ǿ�ʱֱ��ǿתΪstrƴ�ӵ�wget������
        @return: ���ú�Ŀǰ��Ч�Ĳ���
        """
        if wget_args:
            self.custom_wget_args = str(wget_args)
        return self.custom_wget_args

    def compute_cut_dir(self, src_path):
        """
        @note: wgetʱӦ�ÿ�����dir��������abc/efg//Ӧ�ÿ���3��
        @param src_path:��Ҫ�ü���Ŀ¼
        """
        tmp_path = src_path.strip('/')
        cut_dir = len(tmp_path.split('/')) - 1
        if cut_dir < 0:
            self.log.warning("wget cut_dir <0 %s, force to zero", tmp_path)
            cut_dir = 0
        return cut_dir

    def add_basic_wgetOptions(self, src_path, wgetOptions):
        """
        @note: ��wget�Ļ���ѡ��ƴ������
        @param src_path:��Ҫ�ü���Ŀ¼
        @param wgetOptions:wget�Ĳ���
        """
        cut_dir_num = self.compute_cut_dir(src_path)
        wgetOptions = self.basic_wget_options + " --limit-rate=" + self.limit_rate + " --cut-dirs=" + str(cut_dir_num) + " " + wgetOptions
        #����Զ����wget����
        if self.custom_wget_args:
            wgetOptions = "%s %s" %(wgetOptions, self.custom_wget_args)
        return wgetOptions

    def wget_data(self, host, user="anonymous", passwd="anonymous", src_path=".", file_or_dir="file", dest_path=".", wgetOptions="", dest_is_file=False):
        """
        @note:ʹ��wget�������ݵĻ�������
        @param host: ����Դ��ַ
        @param user: �û���
        @param passwd: ����
        @param src_path: ����ԴĿ¼
        @param file_or_dir: �����������ļ�����Ŀ¼
        @param dest_path: ����Ŀ�ĵ�ַ��element��Ҫ�о��Ե�ַ�ṩ��download lib
        @param wgetOptions: wget��ѡ��
        @param dest_is_file: Ŀ�ĵ�ַ�Ƿ�Ϊ�ļ�����ΪTrue��ʹ��-O����ΪFalse��ʹ��-P
        """
        #ƴ��ftp��ַ
        src_path = os.path.normpath(src_path.strip('/'))

        if user == "" and passwd == "" :
            ftp_address = "ftp://%s/%s" % (host, src_path)
        else :
            ftp_address = "ftp://%s:%s@%s/%s" % (user, passwd, host, src_path)
        if file_or_dir == "dir":
            ftp_address = ftp_address + "/*"
            src_path = src_path + "/*"
        #ƴ��wgetѡ��
        wgetOptions = self.add_basic_wgetOptions(src_path, wgetOptions)
        #whole_dest_path = self.host_info["path"] + "/" + dest_path
        whole_dest_path = self.host_info["path"] + "/" + dest_path
        #�����Ŀ���ַΪ�ļ�����ʹ��-O������ʹ��-P
        if dest_is_file:
            wgetOptions += " -O " + whole_dest_path
        else:
            wgetOptions += " -P " + whole_dest_path

        #ƴ���������
        whole_wget_cmd = "wget %s %s" % (wgetOptions, ftp_address)
        self.log.debug("wget cmd:%s", whole_wget_cmd)

        #ִ������
        #retry self.retry_num ��
        ret = 0
        retry_flag = 0
        for i in range(self.retry_num):
            ret = self.sys.xd_system(whole_wget_cmd)
            if ret == 0:
                if retry_flag:
                    self.log.info("Finally Success to [wget %s of %s] after retry.", src_path, self.type)
                break
            else:
                retry_flag = 1
                if i == (self.retry_num - 1):
                    self.log.critical("The %s fail to [wget %s of %s]! no retry again!",str(self.retry_num), src_path,self.type)
                    raise XDDownloadError,"download error"
                else :
                    time.sleep(10 * (i+1))
                    self.log.warning("The %s fail to [wget %s of %s], sleep %s s, retry...",str(i+1), src_path, self.type, str(10 * (i+1)))
        return ret


    def get_date_str(self, day_num = 0):
        """
        @note: ����ʱ���ַ�������20110330, day_num��ʾ��Ե�ǰ���ڵ�ʱ����
                   ������õ�����������ַ���day_num=-1���õ������day_num =1
        """
        std_day = datetime.now()
        ret_day = std_day + timedelta(days = day_num)
        return ret_day.strftime("%Y%m%d")


    def add_ignore(self, path, flag="-X"):
        """
        @note: download�����в�������Щ������flag = -X or -R, -X��ʾignoreĿ¼��-R��ʾignore�ļ������ļ���ͨ���
               path�����������ģ���ڲ������·��������bdbs/data/bdindex/����д��data/bdindex/����
        """
        if flag == "-R":
            self.ignore_file_list.append(path)

        if flag == "-X":
            self.ignore_dir_list.append(path)
        return 0

    def add_ignore_from_list(self, path_list, flag="-X"):
        """
        @note: ��һ��list�м���ignore
               flagͬadd_ignore
               path_list����Ҫ���Ե��ļ���Ŀ¼list
        """
        if flag == "-R":
            for el in path_list:
                self.ignore_file_list.append(el)
        if flag == "-X":
            for el in path_list:
                el = el.strip('/')
                self.ignore_dir_list.append(el)
        return 0


    def make_X_wget_options_str(self, src_path):
        """
        @note: ����self.ignore_dir_list����wget��-Xѡ��
               ignore_list���ŵĶ���ģ���ڲ������·������Ҫƴ����src_path�γɾ���·��
        """
        if len(self.ignore_dir_list) == 0:
            return ""

        Xopt_str = ""
        for opt_element in self.ignore_dir_list:
            Xopt_str += src_path.strip('/') + "/" + opt_element + ","
        Xopt_str = Xopt_str[0:-1]
        Xopt_str = "-X \"" + Xopt_str + "\""
        return Xopt_str

    def make_R_wget_options_str(self):
        """
        @note: ����self.ignore_file_list����wget��-Rѡ��
        """
        if len(self.ignore_file_list) == 0:
            return ""

        Ropt_str = ""
        for opt_element in self.ignore_file_list:
            Ropt_str += os.path.basename(opt_element) + ","
        Ropt_str = Ropt_str[0:-1]
        Ropt_str = "-R \"" + Ropt_str + "\""
        return Ropt_str

    def remove_element_prefix(self,src):
        """
        @note: ɾ��element��ǰ׺������"./src" ���������� "src"
        @param src: ������Ҫ����ǰ׺���ַ���
        @return: ȥ��./����/ǰ׺���ַ���
        """
        if src.startswith("./"):
            return src[2:]
        elif src.startswith("/"):
            return src[1:]
        else:
            return src

    def expand_env_variable(self, variable):
        """
        @note: չ����������������������������ڻ��߷�$��ͷ���򷵻�ԭ��
        @param variable: ����������
        """
        ret = variable
        if variable.startswith("$"):
            tmp = os.getenv(variable[1:])
            if tmp:
                ret = tmp
            else:
                self.log.warning("Expand EVN[%s] failed ,download may fail.To fix it you should set env variable.",variable[1:])
        return ret



class HadoopDownload(BaseDownload):
    """
    @hadoop��ص�download
    """
    def __init__(self,log=None,host_info={"host":"127.0.0.1","user":"work","path":"./"},\
                    type="",retry=5):
        BaseDownload.__init__(self, log, host_info, retry)
        self.type = type
        self.path_dict = {}
        self.element_dict = {}

    def get_hadoop_module_host_dir(self, host, user, passwd, date_str):
        """
              ������һЩ��û�䣬�������ʵ�ָú�������������Ӧ������ʱ���Զ���ȡ·����������Ӧ�������
              �ú������ض�Ӧ�Ļ���·�����������������е�db-cm-fcbs01.db01
        """
        ret = 0
        retry_flag = 0
        tmp_str = None
        for i in range(self.retry_num):
            ret,tmp_str,err_str = self.sys.xd_system("lftp ftp://%s:%s@%s/%s -e 'ls -l;quit'" % (user, passwd, host, date_str), output=True)
            if ret == 0:
                if retry_flag:
                    self.log.info("Finally Success to get host dir behind [ftp://%s:%s@%s/%s] after retry", user, passwd, host, date_str)
                break
            else:
                retry_flag = 1
                if i == (self.retry_num-1):
                    self.log.critical("the %s th fail to get host dir behind [ftp://%s:%s@%s/%s] no retry again!", \
                            str(i+1), user, passwd, host, date_str)
                    raise XDHadoopError,"get host dir from hadoop error"
                else :
                    time.sleep(10 * (i+1))
                    self.log.warning("the %s th fail to get host dir behind [ftp://%s:%s@%s/%s] after retry", \
                            str(i+1), user, passwd, host, date_str)
        if ret != 0:
            return None
        tmp_str = tmp_str.splitlines()[0]
        ret_str = tmp_str.split()[-1]
        return ret_str


    def set_path_element_dict(self,path_dict,element_dict):
        """
        @note:ͨ��ÿ��ģ�����е������ļ���Ϣ����ȡ����Դ����Ϣ
              �÷���Ŀǰ��element.py������ã�Ŀ���Ǹ�ÿ��element���벻ͬ��������Ϣ
        @param path_dict: ��������Դ��Ϣ
        @param element_dict: ����element��Ϣ
        """
        self.path_dict = path_dict
        self.element_dict = element_dict
        return 0


    def combin_wget_options(self,day_num=-1):
        """
        @note:ƴ��һ��������wget����
              ע��hadoop��ƴ�ӿ����е��ر���Ҫ���������ݵĻ�����
              ���ص���һ��Ԫ��(wgetOptins,src_path)
        @param day_num: -1��������
        """
        #��ȡ�����ַ���
        date_str = self.get_date_str(day_num)
        #��ȡ����������ַĿ¼
        online_host_str = self.get_hadoop_module_host_dir(self.path_dict["host"], self.path_dict["user"], self.path_dict["passwd"], date_str)
        if online_host_str == None:
            raise XDHadoopError,"host dir from hadoop is None"

        #ƴ��srcpath�ַ���
        src_path = date_str + "/" + online_host_str + "/" + self.path_dict["dir"] \
                        + "/" + self.remove_element_prefix(self.element_dict["src"])

        #ƴ��-X wgetѡ��
        Xopt_str = self.make_X_wget_options_str(src_path)
        #ƴ��-R wgetѡ��
        Ropt_str = self.make_R_wget_options_str()
        wget_options = Xopt_str + " " + Ropt_str
        return src_path,wget_options


    def download_from_hadoop(self,day_num=-1):
        """
        @note:���ػ�׼������һ��������ͬ������
        """
        #��ȡpath_dict,��������¼������ģ���Դ��Ϣ,���������ȡ��element.py����ȥ����
        #self.get_online_path_dict()
        #self.get_npatfile_path_dict()
        #ƴ�ӳ�һ��wget����
        if self.element_dict.has_key("-X"):
            x_list = []
            for x_ele in self.element_dict["-X"].split(","):
                    x_list.append(x_ele)
            self.add_ignore_from_list(x_list,"-X")
        if self.element_dict.has_key("-R"):
            r_list = []
            for r_ele in self.element_dict["-R"].split(","):
                    r_list.append(r_ele)
            self.add_ignore_from_list(r_list,"-R")
        wget_options = self.combin_wget_options(day_num)
        #�������أ���¼dg��־
        self.log.debug("Begin Module %s get std env from hadoop...", self.type)
        if self.element_dict.has_key("property") and self.element_dict["property"] == "file":
            ret = self.wget_data(self.path_dict["host"], self.path_dict["user"], self.path_dict["passwd"], \
                             wget_options[0], "file", self.element_dict["dst"], wget_options[1])
        else:
            ret = self.wget_data(self.path_dict["host"], self.path_dict["user"], self.path_dict["passwd"], \
                             wget_options[0], "dir", self.element_dict["dst"], wget_options[1])
        self.log.debug("Finish Module %s get std env from hadoop...", self.type)
        return ret

    def smart_download(self):
        """
        @note:Ŀǰ�Ƚϼ򵥣�������Ƿ���
        """
        download_time = Timer2()
        download_time.start()
        self.log.info("begin download %s module used hadoop way" %(self.type))
        if self.element_dict.has_key("args") and self.element_dict["args"] <> None:
            ret = self.download_from_hadoop(int(self.element_dict["args"]))
        else:
            raise XDNoModInfoError,"please check elementdict, args can not be None"
        download_time.end()
        self.log.info("%s download from %s used %s s" %(self.type,self.path_dict["host"],str(download_time.get_sec())))
        return ret

class StdDownload(BaseDownload):
    """
        @note:��׼�������ָ࣬���Ǵ�һ��Ļ���������wget����ģ�飬�����hadoop�����Ĳ�ͬ����������
         1)ƴ�ӵĴ��ǲ�ͬ��
         2)������hadoop�Ĳ�������
    """
    def __init__(self,log=None,host_info={"host":"127.0.0.1","user":"work","path":"./"},type="",retry=5):
        BaseDownload.__init__(self, log, host_info, retry)
        self.type = type
        self.path_dict = {}
        self.element_dict = {}

    def set_path_element_dict(self,path_dict,element_dict):
        self.path_dict = path_dict
        self.element_dict = element_dict
        return 0

    def combin_wget_options(self):
        """
        @note:ƴ��wget�Ĵ�
        """
        #ƴ��-R wgetѡ��
        Ropt_str = self.make_R_wget_options_str()
        #ƴ��-X wgetѡ��
        src_path = self.path_dict["dir"] + "/" +self.remove_element_prefix(self.element_dict["src"])
        Xopt_str = self.make_X_wget_options_str(src_path)

        wget_options = Xopt_str + " " + Ropt_str
        return src_path,wget_options

    def download_from_std(self):
        """
        @note:���ػ�׼��������������Ǹ���ģ���Լ�ά���Ŀɲ⻷��
        """
        #��ȡpath_dict,��������¼������ģ���Դ��Ϣ
        #self.get_online_path_dict()
        #ƴ�ӳ�һ��wget����
        if self.element_dict.has_key("-X"):
            x_list = []
            for x_ele in self.element_dict["-X"].split(","):
                    x_list.append(x_ele)
            self.add_ignore_from_list(x_list,"-X")
        if self.element_dict.has_key("-R"):
            r_list = []
            for r_ele in self.element_dict["-R"].split(","):
                    r_list.append(r_ele)
            self.add_ignore_from_list(r_list,"-R")
        wget_options = self.combin_wget_options()
        #�������أ���¼dg��־
        self.log.debug("Begin Module %s get std env from std...", self.type)
        if self.element_dict.has_key("property") and self.element_dict["property"] == "file":
            ret = self.wget_data(self.path_dict["host"], self.path_dict["user"], self.path_dict["passwd"], \
                        wget_options[0], "file", self.element_dict["dst"], wget_options[1], self.element_dict.get("dst_is_file", False))
        else:
            ret = self.wget_data(self.path_dict["host"], self.path_dict["user"], self.path_dict["passwd"], \
                        wget_options[0], "dir", self.element_dict["dst"], wget_options[1])
        self.log.debug("Finish Module %s get std env from std...", self.type)
        return ret

    def smart_download(self):
        """
        @note:Ŀǰ�Ƚϼ򵥣�������Ƿ���
        """
        download_time = Timer2()
        download_time.start()
        self.log.info("begin download %s module used std way" %(self.type))
        ret = self.download_from_std()
        download_time.end()
        self.log.info("%s download from %s used %s s" %(self.type,self.path_dict["host"],str(download_time.get_sec())))
        return ret

class ScmpfDownload(BaseDownload):
    """
    @note:��׼�������ָ࣬���Ǵ�һ��Ļ���������wget����ģ�飬�����hadoop�����Ĳ�ͬ����������
         1)ƴ�ӵĴ��ǲ�ͬ��
         2)������hadoop�Ĳ�������
    """
    def __init__(self,log=None,host_info={"host":"127.0.0.1","user":"work","path":"./"},type="",retry=5):
        BaseDownload.__init__(self, log, host_info, retry)
        self.type = type
        self.path_str = None
        self.scmpf_host = None
        self.scmpf_user = None
        self.scmpf_passwd = None
        self.path_dict = {}
        self.element_dict = {}

    def check_scmpf_version(self, version):
        """
        @note: ���version�Ƿ�����λ�汾�Ż�����λ�汾��
        @return: �������λ�汾���򷵻�3�������λ�汾����4�����򷵻�����ֵ
        """
        version3 = re.compile(r"^\d+\.\d+\.\d+$")
        version4 = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
        if version3.search(version):
            return 3
        if version4.search(version):
            return 4
        return 1

    def set_path_element_dict(self,path_dict,element_dict):
        self.path_dict = path_dict
        self.element_dict = element_dict
        return 0

    def download_from_scmpf(self, version):
        """
        @note: ��scmpf��ȡģ���Ӧ������
        @version: scmpf�ϵİ汾�ţ���������λ�汾�ţ�����1.0.3.1; Ҳ��������λ�汾�ţ�����1.0.3
        """
        if self.element_dict.has_key("-X"):
            x_list = []
            for x_ele in self.element_dict["-X"].split(","):
                    x_list.append(x_ele)
            self.add_ignore_from_list(x_list,"-X")
        if self.element_dict.has_key("-R"):
            r_list = []
            for r_ele in self.element_dict["-R"].split(","):
                    r_list.append(r_ele)
            self.add_ignore_from_list(r_list,"-R")
        #�жϰ汾���Ƿ���Ϲ���
        version_num = self.check_scmpf_version(version)
        if 3 != version_num and 4 != version_num:
            self.log.critical("%s scmpf version[%s] format wrong! We need X.X.X or X.X.X.X!", self.type, version)
            raise XDNoModInfoError,"scmpf version format wrong"

        #self.get_scmpf_path_dict()


        #���汾���е�.�滻Ϊ-�������ϱ�Ҫ�ĺ�׺
        suffix3 = "BL"
        suffix4 = "PD_BL"
        inner_version = version.replace(".", "-")
        if 3 == version_num:
            inner_version += "_" + suffix3
        else:
            inner_version += "_" + suffix4

        abs_src_path = self.path_dict["dir"] + "_" + inner_version + \
                        "/" + self.remove_element_prefix(self.element_dict["src"])
        #ƴ��-R wgetѡ��
        Ropt_str = self.make_R_wget_options_str()
        #ƴ��-X wgetѡ��
        Xopt_str = self.make_X_wget_options_str(abs_src_path)
        wget_options = Xopt_str + " " + Ropt_str
        if self.element_dict.has_key("property") and self.element_dict["property"] == "file":
            ret = self.wget_data(host=self.path_dict["host"], user=self.path_dict["user"], \
                             passwd=self.path_dict["passwd"], src_path=abs_src_path, \
                             dest_path=self.element_dict["dst"],file_or_dir="file",wgetOptions=wget_options)
        else:
            ret = self.wget_data(host=self.path_dict["host"], user=self.path_dict["user"], \
                             passwd=self.path_dict["passwd"], src_path=abs_src_path, \
                             dest_path=self.element_dict["dst"],file_or_dir="dir",wgetOptions=wget_options)

        if 0 == ret:
            self.log.debug("%s get %s@%s:%s from scmpf success!", self.type, \
                            self.path_dict["user"], self.path_dict["host"], abs_src_path)
            return 0
        else:
            self.log.critical("%s get %s@%s:%s from scmpf fail!", self.type, \
                            self.path_dict["user"], self.path_dict["host"], abs_src_path)
            return 1

    def smart_download(self):
        """
        @note:Ŀǰ�Ƚϼ򵥣�������Ƿ���
        """
        download_time = Timer2()
        download_time.start()
        self.log.info("begin download %s module used scmpf way" %(self.type))
        if self.element_dict.has_key("args") and self.element_dict["args"] <> None:
            ret = self.download_from_scmpf(self.element_dict["args"])
        else:
            raise XDNoModInfoError,"please check element_dict,args cannot be None"
        download_time.end()
        self.log.info("%s download from scmpf used %s s" %(self.type,str(download_time.get_sec())))
        return ret

class HudsonDownload(BaseDownload):
    """
    @note:֧������hudson archive�ļ�����Ҫ����hudson·��ƴ�ӹ淶
         1)host:
         2)dir: ָ��job name�㼶���磺hudson/view/Trunk/job/as-quick
         3)jobnum: ��ʾ�����
         4)element src:
    """
    def __init__(self,log=None,host_info={"host":"127.0.0.1","user":"work","path":""},type="",retry=5):
        BaseDownload.__init__(self, log, host_info, retry)
        self.type = type
        self.path_dict = {}
        self.element_dict = {}

    def set_path_element_dict(self,path_dict,element_dict):
        self.path_dict = path_dict
        self.element_dict = element_dict
        return 0

    def combin_wget_options(self):
        """
        @note:ƴ��wget�Ĵ�
        """
        #ƴ��-R wgetѡ��
        Ropt_str = self.make_R_wget_options_str()
        #ƴ��-X wgetѡ��
        build_arg = self.expand_env_variable(self.element_dict["args"])
        if build_arg.isdigit():
            src_path = self.path_dict["dir"] + "/builds/" + build_arg+\
                            "/" + self.remove_element_prefix(self.element_dict["src"])
        else:
            src_path = self.path_dict["dir"] + "/" + build_arg\
                            + "/" + self.remove_element_prefix(self.element_dict["src"])
        Xopt_str = self.make_X_wget_options_str(src_path)

        wget_options = Xopt_str + " " + Ropt_str
        return src_path,wget_options

    def download_from_hudson(self):
        """
        @note:�����ļ���hudson
        """
        #ƴ�ӳ�һ��wget����
        if self.element_dict.has_key("-X"):
            x_list = []
            for x_ele in self.element_dict["-X"].split(","):
                    x_list.append(x_ele)
            self.add_ignore_from_list(x_list,"-X")
        if self.element_dict.has_key("-R"):
            r_list = []
            for r_ele in self.element_dict["-R"].split(","):
                    r_list.append(r_ele)
            self.add_ignore_from_list(r_list,"-R")
        wget_options = self.combin_wget_options()
        #�������أ���¼dg��־
        self.log.debug("Begin Module %s get env from hudson...", self.type)
        if self.element_dict.has_key("property") and self.element_dict["property"] == "file":
            ret = self.wget_data(self.path_dict["host"], self.path_dict["user"], self.path_dict["passwd"], \
                        wget_options[0], "file", self.element_dict["dst"], wget_options[1])
        else:
            ret = self.wget_data(self.path_dict["host"], self.path_dict["user"], self.path_dict["passwd"], \
                        wget_options[0], "dir", self.element_dict["dst"], wget_options[1])
        self.log.debug("Finish Module %s get env from hudson...", self.type)
        return ret

    def smart_download(self):
        """
        @note:Ŀǰ�Ƚϼ򵥣�������Ƿ���
        """
        download_time = Timer2()
        download_time.start()
        self.log.info("begin download %s module used hudson way" %(self.type))
        ret = self.download_from_hudson()
        download_time.end()
        self.log.info("%s download from %s used %s s" %(self.type,self.path_dict["host"],str(download_time.get_sec())))
        return ret

class LocalDownload(BaseDownload):
    """
    @note:֧�ֱ�������
    """
    def __init__(self,log=None,host_info={"host":"127.0.0.1","user":"work","path":"./"},type="",retry=5):
        BaseDownload.__init__(self, log, host_info, retry)
        self.type = type
        self.path_dict = {}
        self.element_dict = {}

    def set_path_element_dict(self,path_dict,element_dict):
        self.path_dict = path_dict
        self.element_dict = element_dict
        return 0

    def convert_dst_path(self):
        #���dst�ĺ�׺��src�ĺ�׺��ͬ����ɾ����׺������
        if os.path.basename(self.element_dict["dst"]) == os.path.basename(self.element_dict["src"]):
            self.element_dict["dst"] = os.path.dirname(self.element_dict["dst"])

    def smart_download(self):
        download_time = Timer2()
        download_time.start()
        self.log.info("begin download %s module used local way" %(self.type))
        if self.path_dict["dir"] <> None and self.element_dict["dst"] <> None:
            if self.element_dict.has_key("yaml_type") and self.element_dict["yaml_type"]==1:
                self.convert_dst_path()
            dst = "%s/%s" % (self.host_info["path"], self.remove_element_prefix(self.element_dict["dst"]))
            if not os.path.isdir(dst):
                self.sys.xd_system("mkdir -p %s" % dst)

            src = self.path_dict["dir"]
            if self.element_dict.has_key("src") and self.element_dict["src"] <> None:
                src = "%s/%s" % (src, self.element_dict["src"])

            cmd = "cp -rf %s %s" % (src,dst)
            self.log.info(cmd)
            self.sys.xd_system(cmd)
        else:
            raise XDNoModInfoError,"please check path_dict and element_dict"
        self.log.info("%s download from local used %s s" %(self.type,str(download_time.get_sec())))
        return 0

class SvnDownload(BaseDownload):
    """
    @note:֧��svn ����,��������svn_cmd,��ѡ������svn co ���� svn export
    """
    def __init__(self,log=None,host_info={"host":"127.0.0.1","user":"work","path":"./"},type="",retry=5):
        BaseDownload.__init__(self, log, host_info, retry)
        self.type = type
        self.path_dict = {}
        self.element_dict = {}

    def set_path_element_dict(self,path_dict,element_dict):
        self.path_dict = path_dict
        self.element_dict = element_dict
        return 0

    def smart_download(self):
        download_time = Timer2()
        download_time.start()
        self.log.info("begin download %s module used svn way" %(self.type))
        if self.path_dict["dir"] <> None and self.element_dict["dst"] <> None:
            dst = "%s/%s" % (self.host_info["path"], self.remove_element_prefix(self.element_dict["dst"]))
            if not os.path.isdir(dst):
                self.sys.xd_system("mkdir -p %s" % dst)

            src = self.path_dict["dir"]
            if self.element_dict.has_key("src") and self.element_dict["src"] <> None:
                src = "%s/%s" % (src, self.element_dict["src"])
            if self.path_dict.has_key("user") and self.path_dict.has_key("password"):
                cmd = "svn %s --password=%s --username=%s %s %s" % (self.element_dict["svn_cmd"],\
                       self.path_dict["password"],self.path_dict["user"],src,dst)
            else:
                cmd = "svn %s %s %s" % (self.element_dict["svn_cmd"],src,dst)
            self.log.debug(cmd)
            self.sys.xd_system(cmd)
        else:
            raise XDNoModInfoError,"please check path_dict and element_dict"
        self.log.info("%s download from svn used %s s" %(self.type,str(download_time.get_sec())))
        return 0

class DataCenterDownload(BaseDownload):
    """
    @note:����data.des�ļ���Ȼ��������ض���
         ��Ҫʹ�����Լ��һ���ӿڣ�����ӿ����һЩ���ݵĹ���
         1)data.des�ļ�������
         2)����������ĵĴ洢�ص����Ż�
    """
    def __init__(self,log=None,host_info={"host":"127.0.0.1","user":"work","path":"./"},type="",retry=0):
        BaseDownload.__init__(self, log, host_info, retry)
        self.type = type
        self.data_des_dict = {}
        self.path_dict = {}
        self.element_dict = {}

    def set_path_element_dict(self,path_dict,element_dict):
        self.path_dict = path_dict
        self.element_dict = element_dict
        return 0

    def prase_data_des_file(self,file):
        """
        @note:����data.des�ļ�
        """
        fd = open(file,"r")
        dst_list = []
        src_list = []
        for line in fd.readlines():
            if line.endswith("= {\n"):
                dst_list.append(line[:-5])
            if line.startswith("key = "):
                src_list.append(line[6:-1])
        for i in range(0,len(dst_list)):
            self.data_des_dict[dst_list[i]]=src_list[i]
        fd.close()
        return 0

    def prase_yaml_file(self,des_file,des_file_base=None):
        """
        @note:����data.des�ļ�
        Modified by hushiling01, Feb 21,2013
        ʵ����������
        """
        fd = open(des_file,"r")
        dst_list = []
        src_list = []
        for line in fd.readlines():
            if line.endswith(":\n"):
                dst_list.append(line[:-2])
            if line.startswith("  src: "):
                src_list.append(line[7:-1])

        base_dst_list = []
        base_src_list = []
        if des_file_base != None:
            base_file = open(des_file_base,"r")
            for line in base_file.readlines():
                if line.endswith(":\n"):
                    base_dst_list.append(line[:-2])
                if line.startswith("  src: "):
                    base_src_list.append(line[7:-1])

        for i in range(0,len(dst_list)):
            if base_dst_list != [] and dst_list[i] in base_dst_list:
                _idx = base_dst_list.index(dst_list[i])
                if src_list[i] == base_src_list[_idx]:
                    continue
            self.data_des_dict[dst_list[i]]=src_list[i]
        fd.close()
        #print "==== self.data_des_dict",self.data_des_dict

        return 0

    def judge_des_file(self,file):
        """
        @note: ��ʱ���ڼ������ϸ�ʽ���������ں�ɾ��
        @return: 2 yaml ��ʽ
                 1 datades ��ʽ
                 0 ��ʽ����
        """
        fd = open(file,"r")
        line = fd.readline()
        if line.endswith(":\n"):
            return 2
        elif line.endswith("= {\n"):
            return 1
        else:
            return 0

    def combin_wget_options(self,src):
        """
        @note:ƴ��wget�Ĵ�,������һ��ƴ�ӣ�data.des��ƴ��n��
        """
        #ƴ��-R wgetѡ��
        Ropt_str = self.make_R_wget_options_str()
        #ƴ��-X wgetѡ��
        #�滻yf-cm-staticdata00.yf01����ʵ���ǽ�ȥһ��
        hostname="yf-cm-staticdata00.yf01"
        index = src.find(hostname)
        index += len(hostname)
        src_path = src[index:]
        Xopt_str = self.make_X_wget_options_str(src_path)
        wget_options = Xopt_str + " " + Ropt_str
        return src_path,wget_options

    def download_from_data_des(self,des_file,des_file_base=None):
        """
        @note:���ػ�׼��������������Ǹ���ģ���Լ�ά���Ŀɲ⻷��
        @param des_file: data.des�ļ�·��,Ҫ����ɾ���·�����룬�������
        Modified by hushiling01, Feb 21,2013
        DataCenter����������������֧����������,�ṩһ���µ�DataCenter����������,�ṩ�¾�����data.des��ֻ���������б仯�Ĳ���
        ע�⣬��׼�ļ����µ��ļ�������ȫ������
        @param des_file_base: data.des�Ļ�׼�ļ�·��
        """
        #��ȡpath_dict,��������¼������ģ���Դ��Ϣ
        ret = 0
        #self.prase_data_des_file(des_file)
        if self.judge_des_file(des_file) == 1:
            self.prase_data_des_file(des_file)
        elif self.judge_des_file(des_file) == 2:
            self.prase_yaml_file(des_file,des_file_base)
        else:
            self.log.warning("you input wrong file to prase,please check des file")
            return 0
        if self.element_dict.has_key("limit_rate"):
            self.set_limit_rate(self.element_dict["limit_rate"])
        self.log.debug("Begin Module %s get std env from data center...", self.type)
        for k in self.data_des_dict.keys():
            #bin.des ֧�ִӲ�Ʒ������
            if self.data_des_dict[k].startswith("getprod"):
                _dst = os.path.dirname(k)
                _bin = os.path.basename(k)
                _dst_path = os.path.join(self.host_info["path"],_dst)
                cmd = "wget -nv -nH --level=0 --tries=20 --limit-rate=10m --cut-dirs=7 -P %s ftp://:%s"%(_dst_path,self.data_des_dict[k])
                self.sys.xd_system(cmd)
                self.sys.xd_system("cd %s;chmod +x %s"%(self.host_info["path"],k))
            #data.des(data.des.base)֧�ִ�������������
            elif self.data_des_dict[k].startswith("ftp"):
                wget_options = self.combin_wget_options(self.data_des_dict[k])
                #�������أ���¼dg��־,����ط��滻�ӿ�Ϊ���ǵ����
                #host : 
                #dst  : k
                #src  : wget_options[0]
                #tmp_option=wget_options[0].replace("var","var_bak")
                var_index = wget_options[0].index("var")
                tmp_option=("/app/ecom/nova/mfs/"+wget_options[0].replace("var","var_bak")[var_index:])
                dir_or_not = [""]
                #�ж��Ƿ���Ŀ¼�������Ŀ¼���ط�ʽ���ļ��Ĳ�ͬ������ط�������
                if dir_or_not[0] == "d":
                    ret |= self.wget_data(self.path_dict["host"], "", "", tmp_option, "dir", k, wget_options[1])
                else:
                    ret |= self.wget_data(self.path_dict["host"], "", "", \
                                          tmp_option, "file", "/data", wget_options[1])
                    if os.path.isdir(k[:k.rfind("/")]) == False:
                            self.sys.xd_system("cd %s;mkdir -p %s"%(self.host_info["path"],k[:k.rfind("/")]))
                    self.sys.xd_system("cd %s;mv data/%s %s"%(self.host_info["path"],\
                                          tmp_option[tmp_option.rfind("/"):],k))
        self.log.debug("Finish Module %s get std env from data center...", self.type)
        return ret

    def smart_download(self):
        """
        @note:Ŀǰ�Ƚϼ򵥣�������Ƿ���
        @param file:��Ҫ�������ļ�
        """
        download_time = Timer2()
        download_time.start()
        self.log.info("begin download %s module used op-center way" %(self.type))
        des_file_base = None
        if self.element_dict.has_key("des_file_base"):
            des_file_base = self.element_dict["des_file_base"]
        ret = self.download_from_data_des(self.element_dict["des_file"],des_file_base)
        download_time.end()
        self.log.info("download from op-center used %s s" %(str(download_time.get_sec())))
        return ret

class HDFSDownload(BaseDownload):
    """
    @note: download from hdfs
    """
    def __init__(self,log=None,host_info={"host":"127.0.0.1","user":"work","path":""},\
                 type="",retry=5,hdfs_path="", \
                 hadoop_client=""):
        BaseDownload.__init__(self, log, host_info, retry)
        self.type = type
        self.path_dict = {}
        self.element_dict = {}
        self.hdfs_path = hdfs_path
        self.hadoop_client = hadoop_client

    def set_path_element_dict(self,path_dict,element_dict):
        self.path_dict = path_dict
        self.element_dict = element_dict
        return 0

    def smart_download(self):
        download_time = Timer2()
        download_time.start()
        self.log.info("begin download %s module used hdc way" %(self.type))
        if self.path_dict["dir"] <> None and self.element_dict["dst"] <> None:
            dst = "%s/%s" % (self.host_info["path"], self.remove_element_prefix(self.element_dict["dst"]))
            if not os.path.isdir(dst):
                self.sys.xd_system("mkdir -p %s" % dst)
            src = self.path_dict["dir"].lstrip('/')
            if self.element_dict.has_key("src") and self.element_dict["src"] <> None:
                src = "%s/%s" % (src, self.element_dict["src"])
            self.sys.xd_system("rm -rf hdc")
            wget_cmd = "wget ftp:// 2>/dev/null"
            self.sys.xd_system(wget_cmd)
            cmd = "chmod 755 hdc && ./hdc -get "+self.hadoop_client.rstrip('/')+"/%s %s" % (src,dst)
            self.sys.xd_system(cmd)
        else:
            raise XDNoModInfoError,"please check path_dict and element_dict"
        download_time.end()
        self.log.info("%s download from hdc used %s s" %(self.type,str(download_time.get_sec())))
        return 0

from frame.lib.commonlib.dlog import dlog



if __name__ == '__main__':
    pass
