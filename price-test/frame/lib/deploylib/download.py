# -*- coding: GB18030 -*-
"""
@author: guoan
@modified by: maqi
@date: July 28, 2011
@summary: download的基类
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
    @note: 所有模块download调用这个模块
    """
    def __init__(self, log=None, host_info={"host":"127.0.0.1","user":"work","path":"./"}, retry=5):
        """
        @note: 基本的下载类，目标是把wget包装起来,这次的重写
               1)注意返回值设置
               2)把单测写起来，从这个重构开始，也花不了太多时间~~~~
        """
        self.basic_wget_options = "-r -nv -nH --level=0 --tries=20"
        self.limit_rate = "40m"
        self.retry_num = retry
        self.ignore_file_list=[]
        self.ignore_dir_list=[]

        self.log = log
        self.host_info = host_info
        self.sys = XDSystem(self.log)
        #用户自定义的wget参数，暂不进行正确性检查
        self.custom_wget_args = ""

    def set_limit_rate(self, limit_rate):
        """
        @note: 设置wget limit-rate选项
        @param limit_rate:下载上限速率
        @return: 设置的速率
        """
        self.limit_rate = str(limit_rate)
        return self.limit_rate

    def set_custom_wget_args(self, wget_args):
        """
        @note: 设置自定义的wget参数，每次设置都会覆盖以前的设置
        @param wget_args: 参数内容，非空时直接强转为str拼接到wget命令中
        @return: 设置后，目前生效的参数
        """
        if wget_args:
            self.custom_wget_args = str(wget_args)
        return self.custom_wget_args

    def compute_cut_dir(self, src_path):
        """
        @note: wget时应该砍掉的dir数，比如abc/efg//应该砍掉3层
        @param src_path:需要裁减的目录
        """
        tmp_path = src_path.strip('/')
        cut_dir = len(tmp_path.split('/')) - 1
        if cut_dir < 0:
            self.log.warning("wget cut_dir <0 %s, force to zero", tmp_path)
            cut_dir = 0
        return cut_dir

    def add_basic_wgetOptions(self, src_path, wgetOptions):
        """
        @note: 将wget的基本选项拼接起来
        @param src_path:需要裁减的目录
        @param wgetOptions:wget的参数
        """
        cut_dir_num = self.compute_cut_dir(src_path)
        wgetOptions = self.basic_wget_options + " --limit-rate=" + self.limit_rate + " --cut-dirs=" + str(cut_dir_num) + " " + wgetOptions
        #添加自定义的wget参数
        if self.custom_wget_args:
            wgetOptions = "%s %s" %(wgetOptions, self.custom_wget_args)
        return wgetOptions

    def wget_data(self, host, user="anonymous", passwd="anonymous", src_path=".", file_or_dir="file", dest_path=".", wgetOptions="", dest_is_file=False):
        """
        @note:使用wget下载数据的基本方法
        @param host: 下载源地址
        @param user: 用户名
        @param passwd: 密码
        @param src_path: 下载源目录
        @param file_or_dir: 具体是下载文件还是目录
        @param dest_path: 绝对目的地址，element需要有绝对地址提供给download lib
        @param wgetOptions: wget的选项
        @param dest_is_file: 目的地址是否为文件，若为True，使用-O，若为False，使用-P
        """
        #拼接ftp地址
        src_path = os.path.normpath(src_path.strip('/'))

        if user == "" and passwd == "" :
            ftp_address = "ftp://%s/%s" % (host, src_path)
        else :
            ftp_address = "ftp://%s:%s@%s/%s" % (user, passwd, host, src_path)
        if file_or_dir == "dir":
            ftp_address = ftp_address + "/*"
            src_path = src_path + "/*"
        #拼接wget选项
        wgetOptions = self.add_basic_wgetOptions(src_path, wgetOptions)
        #whole_dest_path = self.host_info["path"] + "/" + dest_path
        whole_dest_path = self.host_info["path"] + "/" + dest_path
        #若标记目标地址为文件，则使用-O，否则使用-P
        if dest_is_file:
            wgetOptions += " -O " + whole_dest_path
        else:
            wgetOptions += " -P " + whole_dest_path

        #拼接整体命令串
        whole_wget_cmd = "wget %s %s" % (wgetOptions, ftp_address)
        self.log.debug("wget cmd:%s", whole_wget_cmd)

        #执行命令
        #retry self.retry_num 次
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
        @note: 返回时间字符串类似20110330, day_num表示相对当前日期的时间跨度
                   例如想得到昨天的日期字符串day_num=-1，得到明天的day_num =1
        """
        std_day = datetime.now()
        ret_day = std_day + timedelta(days = day_num)
        return ret_day.strftime("%Y%m%d")


    def add_ignore(self, path, flag="-X"):
        """
        @note: download过程中不下载哪些东西，flag = -X or -R, -X表示ignore目录，-R表示ignore文件名或文件名通配符
               path必须是相对于模块内部的相对路径，例如bdbs/data/bdindex/，就写成data/bdindex/即可
        """
        if flag == "-R":
            self.ignore_file_list.append(path)

        if flag == "-X":
            self.ignore_dir_list.append(path)
        return 0

    def add_ignore_from_list(self, path_list, flag="-X"):
        """
        @note: 从一个list中加入ignore
               flag同add_ignore
               path_list是需要忽略的文件或目录list
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
        @note: 根据self.ignore_dir_list生成wget的-X选项
               ignore_list里存放的都是模块内部的相对路径，需要拼接上src_path形成绝对路径
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
        @note: 根据self.ignore_file_list生成wget的-R选项
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
        @note: 删除element的前缀，例如"./src" 经过处理变成 "src"
        @param src: 输入需要处理前缀的字符串
        @return: 去除./或者/前缀的字符串
        """
        if src.startswith("./"):
            return src[2:]
        elif src.startswith("/"):
            return src[1:]
        else:
            return src

    def expand_env_variable(self, variable):
        """
        @note: 展开环境变量，如果环境变量不存在或者非$开头，则返回原串
        @param variable: 环境变量名
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
    @hadoop相关的download
    """
    def __init__(self,log=None,host_info={"host":"127.0.0.1","user":"work","path":"./"},\
                    type="",retry=5):
        BaseDownload.__init__(self, log, host_info, retry)
        self.type = type
        self.path_dict = {}
        self.element_dict = {}

    def get_hadoop_module_host_dir(self, host, user, passwd, date_str):
        """
              而另外一些则还没变，因此我们实现该函数来进行自适应，根据时间自动获取路径名，以适应所有情况
              该函数返回对应的机器路径名，如上面例子中的db-cm-fcbs01.db01
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
        @note:通过每个模块特有的配置文件信息，读取下载源的信息
              该方法目前在element.py里面调用，目的是给每个element传入不同的下载信息
        @param path_dict: 传入下载源信息
        @param element_dict: 传入element信息
        """
        self.path_dict = path_dict
        self.element_dict = element_dict
        return 0


    def combin_wget_options(self,day_num=-1):
        """
        @note:拼接一条完整的wget命令
              注意hadoop的拼接可能有点特别，需要读到：备份的机器名
              返回的是一个元组(wgetOptins,src_path)
        @param day_num: -1代表昨天
        """
        #获取日期字符串
        date_str = self.get_date_str(day_num)
        #获取线上主机地址目录
        online_host_str = self.get_hadoop_module_host_dir(self.path_dict["host"], self.path_dict["user"], self.path_dict["passwd"], date_str)
        if online_host_str == None:
            raise XDHadoopError,"host dir from hadoop is None"

        #拼接srcpath字符串
        src_path = date_str + "/" + online_host_str + "/" + self.path_dict["dir"] \
                        + "/" + self.remove_element_prefix(self.element_dict["src"])

        #拼接-X wget选项
        Xopt_str = self.make_X_wget_options_str(src_path)
        #拼接-R wget选项
        Ropt_str = self.make_R_wget_options_str()
        wget_options = Xopt_str + " " + Ropt_str
        return src_path,wget_options


    def download_from_hadoop(self,day_num=-1):
        """
        @note:下载基准环境，一般是线上同步环境
        """
        #获取path_dict,这个里面记录着下载模块的源信息,这个部分提取到element.py里面去做了
        #self.get_online_path_dict()
        #self.get_npatfile_path_dict()
        #拼接出一条wget命令
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
        #进行下载，记录dg日志
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
        @note:目前比较简单，今后考虑是否补足
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
        @note:标准的下载类，指的是从一般的机器上面用wget下载模块，这个和hadoop的最大的不同有以下两点
         1)拼接的串是不同的
         2)不会有hadoop的补备功能
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
        @note:拼接wget的串
        """
        #拼接-R wget选项
        Ropt_str = self.make_R_wget_options_str()
        #拼接-X wget选项
        src_path = self.path_dict["dir"] + "/" +self.remove_element_prefix(self.element_dict["src"])
        Xopt_str = self.make_X_wget_options_str(src_path)

        wget_options = Xopt_str + " " + Ropt_str
        return src_path,wget_options

    def download_from_std(self):
        """
        @note:下载基准环境，这个环境是各个模块自己维护的可测环境
        """
        #获取path_dict,这个里面记录着下载模块的源信息
        #self.get_online_path_dict()
        #拼接出一条wget命令
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
        #进行下载，记录dg日志
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
        @note:目前比较简单，今后考虑是否补足
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
    @note:标准的下载类，指的是从一般的机器上面用wget下载模块，这个和hadoop的最大的不同有以下两点
         1)拼接的串是不同的
         2)不会有hadoop的补备功能
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
        @note: 检查version是否是三位版本号或者四位版本号
        @return: 如果是三位版本，则返回3，如果四位版本返回4，否则返回其他值
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
        @note: 从scmpf获取模块对应的数据
        @version: scmpf上的版本号，可以是四位版本号，例如1.0.3.1; 也可以是三位版本号，例如1.0.3
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
        #判断版本号是否符合规则
        version_num = self.check_scmpf_version(version)
        if 3 != version_num and 4 != version_num:
            self.log.critical("%s scmpf version[%s] format wrong! We need X.X.X or X.X.X.X!", self.type, version)
            raise XDNoModInfoError,"scmpf version format wrong"

        #self.get_scmpf_path_dict()


        #将版本号中的.替换为-，并加上必要的后缀
        suffix3 = "BL"
        suffix4 = "PD_BL"
        inner_version = version.replace(".", "-")
        if 3 == version_num:
            inner_version += "_" + suffix3
        else:
            inner_version += "_" + suffix4

        abs_src_path = self.path_dict["dir"] + "_" + inner_version + \
                        "/" + self.remove_element_prefix(self.element_dict["src"])
        #拼接-R wget选项
        Ropt_str = self.make_R_wget_options_str()
        #拼接-X wget选项
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
        @note:目前比较简单，今后考虑是否补足
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
    @note:支持下载hudson archive文件，需要符合hudson路径拼接规范
         1)host:
         2)dir: 指向job name层级，如：hudson/view/Trunk/job/as-quick
         3)jobnum: 表示任务号
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
        @note:拼接wget的串
        """
        #拼接-R wget选项
        Ropt_str = self.make_R_wget_options_str()
        #拼接-X wget选项
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
        @note:下载文件从hudson
        """
        #拼接出一条wget命令
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
        #进行下载，记录dg日志
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
        @note:目前比较简单，今后考虑是否补足
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
    @note:支持本机拷贝
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
        #如果dst的后缀与src的后缀相同，则删掉后缀的名字
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
    @note:支持svn 下载,可以配置svn_cmd,来选择是用svn co 还是 svn export
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
    @note:解析data.des文件，然后完成下载动作
         需要使用者自己搭建一个接口，这个接口完成一些备份的工作
         1)data.des文件解析器
         2)针对数据中心的存储特点做优化
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
        @note:解析data.des文件
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
        @note:解析data.des文件
        Modified by hushiling01, Feb 21,2013
        实现增量下载
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
        @note: 暂时用于兼容新老格式，两个星期后删除
        @return: 2 yaml 格式
                 1 datades 格式
                 0 格式错误
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
        @note:拼接wget的串,单独的一条拼接，data.des会拼接n条
        """
        #拼接-R wget选项
        Ropt_str = self.make_R_wget_options_str()
        #拼接-X wget选项
        #替换yf-cm-staticdata00.yf01，其实就是截去一节
        hostname="yf-cm-staticdata00.yf01"
        index = src.find(hostname)
        index += len(hostname)
        src_path = src[index:]
        Xopt_str = self.make_X_wget_options_str(src_path)
        wget_options = Xopt_str + " " + Ropt_str
        return src_path,wget_options

    def download_from_data_des(self,des_file,des_file_base=None):
        """
        @note:下载基准环境，这个环境是各个模块自己维护的可测环境
        @param des_file: data.des文件路径,要求处理成绝对路径传入，以免混乱
        Modified by hushiling01, Feb 21,2013
        DataCenter下载适配器升级，支持增量下载,提供一个新的DataCenter下载适配器,提供新旧两份data.des，只下载其中有变化的部分
        注意，基准文件和新的文件，都是全量描述
        @param des_file_base: data.des的基准文件路径
        """
        #获取path_dict,这个里面记录着下载模块的源信息
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
            #bin.des 支持从产品库下载
            if self.data_des_dict[k].startswith("getprod"):
                _dst = os.path.dirname(k)
                _bin = os.path.basename(k)
                _dst_path = os.path.join(self.host_info["path"],_dst)
                cmd = "wget -nv -nH --level=0 --tries=20 --limit-rate=10m --cut-dirs=7 -P %s ftp://:%s"%(_dst_path,self.data_des_dict[k])
                self.sys.xd_system(cmd)
                self.sys.xd_system("cd %s;chmod +x %s"%(self.host_info["path"],k))
            #data.des(data.des.base)支持从数据中心下载
            elif self.data_des_dict[k].startswith("ftp"):
                wget_options = self.combin_wget_options(self.data_des_dict[k])
                #进行下载，记录dg日志,这个地方替换接口为我们的入口
                #host : 
                #dst  : k
                #src  : wget_options[0]
                #tmp_option=wget_options[0].replace("var","var_bak")
                var_index = wget_options[0].index("var")
                tmp_option=("/app/ecom/nova/mfs/"+wget_options[0].replace("var","var_bak")[var_index:])
                dir_or_not = [""]
                #判段是否是目录，如果是目录下载方式和文件的不同，这个地方做处理
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
        @note:目前比较简单，今后考虑是否补足
        @param file:需要解析的文件
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
